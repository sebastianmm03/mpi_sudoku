# Tarea 1: repartir tableros

Implementa una versión MPI en esta carpeta. Al ejecutar todos los tableros, cada ID debe ser una tarea que pueda asignarse a un proceso. Reutiliza el resolvedor de `../sudoku.py` y reúne los estados en el proceso coordinador.

Registra el tiempo total de ejecución y confirma que se procesaron los 30 IDs. Añade aquí el comando para ejecutar tu implementación con el contenedor. Incluye `--allow-run-as-root --use-hwthread-cpus --oversubscribe` en `mpiexec`, como en la calibración.
