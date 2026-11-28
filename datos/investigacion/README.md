# Guía de la investigación de datos — ruta FB28 (Portal Américas ↔ Portal Norte)

> Para el equipo. Ustedes investigan y llenan los archivos de esta carpeta; el asistente los
> revisa, los convierte al JSON que lee el simulador (`datos/ruta_fb28.json`) y marca lo que falte.
> Cada dato corresponde a una fila de `docs/supuestos_y_datos_pendientes.md` (D1…D8, S1…S10).

## 1. Qué archivos llenar

| Archivo | Qué va | Datos que resuelve | Lo necesita el bloque |
|---|---|---|---|
| `fuentes.md` | Cada fuente consultada, con un id (F1, F2…) | Citas IEEE | Todos |
| `estaciones.csv` | Una fila por **estación** del servicio, en orden | D1, D2, D3 | **B** (lo primero) |
| `tramos.csv` | Tiempo (o distancia) entre estaciones consecutivas, por sentido | D4, S1 | C |
| `demanda.csv` | Cuánta gente entra a cada estación, por franja horaria | D5, D6, D7 | C |
| `parametros.csv` | Valores sueltos: capacidad del bus, velocidad, flota… | D8, S1–S4, S10 | C y D |

**Orden de entrega:** primero `estaciones.csv` + `fuentes.md` (con eso arranco el bloque B);
después tramos y demanda (bloque C); `parametros.csv` puede ir llenándose en paralelo.

Se pueden llenar en Excel o Google Sheets y exportar como **CSV UTF-8** (para que no se dañen las
tildes). Si Excel guarda con punto y coma (`;`) o coma decimal, no pasa nada: avísenme y lo adapto.

## 2. Reglas para todos los archivos

1. **Nada inventado.** Si un dato no aparece, la celda queda **vacía** y en `notas` se escribe
   `no encontrado` (y dónde se buscó). Un vacío honesto vale más que un número dudoso.
2. **Toda cifra lleva `fuente_id`.** Si es una estimación del equipo, `fuente_id` = `supuesto` y en
   `notas` va el razonamiento (por ejemplo: "promedio de las dos estaciones vecinas").
3. **Primero lo oficial:** TransMilenio S.A. (página web, mapas y fichas de servicios), portal de
   datos abiertos de TransMilenio, Datos Abiertos Bogotá, IDECA. Las fuentes secundarias (Google
   Maps, Moovit, noticias) sirven **solo para contrastar** y se marcan como `secundaria` en `fuentes.md`.
4. **Anotar el año del dato.** Una tabla de 2019 y una de 2024 no son comparables; si se mezclan,
   decirlo en `notas`.
5. **Nombres tal como los escribe la fuente oficial**, con tildes. Si hay dos nombres (por ejemplo,
   uno antiguo), el oficial en `nombre_oficial` y el otro en `notas`.
6. **Unidades fijas**, las de cada columna (segundos, metros, km/h, grados decimales). Punto decimal.
7. **Una persona llena y otra revisa.** La columna `revisado_por` lleva el nombre de quien comprobó
   la fila contra la fuente.

## 3. `estaciones.csv` (D1, D2, D3) — bloquea el bloque B

**Antes de llenar, confirmar D1:** que el servicio exista y su código exacto. Si no existe un
servicio directo Américas–Norte, **paren y avisen**: es una decisión del equipo (elegir el servicio
real más parecido o declararlo supuesto) y cambia el resto.

Una fila por estación **física**, ordenadas de **Portal Américas (orden 1) a Portal Norte**.
Los dos portales van una sola vez cada uno: el simulador los duplica solo (andén de llegada y de
salida, `contexto_fase2.md` §3.3.1).

| Columna | Qué poner | Ejemplo de formato (no es dato real) |
|---|---|---|
| `orden` | 1, 2, 3… sin saltos | `1` |
| `nombre_oficial` | Nombre de la estación | `Portal Américas` |
| `codigo_oficial` | Código de la estación si la fuente lo tiene; si no, vacío | |
| `troncal` | Troncal o corredor donde está | `Américas` |
| `latitud`, `longitud` | Grados decimales (WGS84), al menos 5 decimales. En Bogotá la latitud es cerca de 4,6 y la longitud cerca de −74,1 (con signo menos) | `4.62975`, `-74.20431` |
| `para_en_B` | `si` / `no`: ¿el servicio se detiene aquí yendo hacia Portal Norte? | `si` |
| `para_en_F` | `si` / `no`: ¿se detiene yendo hacia Portal Américas? | `si` |
| `fuente_id` | Id de `fuentes.md` | `F1` |
| `revisado_por` | Quien la verificó | |
| `notas` | Lo que haga falta aclarar | |

**Por qué `para_en_B` y `para_en_F` por separado:** muchos servicios no paran en las mismas
estaciones en los dos sentidos (o la estación tiene vagones distintos). El simulador arma un andén
por cada estación y sentido donde el bus sí para.

**Coordenadas:** ojo con invertir latitud y longitud, y con perder el signo menos. Verificar unas
cuantas pegando `lat, lon` en un mapa: deben caer encima de la estación.

## 4. `tramos.csv` (D4, S1) — bloque C

Una fila por cada par de estaciones **consecutivas donde el bus para**, en cada sentido
(B: de Américas hacia Norte; F: de Norte hacia Américas).

| Columna | Qué poner |
|---|---|
| `sentido` | `B` o `F` |
| `desde_orden`, `hasta_orden` | Los `orden` de `estaciones.csv` (en F van de mayor a menor) |
| `segundos` | Tiempo de recorrido entre las dos, si alguna fuente lo da |
| `distancia_metros` | Distancia por la vía, si no hay tiempo |
| `metodo` | `oficial` (de la fuente), `medido` (lo cronometró el equipo en un viaje real) o `calculado` |
| `fuente_id`, `notas` | Como siempre |

Basta con **una** de las dos columnas (`segundos` o `distancia_metros`). Si solo hay distancias,
hace falta `velocidad_comercial` en `parametros.csv`, con fuente, y el tiempo lo calculo yo.
Si no hay ninguna, avísenme: puedo calcular la distancia en línea recta con las coordenadas, pero
queda marcada como **supuesto** (subestima la distancia real).

## 5. `demanda.csv` (D5, D6, D7) — bloque C

Cuánta gente **entra** a cada estación, por franja horaria. Lo más probable es encontrarla como
"validaciones" o "entradas" por estación en los datos abiertos de TransMilenio.

| Columna | Qué poner |
|---|---|
| `orden`, `nombre_oficial` | Los de `estaciones.csv` |
| `sentido` | `B`, `F`, o vacío si la fuente no separa sentidos (lo normal) |
| `franja_inicio`, `franja_fin` | `hh:mm` en 24 horas, por ejemplo `06:00` y `07:00` |
| `valor` | El número que da la fuente |
| `unidad` | Tal como viene: `entradas/hora`, `validaciones/día`… (yo hago la conversión) |
| `fuente_id`, `notas` | Indicar el día o período que representa (día hábil típico, un mes, un año) |

- Si la fuente **no separa sentidos**, se deja vacío: el reparto entre B y F será un **supuesto**
  que decidimos juntos.
- Buscar al menos: hora pico de la mañana, hora valle y hora pico de la tarde. Con eso queda
  resuelta D6 (las franjas). Si hay datos por hora del día completo, mejor.
- **D7 no se da por cierta:** la hipótesis "en la mañana la demanda va hacia el norte y en la tarde
  se invierte" se acepta solo si los datos la muestran. Si encuentran algo al respecto, anótenlo.
- Los portales de **llegada** tendrán tasa 0 en el modelo (S12); de todas formas anoten su demanda
  real como andén de salida.

## 6. `parametros.csv` (D8, S1–S4, S10)

Ya trae las filas; solo hay que llenar `valor`, `fuente_id` y `notas`.

| Parámetro | Qué buscar o decidir |
|---|---|
| `capacidad_bus` | Pasajeros que caben en el vehículo del servicio (D8). Hoy el simulador usa 10, que no es real |
| `tipo_vehiculo` | Articulado o biarticulado |
| `velocidad_comercial` | Solo si `tramos.csv` trae distancias y no tiempos (S1) |
| `buses_en_servicio` e `intervalo_de_paso` | Cuántos buses opera el servicio, o cada cuántos minutos pasa uno. Sirve para la flota inicial |
| `hora_inicio_simulacion` | Decisión del equipo (S2), por ejemplo el inicio de la hora pico |
| `tope_flota` | Decisión del equipo (S4): máximo de buses al despachar |
| `probabilidad_prioritario` | Proporción de usuarios con prioridad (S10). Hoy es 0,5 y no es real |

## 7. Lista de verificación antes de entregarme

- [ ] D1 confirmado (el servicio existe y tiene ese código), con fuente.
- [ ] `estaciones.csv` completo: `orden` sin saltos, de Portal Américas a Portal Norte.
- [ ] Cada fila con `fuente_id` y `revisado_por`.
- [ ] Coordenadas comprobadas en un mapa (al menos los portales y tres estaciones intermedias).
- [ ] `fuentes.md` con cada id usado, sus URL y fechas de consulta.
- [ ] Vacíos explicados en `notas`, sin cifras inventadas.

Cuando esté, digan "entrega 1 lista" y yo: valido los archivos (orden, coordenadas dentro de
Bogotá, sentidos, fuentes), les reporto lo que encuentre y armo el JSON del bloque B.
