# Informe de resultados

Completa este informe después de implementar las tres tareas MPI. Ejecuta las comparaciones con el mismo archivo `seeds.txt`, en el mismo equipo y con el contenedor del taller.

## Entorno

- Equipo: Intel Core i5-12450H (8 núcleos / 12 hilos lógicos), 32 GB de RAM, Windows 11 Home + Docker Desktop (Docker 29.8.2)
- Versión del contenedor: `augustosalazar/slim-mpi:2`
- Cantidad de repeticiones por medición: 3
- Valor común de `N` elegido: 4 (recomendado por `detectar_procesos_mpi.py`, mediana 1,702 s)

### Calibración de `N` (contar primos hasta 2.000.000)

| N | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Mediana (s) | 4,047 | 2,483 | 2,603 | **1,702** | 1,760 | 2,066 | 1,727 | 1,746 | 2,521 | 2,273 | 2,750 | 3,879 |

### Versión secuencial (`baseline_secuencial.py --all`)

| Corrida | Tiempo total (s) |
| --- | ---: |
| 1 | 84,260 |
| 2 | 86,446 |
| 3 | 73,297 |
| **Mediana** | **84,260** |

## Comparación final con el mismo `N`

Repite tres veces cada ejecución y registra la mediana. Mantén fijo el `N` elegido en todas las filas MPI. Incluye `--allow-run-as-root --use-hwthread-cpus --oversubscribe` en `mpiexec`, igual que en la calibración, para permitir valores de `N` mayores que los slots detectados.

| Implementación | Caso | Procesos | Mediana del tiempo total (s) | Aceleración frente a secuencial |
| --- | --- | ---: | ---: | ---: |
| Secuencial | Todos los IDs | 1 | 84,260 | 1,00 |
| MPI por tableros | Todos los IDs | N |  |  |
| MPI por ramas | Todos los IDs, uno después de otro | N |  |  |
| MPI híbrido | Todos los IDs | N |  |  |

Calcula la aceleración como `tiempo secuencial / tiempo MPI`. Mide el tiempo MPI desde el inicio del reparto hasta recibir todos los resultados necesarios.

## Conclusiones

- ¿Qué estrategia obtuvo el menor tiempo para los 30 tableros? ¿Cuánto mejoró respecto a la versión secuencial?
- ¿Cómo afectaron la comunicación y las diferencias de duración entre tableros?
- ¿Cómo se comparó repartir tableros con resolverlos en orden y repartir las ramas de cada uno?
