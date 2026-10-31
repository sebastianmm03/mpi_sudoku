import argparse
import sys
import time
from pathlib import Path

from mpi4py import MPI

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))  # importar archivos

from baseline_secuencial import leer_seeds
from sudoku import resolver_con_tiempo

comm = MPI.COMM_WORLD
rank = comm.Get_rank()  # número de proceso
size = comm.Get_size()  # procesos

# Todos los procesos leen los argumentos y los tableros: no comparten memoria,
# así que cada uno necesita su propia copia de la lista.
parser = argparse.ArgumentParser(description="Sudoku con MPI: reparto de tableros.")
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
    tableros = list(seeds.items())  # lista de (id, tablero)


def trabajador():
    # Primer mensaje: "estoy libre, dame trabajo". None = no traigo resultado
    comm.send(None, dest=0)
    while True:
        indice = comm.recv(source=0)  # el coordinador me dice qué tablero resolver
        if indice is None:  # None desde el coordinador = no quedan tableros
            break
        tablero = tableros[indice][1]
        # resolver() modifica el tablero que recibe, así que trabajo con una copia
        copia = [fila[:] for fila in tablero]
        resuelto, segundos = resolver_con_tiempo(copia)
        # Entrego el resultado, esto también le avisa al coordinador que estoy libre
        comm.send((indice, resuelto, segundos), dest=0)


def coordinador():
    pendientes = list(range(len(tableros)))  # índices de tableros sin repartir
    activos = size - 1  # trabajadores que todavía no han recibido el "fin"
    procesados = 0
    resueltos = 0
    etiqueta = "Tiempo" if args.id else "Tiempo parcial"

    inicio = time.perf_counter()  # empieza el tiempo total (reloj real)
    while activos > 0:
        estado = MPI.Status()
        # Atiendo al primero que escriba, sin importar su rank
        mensaje = comm.recv(source=MPI.ANY_SOURCE, status=estado)
        quien = estado.Get_source()

        if mensaje is not None:  # no es "estoy libre" inicial: trae un resultado
            indice, resuelto, segundos = mensaje
            procesados += 1
            if resuelto:
                resueltos += 1
            print(f"\nID: {tableros[indice][0]}  (proceso {quien})")
            print("Resuelto" if resuelto else "Sin solución")
            print(f"{etiqueta}: {segundos:.6f} segundos", flush=True)

        if pendientes:
            comm.send(pendientes.pop(0), dest=quien)  # el siguiente tablero
        else:
            comm.send(None, dest=quien)  # no hay más: señal de fin
            activos -= 1
    total = time.perf_counter() - inicio  # llegan todos los resultados

    print(f"\nTableros procesados: {procesados}/{len(tableros)} (resueltos: {resueltos})")
    print(f"Tiempo total (reloj real): {total:.6f} segundos")


if size < 2:
    print("Se necesitan al menos 2 procesos: uno coordina y otros resuelven.")
elif rank == 0:
    coordinador()
else:
    trabajador()
