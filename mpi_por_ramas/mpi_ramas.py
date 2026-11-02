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
rank = comm.Get_rank()  # número de proceso
size = comm.Get_size()  # cuántos procesos

REVISAR_CADA = 5000  # cada cuántos pasos del backtracking reviso si llegó un mensaje

parser = argparse.ArgumentParser(description="Sudoku con MPI: reparto de ramas.")
grupo = parser.add_mutually_exclusive_group()
grupo.add_argument("--id", dest="id", help="resolver solo el tablero con este ID")
grupo.add_argument("--all", action="store_true", help="resolver todos los tableros")
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


class Detener(Exception):
    """Sirve para salir del backtracking cuando otro proceso ya resolvió el tablero."""


otro_encontro = False  # True cuando me avisaron que otro proceso resolvió este tablero
pasos = 0  # cuántas casillas he rellenado en la rama actual


def alguien_encontro(etiqueta):
    """Revisa si otro proceso ya encontró la solución, sin quedarse esperando."""
    global otro_encontro
    # Iprobe solo pregunta si hay un mensaje, recv se quedaría esperando
    if not otro_encontro and comm.Iprobe(source=MPI.ANY_SOURCE, tag=etiqueta):
        comm.recv(source=MPI.ANY_SOURCE, tag=etiqueta)  # leo el aviso
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
    # Se pide un mínimo de ramas (más que procesos) para repartir el trabajo parejo
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
                        raise Detener  # otro resolvió y dejó de buscar
                    if resolver_rama(tablero, etiqueta):
                        return True
                    tablero[fila][columna] = 0  # retroceso, probar otro valor
            return False
    return True  # no hay má casillas vacías


def resolver_tablero(indice, tablero):
    """Resuelve un tablero entre todos los procesos. Devuelve True si se resolvió."""
    global otro_encontro, pasos
    otro_encontro = False
    etiqueta = indice  # cada tablero usa su propia etiqueta para no mezclar avisos

    # Todos los procesos generan la misma lista de ramas por eso el cálculo es igual en todos
    ramas = generar_ramas(tablero, 4 * size)

    yo_encontre = False
    try:
        # Reparto, el proceso r toma las ramas r, r+size, r+2*size, ...
        for i in range(rank, len(ramas), size):
            if alguien_encontro(etiqueta):
                break
            copia = [fila[:] for fila in ramas[i]]
            pasos = 0
            if resolver_rama(copia, etiqueta):
                yo_encontre = True
                for destino in range(size):  # aviso a todos los demás
                    if destino != rank:
                        comm.send(1, dest=destino, tag=etiqueta)
                break
    except Detener:
        pass

    # allgather espera a que todos terminen el tablero y junta lo que cada uno encontró
    resultados = comm.allgather(yo_encontre)
    return any(resultados)


def main():
    """Resuelve los tableros uno después de otro y mide los tiempos."""
    resueltos = 0
    etiqueta_tiempo = "Tiempo" if args.id else "Tiempo parcial"

    comm.Barrier()  # todos empiezan juntos
    inicio = time.perf_counter()  # empieza el tiempo total (reloj real)
    for indice, (nombre, tablero) in enumerate(tableros):
        inicio_tablero = time.perf_counter()
        resuelto = resolver_tablero(indice, tablero)
        segundos = time.perf_counter() - inicio_tablero
        if resuelto:
            resueltos += 1
        if rank == 0:
            print(f"\nID: {nombre}")
            print("Resuelto" if resuelto else "Sin solución")
            print(f"{etiqueta_tiempo}: {segundos:.6f} segundos", flush=True)
    total = time.perf_counter() - inicio  # terminó el último tablero

    if rank == 0:
        print(f"\nTableros procesados: {len(tableros)}/{len(tableros)} (resueltos: {resueltos})")
        print(f"Tiempo total (reloj real): {total:.6f} segundos")


main()
