# Taller: resolver Sudoku con MPI

Resuelvo 30 tableros de Sudoku con backtracking y comparo la versión secuencial con tres formas de usar MPI. Todo se ejecuta con Docker usando la imagen `augustosalazar/slim-mpi:2`.

## Organización

- `sudoku.py`, `baseline_secuencial.py`, `detectar_procesos_mpi.py` y `seeds.txt`: archivos base del taller (versión secuencial y calibrador).
- `mpi_por_tableros/`: Tarea 1, se reparten los tableros entre procesos.
- `mpi_por_ramas/`: Tarea 2, los tableros se resuelven en orden y las ramas de cada uno se reparten entre procesos.
- `mpi_hibrido/`: Tarea 3, se combinan las dos ideas: los procesos se dividen en grupos, cada grupo resuelve unos tableros y dentro del grupo se reparten las ramas.
- `INFORME.md`: tiempos y conclusiones.

Cada carpeta tiene su propio README con la explicación y los comandos.

## Cómo ejecutar

Abre una terminal en la carpeta del proyecto (PowerShell en Windows).

Calibrar el número de procesos `N` (en mi equipo salió 4):

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 python /app/detectar_procesos_mpi.py
```

Versión secuencial:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 python /app/baseline_secuencial.py --all
```

Versiones MPI (cambia `N` por 4):

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n N python /app/mpi_por_tableros/mpi_tableros.py --all
```

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n N python /app/mpi_por_ramas/mpi_ramas.py --all
```

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n N python /app/mpi_hibrido/mpi_hibrido.py --all --grupo 1
```

En macOS cambia `"${PWD}:/app"` por `"$(pwd):/app"`.

## Resultados

Los tiempos y las conclusiones están en [INFORME.md](INFORME.md).
