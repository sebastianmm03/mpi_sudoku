# Tarea 3: combinar tableros y ramas

## Cómo funciona

Esta versión mezcla las dos anteriores. Los N procesos se dividen en grupos del mismo tamaño (con `--grupo G` se elige cuántos procesos tiene cada grupo). Cada grupo se encarga de unos tableros, y dentro del grupo los procesos se reparten las ramas de cada tablero.

1. Los grupos se arman con `comm.Split`. El número de grupo de cada proceso es `rank // tamaño_del_grupo`, así los procesos que tienen el mismo número quedan juntos. Con 4 procesos y grupos de 2, los procesos 0 y 1 son el grupo 0 y los procesos 2 y 3 son el grupo 1.
2. `Split` crea un comunicador nuevo (`gcomm`) que solo tiene a los miembros de mi grupo. Dentro de ese comunicador mi número y el tamaño del grupo se cuentan de nuevo desde 0.
3. Los tableros se reparten entre los grupos de forma fija: si hay 2 grupos, el grupo 0 toma los tableros 0, 2, 4... y el grupo 1 toma los 1, 3, 5...
4. Dentro de un grupo, cada tablero se resuelve igual que en `mpi_por_ramas`: se generan ramas, se reparten entre los miembros del grupo, y cuando uno encuentra la solución les avisa a los demás de su grupo (con `Iprobe` cada 5000 pasos). Todo eso usa `gcomm`, así que los avisos y la espera del `allgather` solo ocurren dentro del grupo.
5. Al final todos esperan a que terminen todos los grupos (`Barrier`), y el proceso 0 suma cuántos tableros procesó cada grupo (`reduce`) y muestra el tiempo total.

Solo el primer proceso de cada grupo imprime el resultado de cada tablero, para que no salga repetido.

## Cómo elegí el tamaño de los grupos

Con N = 4 solo hay tres opciones: 4 grupos de 1, 2 grupos de 2 o 1 grupo de 4. Probé las tres, 3 corridas cada una y intercaladas, y me quedé con la de menor mediana:

| Grupo | Configuración | Mediana (s) |
| --- | --- | ---: |
| 1 | 4 grupos de 1 | 42,89 |
| 2 | 2 grupos de 2 | 49,97 |
| 4 | 1 grupo de 4 | 50,30 |

Ganó el grupo de tamaño 1. Cuanto más grande es el grupo, más tiempo pierden los procesos esperándose entre ellos al final de cada tablero. Con grupos de 1 nadie espera a nadie, aunque un solo proceso resuelve cada tablero. Estas mediciones se hicieron en un momento en que el equipo estaba más lento, por eso sirven para comparar los tamaños entre sí y no con las otras versiones.

Después volví a medir los grupos de 1 y de 2 intercalados, junto con la versión por tableros, en un momento en que el equipo rendía normal (mediana de 3 corridas):

| Versión | Mediana (s) |
| --- | ---: |
| Híbrido, grupos de 1 | 34,48 |
| Por tableros | 38,25 |
| Híbrido, grupos de 2 | 39,87 |

También ganó el grupo de 1. Los grupos de 2, que son la mezcla real (varios grupos y varios procesos por grupo), fueron más lentos que repartir solo tableros. Los resultados finales están en `../INFORME.md`.

## Limitación

El reparto de tableros entre grupos es fijo, no dinámico. Si a un grupo le tocan los tableros más difíciles, el otro termina antes y se queda esperando. Para evitarlo habría que repartir los tableros dinámicamente con un coordinador, pero lo dejé fijo para que el código fuera más simple.

## Ejecución con el contenedor

Abre una terminal en la carpeta del proyecto. Cambia `N` por el valor elegido en `../INFORME.md` (en mi equipo salió 4) y `G` por el tamaño de grupo (el mejor fue 1).

### Windows (PowerShell)

Todos los tableros:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n N python /app/mpi_hibrido/mpi_hibrido.py --all --grupo G
```

Un solo tablero, por ejemplo el ID 7:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n N python /app/mpi_hibrido/mpi_hibrido.py --id 7 --grupo G
```

### macOS (Terminal)

Cambia `"${PWD}:/app"` por `"$(pwd):/app"` en los comandos anteriores.

## Salida

Por cada tablero muestra el ID, el grupo que lo resolvió, si se resolvió y el tiempo parcial. Al final muestra la configuración (cuántos grupos y de qué tamaño), cuántos tableros se procesaron y el tiempo total medido con el reloj real.

## Resultados

Con N = 4 y grupos de 1, la mediana fue 34,79 s contra 77,18 s de la versión secuencial (aceleración de 2,22). Los detalles están en `../INFORME.md`.
