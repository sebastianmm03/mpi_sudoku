# Tarea 1: repartir tableros

Aquí cada tablero es una tarea. El proceso 0 es el coordinador y tiene la lista de los 30 tableros. Los demás procesos son trabajadores: cada uno le pide un tablero al coordinador, lo resuelve y le manda el resultado, y con ese mismo mensaje pide otro. Cuando ya no quedan tableros, el coordinador les avisa y terminan.

El reparto es dinámico porque los tableros no tardan lo mismo. Así nadie se queda esperando mientras otro tiene todos los difíciles. El coordinador solo reparte y no resuelve tableros, lo hice así para que el código fuera más simple, aunque por eso con N = 4 solo trabajan 3 procesos.

Algunos detalles:
- El coordinador recibe con `MPI.ANY_SOURCE`, o sea que atiende al primer trabajador que le escriba.
- Se manda solo el número del tablero y no el tablero completo, porque todos ya tienen la lista.
- El trabajador copia el tablero antes de resolverlo porque `resolver()` lo modifica.
- Al final se muestra cuántos tableros se procesaron (30/30) y el tiempo total, medido con el reloj real.

## Ejecución con el contenedor

Cambia `N` por el valor elegido en `../INFORME.md` (en mi equipo salió 4).

Todos los tableros:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n N python /app/mpi_por_tableros/mpi_tableros.py --all
```

Un solo tablero, por ejemplo el 7:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n N python /app/mpi_por_tableros/mpi_tableros.py --id 7
```

En macOS cambia `"${PWD}:/app"` por `"$(pwd):/app"`.

## Resultados

Con N = 4 la mediana fue 38,57 s, contra 77,18 s del secuencial (aceleración de 2,00). Más detalles en `../INFORME.md`.
