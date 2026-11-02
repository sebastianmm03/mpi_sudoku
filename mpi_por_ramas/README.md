# Tarea 2: repartir ramas de cada tablero

Los tableros se resuelven uno después de otro, en orden, pero cada tablero lo resuelven todos los procesos juntos. Aquí no hay coordinador.

Para cada tablero se hace esto:
1. Se generan las ramas. Una rama es el tablero con las primeras casillas vacías rellenadas con valores válidos. Se generan al menos 4 veces más ramas que procesos (16 con N = 4) para que haya trabajo de sobra.
2. Todos los procesos generan la misma lista de ramas.
3. Las ramas se reparten como cartas: el proceso 0 toma la 0, la 4, la 8..., el proceso 1 toma la 1, la 5, la 9... y así.
4. Cada proceso resuelve sus ramas con backtracking.
5. El primero que encuentra la solución les avisa a los demás y todos dejan de buscar.

Para enterarse de que otro ya resolvió, cada 5000 pasos del backtracking el proceso revisa con `Iprobe` si llegó un aviso. `Iprobe` solo pregunta si hay un mensaje y sigue, en cambio `recv` se quedaría esperando y frenaría la búsqueda. Si llegó el aviso, el proceso sale del backtracking con una excepción.

Al final de cada tablero uso `allgather` para que todos esperen a que los demás terminen antes de pasar al siguiente tablero. Además, cada tablero usa su número como etiqueta en los mensajes, para que un aviso no se confunda con el de otro tablero.

El reparto de ramas es fijo. Si a un proceso le tocan ramas difíciles, los demás terminan antes y esperan.

## Ejecución con el contenedor

Cambia `N` por el valor elegido en `../INFORME.md` (en mi equipo salió 4).

Todos los tableros:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n N python /app/mpi_por_ramas/mpi_ramas.py --all
```

Un solo tablero, por ejemplo el 7:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n N python /app/mpi_por_ramas/mpi_ramas.py --id 7
```

En macOS cambia `"${PWD}:/app"` por `"$(pwd):/app"`.

## Resultados

Con N = 4 la mediana fue 40,45 s, contra 77,18 s del secuencial (aceleración de 1,91). Un solo tablero sí mejora, por ejemplo el 3 pasó de unos 5,8 s a unos 1,4 s, pero el total no mejora tanto porque al final de cada tablero hay que esperar al proceso más lento. Más detalles en `../INFORME.md`.
