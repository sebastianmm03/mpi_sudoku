# Informe de resultados

Todas las comparaciones usan el mismo archivo `seeds.txt`, el mismo equipo y el contenedor del taller.

## Entorno

- Equipo: Intel Core i5-12450H (8 núcleos / 12 hilos lógicos), 32 GB de RAM, Windows 11 Home + Docker Desktop (Docker 29.8.2)
- Versión del contenedor: `augustosalazar/slim-mpi:2`
- Cantidad de repeticiones por medición: 3
- Valor común de `N` elegido: 4 (recomendado por `detectar_procesos_mpi.py`, mediana 1,702 s)

### Calibración de `N` (contar primos hasta 2.000.000)

| N | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Mediana (s) | 4,047 | 2,483 | 2,603 | **1,702** | 1,760 | 2,066 | 1,727 | 1,746 | 2,521 | 2,273 | 2,750 | 3,879 |

### Elección del tamaño de grupo del híbrido (N = 4)

Probé las tres formas de repartir 4 procesos en grupos, con 3 corridas cada una, intercaladas (`mpi_hibrido.py --all --grupo G`):

| Tamaño de grupo | Configuración | Corrida 1 (s) | Corrida 2 (s) | Corrida 3 (s) | Mediana (s) |
| --- | --- | ---: | ---: | ---: | ---: |
| 1 | 4 grupos de 1 | 41,454 | 42,886 | 43,781 | **42,886** |
| 2 | 2 grupos de 2 | 51,712 | 49,102 | 49,972 | 49,972 |
| 4 | 1 grupo de 4 | 49,376 | 54,586 | 50,305 | 50,305 |

Se eligió el grupo de tamaño 1 porque tuvo la menor mediana. Estas 9 corridas se hicieron seguidas y en un momento en que el equipo estaba más lento que en las demás mediciones, así que sirven para comparar los tamaños entre sí, no para comparar con las otras versiones. Por eso la comparación final se volvió a medir (ver abajo).

## Comparación final con el mismo `N`

Para que la comparación sea justa, las cuatro versiones se midieron **en la misma sesión, intercaladas** (en cada vuelta se corrió una vez cada versión, y se hicieron tres vueltas). El híbrido se midió con el tamaño de grupo elegido (1).

| Vuelta | Secuencial (s) | MPI por tableros (s) | MPI por ramas (s) | MPI híbrido, grupos de 1 (s) |
| --- | ---: | ---: | ---: | ---: |
| 1 | 75,241 | 37,753 | 40,452 | 34,687 |
| 2 | 77,187 | 38,565 | 39,922 | 35,015 |
| 3 | 77,183 | 38,833 | 40,627 | 34,791 |
| **Mediana** | **77,183** | **38,565** | **40,452** | **34,791** |

| Implementación | Caso | Procesos | Mediana del tiempo total (s) | Aceleración frente a secuencial |
| --- | --- | ---: | ---: | ---: |
| Secuencial | Todos los IDs | 1 | 77,183 | 1,00 |
| MPI por tableros | Todos los IDs | 4 | 38,565 | 2,00 |
| MPI por ramas | Todos los IDs, uno después de otro | 4 | 40,452 | 1,91 |
| MPI híbrido (4 grupos de 1) | Todos los IDs | 4 | 34,791 | 2,22 |

Aceleración = tiempo secuencial / tiempo MPI.

### Primera tanda de mediciones (referencia)

Antes de la comparación final medí cada versión por separado, en otro momento. Las dejo porque muestran cuánto cambia el equipo de una tanda a otra (el secuencial pasó de 84 s a 77 s):

| Versión | Corrida 1 (s) | Corrida 2 (s) | Corrida 3 (s) | Mediana (s) |
| --- | ---: | ---: | ---: | ---: |
| Secuencial | 84,260 | 86,446 | 73,297 | 84,260 |
| MPI por tableros | 33,993 | 36,718 | 35,417 | 35,417 |
| MPI por ramas | 34,488 | 35,788 | 34,685 | 34,685 |

## Conclusiones

- **¿Qué estrategia obtuvo el menor tiempo y cuánto mejoró?** El híbrido con 4 grupos de 1 proceso fue el más rápido: 34,79 s contra 77,18 s de la versión secuencial, o sea una aceleración de 2,22 (el tiempo se redujo a un poco menos de la mitad). Le siguen MPI por tableros (2,00) y MPI por ramas (1,91). Ninguna versión llegó a 4 aunque se usaron 4 procesos.

- **¿Cómo afectaron la comunicación y las diferencias de duración entre tableros?** Los tableros tardan entre 1,2 y 6 s en secuencial, así que repartirlos fijos podía dejar procesos esperando. En MPI por tableros el reparto es dinámico (cada proceso pide otro tablero cuando termina), por eso la carga quedó pareja, pero el proceso 0 solo coordina y con N = 4 resuelven solo 3 procesos. Los mensajes son muy pequeños (un número de tablero y una tupla con el resultado), así que la comunicación casi no cuesta. En MPI por ramas la comunicación es el aviso de "ya lo resolví" y el `allgather` al final de cada tablero: todos los procesos tienen que esperar al más lento antes de pasar al siguiente, y eso se repite 30 veces. Otra cosa que noté es que cuando varios procesos corren a la vez, cada tablero tarda más que en la versión secuencial (por ejemplo el ID 3 tardó 5,2 a 5,8 s solo y bastante más cuando corrían 4 procesos juntos). No medí la causa, pero creo que se debe a que los procesos comparten recursos del procesador, y eso explica en parte por qué no se llega a una aceleración de 4.

- **¿Cómo se comparó repartir tableros con resolverlos en orden y repartir las ramas de cada uno?** Repartir ramas hace que un solo tablero se resuelva más rápido (el ID 3 bajó de unos 5,8 s a unos 1,4 s), que es algo que repartir tableros no puede hacer, porque un tablero lo resuelve un solo proceso. Pero como hay que esperar a todos al final de cada tablero, el total no mejora tanto y quedó un poco peor que repartir tableros (40,45 s contra 38,56 s). El híbrido con grupos de 1 es en la práctica repartir tableros con los 4 procesos resolviendo y sin proceso coordinador, y por eso le ganó a las otras dos. Con grupos más grandes (2 y 4) fue más lento, porque los procesos de un mismo grupo se esperan entre sí en cada tablero.

- **Limitaciones.** El reparto de tableros del híbrido es fijo (cada grupo sabe desde el principio cuáles le tocan), así que si a un grupo le tocan los tableros más difíciles, los demás terminan antes y esperan. Además, los tiempos cambian de una tanda a otra en este equipo (el secuencial dio 84 s en una tanda y 77 s en otra), por eso la comparación final se midió toda junta. Las diferencias pequeñas, como la de tableros contra ramas, pueden estar dentro de esa variación.
