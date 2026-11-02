# Tarea 3: combinar tableros y ramas

Esta versión mezcla las dos anteriores. Los procesos se dividen en grupos (con `--grupo G` se elige cuántos procesos tiene cada grupo). Cada grupo se encarga de unos tableros y, dentro del grupo, los procesos se reparten las ramas de cada tablero.

1. Los grupos se arman con `comm.Split`. El número de grupo de cada proceso es `rank // tamaño_del_grupo`. Por ejemplo, con 4 procesos y grupos de 2, los procesos 0 y 1 son el grupo 0 y los procesos 2 y 3 son el grupo 1.
2. Los tableros se reparten entre los grupos de forma fija: con 2 grupos, el grupo 0 toma los tableros 0, 2, 4... y el grupo 1 toma los 1, 3, 5...
3. Dentro de cada grupo, cada tablero se resuelve igual que en `mpi_por_ramas`, pero los avisos y el `allgather` solo se hacen entre los procesos del mismo grupo.
4. Al final todos esperan a que terminen todos los grupos y el proceso 0 suma cuántos tableros procesó cada grupo y muestra el tiempo total.

## Cómo elegí el tamaño de los grupos

Con N = 4 solo hay tres opciones: 4 grupos de 1, 2 grupos de 2 o 1 grupo de 4. Probé las tres (3 corridas cada una) y me quedé con la de menor mediana:

| Grupo | Configuración | Mediana (s) |
| --- | --- | ---: |
| 1 | 4 grupos de 1 | 34,48 |
| 2 | 2 grupos de 2 | 39,87 |
| 4 | 1 grupo de 4 | 50,30 |

Los grupos de 4 se midieron antes, en un momento en que el equipo estaba más lento (en esa misma tanda los grupos de 1 dieron 42,89 s y los de 2 dieron 49,97 s). Aun así, el orden fue el mismo: ganó el grupo de 1. Cuanto más grande es el grupo, más tiempo pierden los procesos esperándose entre ellos al final de cada tablero.

El reparto de tableros entre grupos es fijo. Si a un grupo le tocan los tableros más difíciles, el otro termina antes y se queda esperando.

## Ejecución con el contenedor

Cambia `N` por el valor elegido en `../INFORME.md` (en mi equipo salió 4) y `G` por el tamaño de grupo (el mejor fue 1).

Todos los tableros:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n N python /app/mpi_hibrido/mpi_hibrido.py --all --grupo G
```

Un solo tablero, por ejemplo el 7:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n N python /app/mpi_hibrido/mpi_hibrido.py --id 7 --grupo G
```

En macOS cambia `"${PWD}:/app"` por `"$(pwd):/app"`.

## Resultados

Con N = 4 y grupos de 1, la mediana fue 34,79 s, contra 77,18 s del secuencial (aceleración de 2,22). Más detalles en `../INFORME.md`.
