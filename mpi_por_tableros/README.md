# Tarea 1: repartir tableros

## Cómo funciona

En esta versión cada tablero es una tarea. El proceso 0 es el coordinador: tiene la lista de los 30 tableros y se los va dando a los demás procesos. Los otros procesos son los trabajadores: cada uno pide un tablero, lo resuelve y cuando termina le manda el resultado al coordinador y pide otro. Esto se repite hasta que ya no quedan tableros, y ahí el coordinador les avisa que terminaron.

El coordinador solo reparte y recibe resultados, no resuelve tableros. Cuando llegan todos los resultados muestra cuántos tableros se procesaron y el tiempo total.

## Por qué el reparto es dinámico

Los tableros no tardan lo mismo: unos se resuelven en 1,5 s y otros en 6 o 7 s. Si le hubiera dado 10 tableros fijos a cada proceso desde el principio, a uno le podían tocar los más difíciles y los demás terminar antes y quedarse esperando sin hacer nada. Así, cada trabajador pide un tablero nuevo apenas termina el anterior y todos trabajan hasta el final.

## Por qué el coordinador no resuelve

Lo hice así para que el código fuera más simple y fácil de entender. La desventaja es que con N = 4 solo resuelven 3 procesos, porque uno se dedica a coordinar. Por eso la aceleración no puede pasar de 3 aproximadamente.

## Cómo se comunican

- El trabajador le manda al coordinador un mensaje cuando está libre. La primera vez manda `None`, que quiere decir "estoy libre pero todavía no tengo ningún resultado".
- El coordinador le responde con el número (índice) del tablero que debe resolver. Mando solo el número y no el tablero completo porque todos los procesos ya tienen la lista de tableros y así el mensaje es más pequeño.
- Cuando el trabajador termina, le manda al coordinador una tupla con el índice, si se resolvió y cuánto tardó. Ese mismo mensaje sirve para pedir otro tablero.
- Cuando ya no quedan tableros, el coordinador responde `None`, que en este sentido significa "ya no hay más, puedes terminar".
- El coordinador usa `MPI.ANY_SOURCE` para atender al primer trabajador que le escriba, sin importar su número, y así no se queda esperando a uno lento.

Antes de resolver, el trabajador hace una copia del tablero porque `resolver()` modifica el tablero que recibe y no quiero dañar el original de la lista.

## Ejecución con el contenedor

Abre una terminal en la carpeta del proyecto. Cambia `N` por el valor elegido en `../INFORME.md` (en mi equipo salió 4).

### Windows (PowerShell)

Todos los tableros:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n N python /app/mpi_por_tableros/mpi_tableros.py --all
```

Un solo tablero, por ejemplo el ID 7:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n N python /app/mpi_por_tableros/mpi_tableros.py --id 7
```

### macOS (Terminal)

Cambia `"${PWD}:/app"` por `"$(pwd):/app"` en los comandos anteriores.

## Salida

Por cada tablero el programa muestra el ID, qué proceso lo resolvió, si se resolvió y el tiempo parcial. Los IDs no salen en orden porque cada trabajador termina cuando termina. Al final muestra cuántos tableros se procesaron (por ejemplo `30/30`) y el tiempo total medido con el reloj real, desde que empieza el reparto hasta que llegan todos los resultados.

## Resultados

Con N = 4 la mediana de tres ejecuciones fue 35,42 s, contra 84,26 s de la versión secuencial (aceleración de 2,38). Los detalles están en `../INFORME.md`.
