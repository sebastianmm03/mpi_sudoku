# Informe de resultados

## Entorno

- Equipo: Intel Core i5-12450H (8 núcleos / 12 hilos), 32 GB de RAM, Windows 11 con Docker Desktop
- Versión del contenedor: `augustosalazar/slim-mpi:2`
- Cantidad de repeticiones por medición: 3
- Valor común de `N` elegido: 4 (lo recomendó `detectar_procesos_mpi.py`)

### Calibración de N

Mediana en segundos de contar primos hasta 2.000.000:

| N | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Mediana (s) | 4,047 | 2,483 | 2,603 | **1,702** | 1,760 | 2,066 | 1,727 | 1,746 | 2,521 | 2,273 | 2,750 | 3,879 |

El menor tiempo fue con N = 4. De N = 4 a 8 los tiempos son casi iguales y desde N = 9 empeoran.

## Comparación final con el mismo `N`

Para que la comparación sea justa, medí todas las versiones en la misma sesión, intercaladas: en cada vuelta corrí una vez cada versión, y repetí 3 vueltas. El híbrido se midió con grupos de 1.

| Vuelta | Secuencial (s) | Por tableros (s) | Por ramas (s) | Híbrido (s) |
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
| MPI híbrido (grupos de 1) | Todos los IDs | 4 | 34,791 | 2,22 |

La aceleración es el tiempo secuencial dividido entre el tiempo MPI.

### Tamaño de grupo del híbrido

| Grupo | Configuración | Mediana (s) |
| --- | --- | ---: |
| 1 | 4 grupos de 1 | 34,479 |
| 2 | 2 grupos de 2 | 39,871 |
| 4 | 1 grupo de 4 | 50,305 |

Los grupos de 1 y de 2 se midieron intercalados en una sesión aparte (3 corridas cada uno). Los grupos de 4 se midieron antes, cuando el equipo estaba más lento; en esa misma tanda los grupos de 1 dieron 42,886 s y los de 2 dieron 49,972 s. En las dos tandas ganó el grupo de 1, por eso lo usé en la comparación final.

## Conclusiones

- **Menor tiempo:** el híbrido con grupos de 1 fue el más rápido, con 34,79 s contra 77,18 s del secuencial, o sea una aceleración de 2,22. Le siguen por tableros (2,00) y por ramas (1,91). Ninguna llegó a 4 aunque se usaron 4 procesos.

- **Comunicación y duración de los tableros:** los tableros tardan entre 1,2 y 6 s, así que repartirlos bien importa. En tableros el reparto dinámico equilibra la carga y los mensajes son muy pequeños, pero el coordinador no resuelve y por eso solo trabajan 3 procesos. En ramas, al final de cada tablero todos esperan al proceso más lento, y eso se repite 30 veces. También vi que cuando corren varios procesos a la vez cada tablero tarda más que en secuencial (el 3 tardó unos 5,5 s solo y más cuando corrían 4 procesos). Creo que es porque los procesos comparten recursos del procesador, pero no lo medí.

- **Tableros contra ramas:** repartir ramas hace que un solo tablero se resuelva más rápido (el 3 pasó de unos 5,8 s a unos 1,4 s), cosa que repartir tableros no puede hacer. Pero como hay que esperar a todos en cada tablero, el total quedó un poco peor (40,45 s contra 38,57 s). El híbrido con grupos de 1 ganó porque usa los 4 procesos para resolver y no espera dentro de cada tablero. Con grupos de 2, que es la mezcla real, fue más lento (39,87 s).

- **Variación entre mediciones:** el equipo no rinde igual en todos los momentos. El secuencial dio 84 s en una primera tanda y 77 s en la comparación final. Por eso medí todo junto y usé la mediana de 3 corridas. Las diferencias pequeñas, como la de tableros contra ramas, pueden estar dentro de esa variación.
