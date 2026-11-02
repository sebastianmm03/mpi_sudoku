import argparse
import sys
import time
from pathlib import Path

from mpi4py import MPI

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))  # importar los archivos de carpeta de arriba

from baseline_secuencial import leer_seeds
from sudoku import puede_colocar

comm = MPI.COMM_WORLD
rank = comm.Get_rank()  # número entre todos los procesos
size = comm.Get_size()  # cuántos procesos en total

REVISAR_CADA = 5000  # cada cuántos pasos del backtracking reviso si llegó un mensaje

parser = argparse.ArgumentParser(description="Sudoku con MPI: tableros y ramas (híbrido).")
parser.add_argument("--grupo", type=int, default=2, help="procesos por grupo (por defecto: 2)")
seleccion = parser.add_mutually_exclusive_group()
seleccion.add_argument("--id", dest="id", help="resolver solo el tablero con este ID")
seleccion.add_argument("--all", action="store_true", help="resolver todos los tableros")
args = parser.parse_args()

seeds = leer_seeds(RAIZ / "seeds.txt")
if args.id:
    if args.id not in seeds:
        if rank == 0:
            print(f"ID '{args.id}' no existe. Disponibles: {', '.join(seeds)}")
        sys.exit(0)
    tableros = [(args.id, seeds[args.id])]
else:
    tableros = list(seeds.items())  # lista(id, tablero)

# Armar grupos, los procesos con el mismo color quedan en el mismo grupo
# Con 4 procesos y grupos de 2, los procesos 0 y 1 son el grupo 0, y los 2 y 3 el grupo 1
tam_grupo = max(1, min(args.grupo, size))
color = rank // tam_grupo  # número de mi grupo
num_grupos = (size + tam_grupo - 1) // tam_grupo
gcomm = comm.Split(color, rank)  # comunicador solo con los miembros de mi grupo
grank = gcomm.Get_rank()  # mi número dentro del grupo
gsize = gcomm.Get_size()  # cuántos somos en mi grupo


class Detener(Exception):
    """Sirve para salir del backtracking cuando otro proceso del grupo ya resolvió el tablero."""


otro_encontro = False  # True cuando me avisaron que otro de mi grupo resolvió este tablero
pasos = 0  # cuántas casillas he rellenado en la rama actual


def alguien_encontro(etiqueta):
    """Revisa si otro proceso de mi grupo ya encontró la solución, sin quedarse esperando."""
    global otro_encontro
    # Iprobe solo pregunta si hay un mensaje, recv se quedaría esperando
    if not otro_encontro and gcomm.Iprobe(source=MPI.ANY_SOURCE, tag=etiqueta):
        gcomm.recv(source=MPI.ANY_SOURCE, tag=etiqueta)  # lee el aviso
        otro_encontro = True
    return otro_encontro


def primera_vacia(tablero):
    """Busca la primera casilla vacía y devuelve (fila, columna), o None si no hay."""
    for fila in range(9):
        for columna in range(9):
            if tablero[fila][columna] == 0:
                return fila, columna
    return None


def generar_ramas(tablero, minimo):
    """Crea las ramas del tablero rellenando las primeras casillas vacías."""
    # Cada rama es el tablero con una combinación distinta de valores válidos
    # Se pide un mínimo de ramas, más que procesos del grupo para repartir parejo
    ramas = [tablero]
    while len(ramas) < minimo:
        nuevas = []
        for rama in ramas:
            celda = primera_vacia(rama)
            if celda is None:  # esta rama ya no tiene casillas vacías
                nuevas.append(rama)
                continue
            fila, columna = celda
            for valor in range(1, 10):
                if puede_colocar(rama, fila, columna, valor):
                    hija = [f[:] for f in rama]  # copia para no dañar la rama original
                    hija[fila][columna] = valor
                    nuevas.append(hija)
        if nuevas == ramas:  # no se pudo expandir más
            break
        ramas = nuevas
    return ramas


def resolver_rama(tablero, etiqueta):
    """Backtracking normal, pero cada cierto número de pasos revisa si otro ya resolvió."""
    global pasos
    for fila in range(9):
        for columna in range(9):
            if tablero[fila][columna] != 0:
                continue
            for valor in range(1, 10):
                if puede_colocar(tablero, fila, columna, valor):
                    tablero[fila][columna] = valor
                    pasos += 1
                    if pasos % REVISAR_CADA == 0 and alguien_encontro(etiqueta):
                        raise Detener  # otro ya resolvió y dejó de buscar
                    if resolver_rama(tablero, etiqueta):
                        return True
                    tablero[fila][columna] = 0  # retroceso, probar otro valor
            return False
    return True  # no quedan casillas vacías


def resolver_tablero(indice, tablero):
    """Resuelve un tablero entre los procesos de mi grupo. Devuelve True si se resolvió."""
    global otro_encontro, pasos
    otro_encontro = False
    etiqueta = indice  # cada tablero usa su propia etiqueta para no mezclar avisos

    # Todos los procesos del grupo generan la misma lista de ramas
    ramas = generar_ramas(tablero, 4 * gsize)

    yo_encontre = False
    try:
        # Reparto dentro del grupo, el miembro r toma las ramas r, r+gsize, r+2*gsize, ...
        for i in range(grank, len(ramas), gsize):
            if alguien_encontro(etiqueta):
                break
            copia = [fila[:] for fila in ramas[i]]
            pasos = 0
            if resolver_rama(copia, etiqueta):
                yo_encontre = True
                for destino in range(gsize):  # aviso a los demás de mi grupo
                    if destino != grank:
                        gcomm.send(1, dest=destino, tag=etiqueta)
                break
    except Detener:
        pass

    # allgather espera a que todos los de mi grupo terminen y junta lo que cada uno encontró
    resultados = gcomm.allgather(yo_encontre)
    return any(resultados)


def main():
    """Cada grupo resuelve sus tableros; al final se junta el conteo y se mide el tiempo."""
    procesados = 0  # tableros que resolvió mi grupo, pero solo cuenta el líder
    resueltos = 0
    etiqueta_tiempo = "Tiempo" if args.id else "Tiempo parcial"

    comm.Barrier()  # todos empiezan juntos
    inicio = time.perf_counter()  # empieza el tiempo total (reloj real)

    # Reparto de tableros entre grupos, el grupo g toma los tableros g, g+num_grupos, ...
    for indice in range(color, len(tableros), num_grupos):
        nombre, tablero = tableros[indice]
        inicio_tablero = time.perf_counter()
        resuelto = resolver_tablero(indice, tablero)
        segundos = time.perf_counter() - inicio_tablero
        if grank == 0:  # solo el líder del grupo imprime y cuenta
            procesados += 1
            if resuelto:
                resueltos += 1
            print(f"\nID: {nombre}  (grupo {color})")
            print("Resuelto" if resuelto else "Sin solución")
            print(f"{etiqueta_tiempo}: {segundos:.6f} segundos", flush=True)

    comm.Barrier()  # espero a que todos los grupos terminen
    total = time.perf_counter() - inicio

    # Junto en el proceso 0 lo que contó cada líder de grupo
    total_procesados = comm.reduce(procesados, op=MPI.SUM, root=0)
    total_resueltos = comm.reduce(resueltos, op=MPI.SUM, root=0)
    if rank == 0:
        print(f"\nConfiguración: {size} procesos = {num_grupos} grupo(s) de {tam_grupo}")
        print(f"Tableros procesados: {total_procesados}/{len(tableros)} (resueltos: {total_resueltos})")
        print(f"Tiempo total (reloj real): {total:.6f} segundos")


main()
