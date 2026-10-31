# Tarea 2: repartir ramas de cada tablero

## Cómo funciona

En esta versión los tableros se resuelven uno después de otro, en orden, pero cada tablero se resuelve entre todos los procesos al mismo tiempo. Aquí no hay coordinador: los N procesos trabajan en cada tablero.

Para cada tablero se hace esto:

1. Se generan las ramas. Una rama es el tablero con las primeras casillas vacías ya rellenadas con una combinación de valores válidos. Por ejemplo, si la primera casilla vacía acepta el 2, el 5 o el 9, salen tres ramas. Se van rellenando más casillas hasta tener por lo menos 4 veces más ramas que procesos (con N = 4 son al menos 16), para que haya trabajo de sobra y se pueda repartir parejo.
2. Todos los procesos generan la misma lista de ramas, porque el cálculo es igual en todos.
3. Las ramas se reparten como cartas: el proceso 0 toma las ramas 0, 4, 8..., el proceso 1 toma las 1, 5, 9..., y así.
4. Cada proceso resuelve sus ramas con backtracking.
5. Cuando uno encuentra la solución les avisa a los demás y todos dejan de buscar.
6. Al final todos esperan a que los demás terminen ese tablero y después pasan al siguiente.

## Cómo se enteran los demás de que ya se resolvió

El problema es que mientras un proceso hace backtracking está metido en un ciclo y no mira mensajes. Por eso cada 5000 pasos revisa con `comm.Iprobe` si llegó un aviso. `Iprobe` solo pregunta si hay un mensaje y sigue, en cambio `recv` se quedaría esperando y frenaría la búsqueda.

Si llegó el aviso, el proceso lanza una excepción (`Detener`) que sale de golpe de todo el backtracking y deja de buscar en ese tablero.

## Para qué sirve el allgather

Al final de cada tablero uso `comm.allgather`. Hace que todos los procesos esperen hasta que cada uno haya terminado ese tablero y además junta lo que encontró cada uno, así se sabe si el tablero se resolvió. Si no estuviera, un proceso que termina rápido podría pasar al siguiente tablero mientras los demás siguen en el anterior.

Además, cada tablero usa su número como etiqueta (`tag`) en los mensajes, para que un aviso de un tablero no se confunda con el de otro.

## Limitación

El reparto de las ramas es fijo, no dinámico: cada proceso ya sabe desde el principio cuáles le tocan. Si a uno le tocan ramas difíciles, los demás terminan antes y se quedan esperando en el `allgather`.

## Ejecución con el contenedor

Abre una terminal en la carpeta del proyecto. Cambia `N` por el valor elegido en `../INFORME.md` (en mi equipo salió 4).

### Windows (PowerShell)

Todos los tableros, uno después de otro:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n N python /app/mpi_por_ramas/mpi_ramas.py --all
```

Un solo tablero, por ejemplo el ID 7:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n N python /app/mpi_por_ramas/mpi_ramas.py --id 7
```

### macOS (Terminal)

Cambia `"${PWD}:/app"` por `"$(pwd):/app"` en los comandos anteriores.

## Salida

Por cada tablero el programa muestra el ID, si se resolvió y el tiempo parcial. Los IDs salen en orden porque se procesan uno después de otro. Al final muestra cuántos tableros se procesaron y el tiempo total medido con el reloj real.

## Resultados

Con N = 4 la mediana de tres ejecuciones fue 34,69 s, contra 84,26 s de la versión secuencial (aceleración de 2,43). Un solo tablero sí mejora: por ejemplo el ID 3 pasó de unos 5,8 s a unos 1,4 s. Los detalles están en `../INFORME.md`.
