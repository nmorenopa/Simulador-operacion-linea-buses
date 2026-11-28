# Contexto del proyecto — Fase 2: Simulador de TransMilenio (ruta Portal Américas ↔ Portal Norte)

> Documento para que el asistente (Claude Code) y el equipo compartan el mismo contexto.
> Equipo: Pablo José Cárdenas, Nicolás Moreno Parra y Santiago Rodríguez Ortega.
> Curso: Estructuras de Datos. **Entrega: fecha aún no fija** (se había aplazado al sábado
> 28-nov-2026; el 27-nov Nicolás indicó que no es definitiva). Se avanza etapa por etapa (§9).

## 1. Objetivo del curso (lo que realmente importa)

El objetivo es **aprender y poder defender oralmente** cómo funcionan las estructuras de datos y
cuándo aplicarlas. El simulador es el vehículo, no el fin. Prioridad en este orden:

1. Que las estructuras nuevas estén implementadas **a mano por el equipo**.
2. Que todo funcione junto.
3. Que se vea profesional.

Si falta tiempo, se recorta primero lo visual, luego las estructuras extra. Nunca se reemplaza
una estructura por una librería.

## 2. Estado de partida (Fase 1, commit `80003fb`)

Simulador de una línea circular de 8 paradas con interfaz Tkinter. Ya existen, hechas por el equipo:

| Estructura | Uso actual |
|---|---|
| `Nodo` | Pieza base de las listas enlazadas |
| `ArregloDinamico` (crece ×1.618) | Flota, paradas, pasajeros a bordo, series de estadísticas |
| `Pila` | Historial para deshacer |
| `Cola` | Pasajeros en cada nivel de prioridad; operaciones pendientes de la interfaz |
| `ColaCircular` | Ruta de cada bus (rotar = avanzar a la siguiente parada) |
| `ColaPrioridad` (arreglo de colas) | Orden de abordaje en cada parada |

Arquitectura actual por capas: `estructuras/` → `simulador/` → `app.py` (Tkinter).
Hay 132 pruebas pytest que cubren las capas 1 y 2. La documentación completa del estado
anterior está en `docs/descripcion.md`.

## 3. Nuevo rumbo (Fase 2)

### 3.1 Qué se hace
Escalar el simulador a **una sola ruta de TransMilenio: Portal Américas ↔ Portal Norte**
(ida y vuelta), con **interfaz web** que dibuje el mapa de Bogotá.

- Un único servicio, el **FB28**: se llama **B28** cuando va de Portal Américas a Portal Norte y
  **F28** cuando va hacia Portal Américas.
- Se sigue modelando como **ruta circular** (ida + vuelta = un ciclo), por eso se conserva la
  `ColaCircular` de la Fase 1.

### 3.2 Decisiones del grupo
1. **Sistema:** TransMilenio, por los problemas logísticos que el equipo conoce como residentes.
2. **Ruta piloto:** Portal Américas ↔ Portal Norte. Conecta el occidente con el norte, y hay
   evidencia de congestión en el Portal Américas y de afectaciones en la Autopista Norte.
   Se eligió portal a portal (y no una troncal) porque origen y destino están bien definidos;
   algunas troncales inician en estaciones compartidas donde los buses ya llegan con pasajeros.
3. **Interfaz web** (HTML, CSS y JavaScript) en lugar de Tkinter: permite un mapa real con zoom
   y una presentación más profesional. La lógica en Python ya está separada de la interfaz.
4. **Datos oficiales:** se guiarán por la información publicada por TransMilenio S.A. (entidad
   gestora, no dueña de los buses; los operan concesionarios) y por los datos abiertos de Bogotá.
   Lo que falte se estima y se declara como **supuesto del modelo**.

### 3.3 Alcance
- Una ruta lineal con dos sentidos. **Sin transbordos.**
- Estaciones reales sacadas de datos abiertos (GeoJSON de estaciones troncales, datos de 2023,
  sin licencia declarada: se cita como fuente y se verifica a mano).
- **Por confirmar:** que exista servicio directo Américas–Norte y qué estaciones recorre.
  La lista de estaciones se revisa manualmente y se guarda en `datos/`.
- Modelo de la ruta: `ColaCircular` de 2N posiciones (estaciones de ida y luego las de vuelta
  en orden inverso), de modo que avanzar siga siendo rotar.
- **Fuera de alcance (por ahora):** varias troncales, transbordos, grafos, rutas de alimentación.

### 3.3.1 Cambio de letra B28 ↔ F28 (decidido el 28-nov; aplicar en la etapa 3 y al definir `datos/`)

**Idea:** la letra **no se guarda en el bus, se deduce** del andén donde está. Cada andén
(estación + sentido) conoce su `sentido` (`"B"` o `"F"`); el servicio del bus es ese sentido más
el número de la ruta. Hay una sola fuente de verdad, así que `agregar_bus()`, `deshacer()` y el
reinicio no necesitan manejar la letra aparte. Se descartó un "interruptor" en el bus que se
voltea en los portales, porque puede quedar desincronizado con la posición.

```
 posición:  0      1    ...   N-1          N           N+1  ...  2N-1
 andén:   P.Amé → ... → ... → P.Norte  |  P.Norte  →  ...  → ... → P.Amé
 sentido:   B      B    ...    B       |     F         F   ...     F
                                       ↑                            ↓
                       aquí rota de B a F        y aquí vuelve a B (cierra el ciclo)
```

**Decisiones del equipo:**
1. **Cada portal aparece dos veces en el anillo:** un andén de llegada (fin de un sentido, solo se
   baja gente) y uno de salida (inicio del otro sentido, solo sube gente). Así todo andén tiene un
   único sentido, y el minuto extra en el portal representa el retorno del bus.
2. **El destino de cada pasajero se elige entre los andenes que quedan adelante en su mismo
   sentido**, hasta el portal de llegada. Nadie "da la vuelta" dentro del bus. Esto resuelve el
   pendiente anotado en la sección del AVL (`explicacion_estructuras.md` §2.1 (g), punto 7).

**Qué toca cada capa (guía; `simulador/` lo escribe el equipo):**

| Capa | Cambio |
|---|---|
| `datos/` | Cada andén del JSON trae su `sentido` (`"B"`/`"F"`); el número de la ruta (`"28"`) va en los datos, no fijo en el código. Los portales aparecen dos veces (llegada y salida). |
| `simulador/parada.py` | `Parada` recibe el atributo `sentido` (un dato más, como `nombre`). |
| `simulador/bus.py` | Un método, por ejemplo `servicio()`, que devuelve el sentido de `parada_actual` más el número de ruta (`"B28"`). O(1). |
| `simulador/simulador.py` | `_generar_llegadas` elige el destino según la decisión 2. `estado()` incluye el `servicio` de cada bus; en `eventos`, `"cambio_servicio": True` cuando la parada siguiente tiene otro sentido. |
| API | Nada nuevo: el dato viaja dentro de `estado()`. |
| Web | Solo dibuja la etiqueta (y puede animar el giro en el portal con `cambio_servicio`); no decide la letra. |

**Efecto en el AVL:** el resumen de esperas por andén separa naturalmente los dos sentidos de una
misma estación, que son problemas logísticos distintos.

### 3.4 Estructuras nuevas (implementadas por el equipo)
Estado al 28-nov: **montículo (de mínimos y de máximos), AVL y árbol de segmentos ya
implementados** como TDA (etapa 1). Usos definidos en la etapa 2 (justificación completa en
`explicacion_estructuras.md` §2):

| Estructura | Uso | Estado |
|---|---|---|
| Árbol balanceado (AVL) | Índice de esperas de los pasajeros que ya abordaron: clave `(tiempo_espera, id_pasajero)` → `Pasajero` | **Decidido** (28-nov), §2.1 |
| Montículo de máximos | Cola de atención del operador: alertas de saturación de andén, con invalidación perezosa | **Decidido** (28-nov), §2.2. El de mínimos queda sin uso en esta fase |
| Árbol de segmentos | Panorama de alertas por **sector** (rango de andenes que elige el operador): cuántos andenes pendientes hay y cuál es el más crítico. Es una copia derivada del montículo | **Decidido** (28-nov), §2.3 |

**Las tres decisiones de uso de la etapa 2 quedaron cerradas el 28-nov.** Se mantienen separadas y
solo se conectan en el punto único de publicación de alertas (§3.6). Ninguna quita una estructura
lineal de la Fase 1.

| Estructura | Responde a | Se actualiza cuando | Consulta pública |
|---|---|---|---|
| AVL | ¿Quiénes esperaron N minutos o más, y dónde? | Un pasajero aborda | `consultar_esperas(minimo, limite)` → `GET /api/esperas` |
| Montículo de máximos | ¿Qué andén atiendo primero? | Se publica una alerta (punto único) | `atender()` → `POST /api/atender`; `GET /api/alertas` |
| Árbol de segmentos | ¿Cómo está este sector: cuántos pendientes y cuál es el peor? | Cambia el estado de alerta de un andén (punto único) | `consultar_sector(desde, hasta)` → `GET /api/sector` |
| Árbol B+ | Histórico de viajes por rango de tiempo | Extra (se recorta primero) |

El 28-nov se agregaron al AVL `maximo()`, `minimo()` y `techo()` (escritos por la IA con el visto
bueno de Nicolás), que devuelven `(clave, valor)` o `None` si el árbol está vacío, con sus pruebas.

Grafos: no se han visto en clase; se dejan para una fase posterior (transbordos y camino mínimo).

### 3.5 Motor por tiempos, despacho y alertas (decidido el 28-nov; aplicar en las etapas 3, 4 y 5)

> Esta sección reúne todo lo que cambia en el motor por las decisiones del AVL y del montículo.
> Cada valor numérico es provisional y está en `supuestos_y_datos_pendientes.md`: **no se
> inventan cifras**; los datos reales los define el equipo en la etapa 3.

#### 3.5.1 El reloj: ticks (opción A2)

- Un **tick** es un paso del reloj y dura `SEGUNDOS_POR_TICK` segundos (constante nombrada; su
  valor se fija en la etapa 3, cuando existan los tiempos reales de los tramos).
- Los tramos vienen en **segundos** desde `datos/` y se convierten a **ticks enteros**.
- Consecuencias:
  1. Las tasas por minuto pasan a **tasas por tick**: llegadas, `intentos_llegada` y una
     probabilidad que debe quedar ≤ 1.
  2. `Pasajero.tiempo_espera()` y la clave del AVL quedan **en ticks**. Todo lo que ve el usuario
     (el umbral que elige el operador, `espera_promedio`, la tabla de esperas) va **en minutos**.
     La conversión vive **dentro del Simulador**: `consultar_esperas` recibe minutos. La API no convierte.
  3. La **hora del día simulada** sale de la hora de inicio más `ticks × SEGUNDOS_POR_TICK`.
  4. **Invariante nuevo:** cada bus tarda exactamente la duración de su tramo, **en ticks**.
     Reemplaza a "cada bus avanza exactamente una parada por tick"; hay que cambiar las pruebas
     que lo verifican (por ejemplo, `test_cada_tick_avanza_el_reloj_y_los_buses_una_parada`).
- Se mantienen: conservación de pasajeros, capacidad nunca superada, prioridad al abordar y
  reproducibilidad con la misma semilla y los mismos parámetros.

#### 3.5.2 Buses en estación o en tránsito

- Cada bus está **en estación** (llega, bajan y suben pasajeros) o **en tránsito** entre dos
  andenes consecutivos de su `ColaCircular`.
- **Tabla de tramos:** un `ArregloDinamico` alineado con las 2N posiciones de la ruta; la
  posición i guarda la duración en ticks del tramo que sale del andén i hacia el siguiente.
- Cada bus lleva los **ticks restantes** de su tramo y la **duración total** del tramo.
- Al llegar a un andén: bajan pasajeros, suben pasajeros, rota su `ColaCircular` y arranca el
  siguiente tramo con su duración. **Permanencia en estación = 0** por ahora.
- La `ColaCircular` de la Fase 1 sigue girando como antes, ahora cada vez que el bus **llega** a un
  andén, no en cada tick.
- `Parada.abordar()` devuelve un `ArregloDinamico` con los pasajeros que subieron (decisión del
  AVL); el Simulador los inserta en el AVL. La Parada no conoce ni el AVL ni el montículo.
- Tiempos por tramo: **supuesto** (por ejemplo, distancia entre estaciones / velocidad supuesta).
  Mientras no haya datos, la tabla es un **placeholder** marcado.

#### 3.5.3 Tasas de llegada por andén y por franja horaria

- Cada andén tiene una **tasa de llegada propia** (desde `datos/`), multiplicada por un factor
  según la **franja horaria** (hora pico). Por eso el Simulador necesita una **hora de inicio**.
- La probabilidad de prioritarios sigue siendo **global**.
- Es **condición** para que el montículo tenga sentido: con tasas iguales, todos los andenes se
  saturan parecido y la cola de alertas no tendría nada que ordenar.
- **Hipótesis a verificar, no a dar por cierta:** en la mañana la demanda fuerte va de Américas
  hacia el norte y en la tarde se invierte. Debe salir de la investigación del equipo.

#### 3.5.4 Cola de alertas (montículo de máximos)

Resumen (detalle completo en `explicacion_estructuras.md` §2.2):

- `Monticulo("maximos")` en el Simulador. Elemento:
  `(severidad, -tick_deteccion, -secuencia, (id_andén, versión))`, con
  `severidad = esperando / capacidad_bus`.
- Por andén, en `ArregloDinamico`s indexados por `id_andén`: `version`, `ultima_publicada`
  (o `None`) y `tick_deteccion` (inicio de la saturación actual: se conserva al republicar y se
  reinicia si el andén sale de saturación y vuelve a entrar).
- El conjunto de andenes con bus en camino se calcula **una vez por tick** (un recorrido de la
  flota) y se reutiliza para todos los andenes: O(B + P) por tick.
- **Evaluación al final de cada tick** (después de las llegadas y el abordaje), andén por andén:
  si tiene bus en camino no se hace nada; si no está saturado se restablece la referencia; si está
  saturado, se publica la primera alerta al cruzar `UMBRAL_SATURACION`, y después una nueva
  (versión + 1) cada vez que `|severidad - ultima_publicada| / ultima_publicada >= CAMBIO_MINIMO`
  (20 %), **subiendo o bajando** (regla simétrica). Solo la última versión es válida.
- **Al extraer** se descarta la alerta si su versión no es la actual, si el andén ya no está
  saturado o si ya tiene un bus en camino.
- La referencia se restablece al salir de saturación, cuando llega el bus despachado y al deshacer
  el despacho.
- **Ver las k más urgentes:** extraer k válidas (descartando obsoletas) y reinsertar **las mismas
  tuplas**. Es una "lectura lógicamente pura" y va dentro del candado de la API.
- Al implementar hay que usar los nombres reales de `estructuras/monticulo.py`: `insertar`,
  `extraer_raiz`, `ver_raiz`, `mostrar`, `tamano` y `esta_vacio`.

#### 3.5.5 Despacho de buses (reemplaza a `agregar_bus`)

- `agregar_bus()` (el bus que aparece en la parada más llena) **se reemplaza** por:
  - `Simulador.atender()`: extrae la primera alerta válida de la **raíz** y despacha. Si no hay
    alertas válidas, error controlado (la API lo devuelve como 4xx).
  - `despachar_bus(id_andén)`: método interno que crea el bus y lo pone a viajar.
  - La constante de la Pila se renombra en coherencia (por ejemplo, `ACCION_DESPACHAR_BUS`).
  - Hay que actualizar las pruebas del Simulador y de la API afectadas. **Mostrar el diff a Nicolás
    antes de aplicarlo.**
- **Portal de salida:** para cada portal se suma la duración de los tramos, en el sentido de la
  ruta, desde su andén de salida hasta el andén destino, y se elige el de **menor tiempo**. Es la
  regla general, y sirve igual con más portales en la Fase 3.
- El bus entra a la flota **ya en tránsito** desde el portal; no aparece en el andén.
- **Expreso y vacío (supuesto del modelo, sin afirmar que TransMilenio lo haga):** pasa por cada
  andén intermedio **sin bajar ni subir** pasajeros; su `ColaCircular` rota igual, porque pasa por
  todos. En el andén destino se comporta como un bus normal. La web debe **distinguirlo visualmente**.
- **Después de llegar sigue circulando** en la ruta para siempre: la flota crece hasta el tope.
- **Tope de flota:** constante nombrada. Si se alcanza, error controlado.
- **"Bus en camino"**: una sola fuente de verdad, `bus.anden_destino` (el andén hacia el que va,
  o `None` cuando ya llegó o es un bus normal). Se deriva recorriendo la flota (O(B), acotado por el
  tope), sin una bandera aparte por andén. Mientras un andén tenga bus en camino, no genera ni
  acepta alertas.
- **Deshacer un despacho** (propuesta aprobada):
  - Solo si el último bus despachado **va vacío**, que es la regla vigente. Como va expreso, siempre
    está vacío hasta llegar.
  - Al deshacer se quita el bus (y con él su `anden_destino`, así que el andén deja de tener bus en
    camino) y se restablece `ultima_publicada` del andén. Si sigue saturado, vuelve a alertar al
    final del siguiente tick. No se devuelve al montículo la alerta extraída.
  - Si el bus ya llegó y subió gente, se rechaza y la acción se conserva en la Pila.
  - Pruebas pedidas:
    1. despacho → deshacer (va vacío) → el andén vuelve a alertar;
    2. despacho → el bus llega y sube gente → deshacer rechazado → la acción sigue en la Pila.

#### 3.5.6 Qué expone cada capa (etapas 4 y 5)

- **`estado()`**:
  - hora simulada;
  - por bus: `estado` (`en_estacion` o `en_transito`), andén actual o tramo (andén origen y andén
    destino), ticks restantes, duración total del tramo, `servicio` (B28/F28), si es expreso y su
    `anden_destino`.
  - `andenes_pendientes` del total de la ruta, con `consultar_todo()` del árbol de segmentos en
    O(1) (definición en §3.6).
  - Las alertas **no** van aquí.
- **`GET /api/ruta`** (se pide una vez al cargar):
  - andenes con `id`, `nombre`, `sentido`, `lat`, `lon` y `es_portal`;
  - la duración de cada tramo, en ticks y en segundos;
  - `segundos_por_tick`.
- **`GET /api/alertas?limite=N`**: las N alertas más urgentes (solo lectura).
- **`POST /api/atender`**: reemplaza a `POST /api/agregar-bus`. Errores 4xx: cola sin alertas
  válidas, tope de flota.
- **`GET /api/esperas?minimo=N`**: consulta del AVL (N en minutos).
- **`GET /api/sector?desde=ID&hasta=ID`**: panorama del árbol de segmentos (§3.6). Errores 4xx:
  ids inválidos, sentidos distintos, rango invertido.
- **Web:**
  - Cada bus se muestra parado en un andén o desplazándose entre dos. El JS calcula el progreso
    como `1 - restantes / duración` e interpola la posición sobre el tramo, al principio en **línea
    recta** entre estaciones consecutivas (seguir el corredor real es un extra).
  - Un tramo puede tardar varios ticks: la animación avanza una fracción por tick, no salta de estación.
  - Panel "Atender ahora" con las alertas más urgentes y un botón "Atender", que solo atiende la raíz.
  - El bus expreso se ve distinto.
  - Panel de sector (**obligatorio en la etapa 5**, si no la decisión del árbol pierde relevancia):
    selector de sentido B28/F28; el operador marca dos estaciones y el JS toma de `GET /api/ruta`
    los ids de los andenes de ese sentido, **ordena los dos ids** (solo compara dos números) y llama
    a `GET /api/sector`. Muestra `andenes_pendientes` y el más crítico (si hay), y puede resaltar
    el sector sobre la polilínea. Clic directo sobre la polilínea: mejora opcional, fuera del alcance.
  - Sin lógica en el JS y sin WebSockets.

#### 3.5.7 Extras de la fase final (vivos, NO implementar sin que se pida)

1. Alerta de bus retrasado (tiempo programado frente a real).
2. Incidentes o bloqueos de vía con duración aleatoria, que reprograman llegadas. Ahí sí vuelve la
   agenda de eventos con el **montículo de mínimos**.
3. Permanencia en estación variable según la carga.
4. Más portales, rutas y troncales.
5. Variante del AVL con el tiempo total de viaje (espera + a bordo).

Lo de hoy se diseña para no cerrarles la puerta: por ejemplo, los datos de la alerta pueden pasar
a `(tipo, id_objeto, versión)` sin reescribir la cola, porque la secuencia única evita que Python
los compare.

#### 3.5.8 Pruebas sugeridas para la etapa 3

- La raíz del montículo corresponde al andén más saturado en un escenario armado a mano.
- Se descartan al extraer las alertas obsoletas (versión vieja, andén ya no saturado, bus en camino).
- Regla del 20 % simétrica: publica al subir y al bajar ≥ 20 %, no publica con cambios menores, y
  publica la primera al cruzar el umbral.
- No se despachan dos buses para el mismo andén; el despacho elige el portal de menor tiempo; se
  respeta el tope de flota; atender sin alertas válidas da un error controlado.
- El expreso no baja ni sube a nadie en los andenes intermedios.
- Cada bus tarda exactamente la duración de su tramo, en ticks.
- Conservación de pasajeros, capacidad nunca superada y reproducibilidad con la misma semilla.
- Ver las k más urgentes deja el montículo equivalente en sus alertas válidas.
- Las dos pruebas de deshacer de §3.5.5.
- AVL: `tamano()` igual a pasajeros abordados; `verificar_balance()` y orden de `en_orden()`
  válidos; `rango` frente a un filtro lineal (extremos incluidos, rango invertido, árbol vacío);
  la conversión de minutos a ticks en `consultar_esperas`, con un SPT que no divida a 60 (por
  ejemplo, 45 s por tick y N = 1 da un umbral de 2 ticks: 1 tick queda fuera y 2 ticks quedan
  dentro) y la frontera con un número impar de ticks (30 s por tick, espera de 3 ticks = 1,5 min:
  entra con N = 1 y no entra con N = 2).
- `tick_deteccion` se reinicia cuando el andén sale de saturación y vuelve a entrar.

### 3.6 Árbol de segmentos: panorama por sector (decidido el 28-nov; aplicar en las etapas 3, 4 y 5)

Detalle y justificación completos en `explicacion_estructuras.md` §2.3. Para la implementación:

- **Vocabulario:** un **tramo** es el trayecto entre dos andenes consecutivos; un **sector** es el
  rango de andenes que elige el operador. Los nombres del código y de la API siguen esta regla.
- **Índice:** las 2N posiciones de la ruta (B28 en la primera mitad, F28 en la segunda).
- **Hoja del andén i:** `(severidad_publicada, i, pendiente)`, o `(0.0, i, 0)` sin alerta vigente.
  **Neutro:** `(float("-inf"), float("inf"), 0)`, una tupla inmutable.
- **`combinar`:** gana la severidad mayor y, si empatan, el índice menor; los pendientes se suman.
  La hoja, `combinar` y el neutro viven en el Simulador; el árbol sigue genérico.
- **`andenes_pendientes`:** andenes **saturados sin bus en camino** (con alerta vigente en el
  montículo). No es "andenes saturados".
- **Punto único de publicación:** un método privado del Simulador actualiza montículo y árbol
  juntos, solo en 5 transiciones:
  1. se publica una alerta;
  2. el andén sale de saturación;
  3. se despacha un bus hacia el andén;
  4. se deshace un despacho;
  5. reinicio.

  Nunca se actualiza en cada tick.
- **Construcción:** las hojas iniciales se arman en un `ArregloDinamico` y se pasa su `mostrar()`
  (lista copia) al constructor. Esa lista es temporal y justificada; no se modifica `estructuras/`.
- **`consultar_sector(id_desde, id_hasta)`:** devuelve diccionarios con `andenes_pendientes` y, si
  hay alguno, el más crítico (id, nombre, sentido, severidad publicada). `ValueError` si un id no
  existe, si los sentidos son distintos o si el rango está invertido.
- **Supuestos de los que depende:** S5 (umbral > 0 y ninguna alerta vigente por debajo del
  umbral), S12 (tasa 0 en los andenes de llegada de cada portal) y S13 (destino aguas abajo en el
  mismo sentido), en `supuestos_y_datos_pendientes.md`.
- **Usar los nombres reales** de `estructuras/arbol_segmentos.py`: `consultar`, `consultar_todo`,
  `actualizar`, `tamano` y `esta_vacio`.
- **Pendiente heredado:** el árbol de segmentos todavía no tiene archivo de pruebas pytest propio.

**Pruebas sugeridas para la etapa 3:**

- `consultar_sector` frente a un recorrido lineal de referencia sobre las severidades publicadas:
  sector de un solo andén, de toda una mitad, extremos incluidos, rango invertido y sentidos
  distintos.
- `combinar` es asociativa y el neutro no altera (con tuplas al azar).
- Tras cada tick, `consultar_todo()` coincide con el máximo de severidad de las alertas vigentes,
  y su cantidad de pendientes coincide con las alertas válidas del montículo. Se comparan **solo la
  severidad y la cantidad**, no el id, porque el desempate difiere.
- Tras despachar, deshacer y reiniciar, el árbol queda consistente con el montículo.
- Con alertas al azar, ninguna hoja vigente queda por debajo del umbral (S5).
- Los andenes de llegada de cada portal nunca alertan (S12).
- Reproducibilidad con la misma semilla.

## 4. Arquitectura objetivo (3 capas, nomenclatura de Nicolás)

```
CAPA 1 — Núcleo abstracto (Python puro, sin web)
  estructuras/   nodo, pila, cola, arreglo, montículo, AVL, árbol de segmentos... (genéricas)
  simulador/     entidades del dominio (Pasajero, Parada/Estación, Bus) y el Simulador
                 -> archivo clave: simulador/simulador.py
CAPA 2 — API (api/)
  FastAPI. "Puertas" GET y POST (no es un CRUD) que traducen peticiones a llamadas del Simulador
CAPA 3 — Interfaz web (web/)
  index.html, css/, js/: mapa de la ciudad, buses animados, panel de control

datos/    JSON de la ruta (estaciones, coordenadas, sentido)
tests/    pytest para las capas 1 y 2 (Playwright por evaluar para la capa 3)
docs/     Documentación en Markdown
legacy/   app.py de Tkinter (Fase 1, se conserva sin editar)
```

Dentro de la capa 1 se mantiene la separación: `estructuras/` no sabe de buses ni pasajeros, y
`simulador/` las usa. (Documentos anteriores hablaban de "4 capas": es la misma arquitectura,
contando `estructuras/` y `simulador/` por separado.)

Reglas:
1. **Cada capa solo conoce la de abajo.**
2. **La API no tiene lógica de negocio.** Cada endpoint llama a un método del `Simulador` y
   devuelve su resultado. Si aparece un `if` de negocio en `api/`, está en el lugar equivocado.
3. **Un único `Simulador` en memoria** en el servidor.
4. **El navegador manda el reloj:** el front llama a `POST /api/avanzar` periódicamente.
5. **La animación es del front:** JS interpola la posición del bus entre el estado anterior y el
   nuevo (equivale al `animar_cuadro()` actual). No se usan WebSockets.
6. **Un solo comando para ejecutar:** FastAPI sirve también la carpeta `web/` (evita CORS y dos servidores).
7. `estructuras/` sin dependencias de dominio (no sabe de buses ni pasajeros).

### Endpoints (todos con prefijo `/api/`; ya hechos: estado, reporte, avanzar, pausar, reanudar, agregar-bus, deshacer)
| Método y ruta | Llama a | Estado |
|---|---|---|
| `GET /api/estado` | `Simulador.estado()` | Hecho; se amplía (§3.5.6) |
| `GET /api/reporte` | `Simulador.reporte()` | Hecho |
| `POST /api/avanzar` | `Simulador.avanzar_tick()` y devuelve el estado | Hecho |
| `POST /api/pausar`, `POST /api/reanudar` | `pausar()`, `reanudar()` | Hecho |
| `POST /api/agregar-bus` | `agregar_bus()` | Hecho; **se reemplaza** por `POST /api/atender` |
| `POST /api/atender` | `Simulador.atender()` | Etapa 4 |
| `POST /api/deshacer` | `deshacer()` | Hecho; se adapta al despacho |
| `GET /api/ruta` | Geometría de la ruta (se pide una vez) | Etapa 4 |
| `GET /api/alertas?limite=N` | Las N alertas más urgentes | Etapa 4 |
| `GET /api/esperas?minimo=N` | `Simulador.consultar_esperas(minimo, limite)` | Etapa 4 |
| `GET /api/sector?desde=ID&hasta=ID` | `Simulador.consultar_sector(id_desde, id_hasta)` | Etapa 4 |
| `POST /api/reiniciar` | Crea un `Simulador` nuevo (con un AVL y un montículo nuevos) | Etapa 4 |

## 5. Tecnología

| Parte | Decisión | Motivo |
|---|---|---|
| Lenguaje del motor | Python 3.10+ | Ya lo dominan |
| API | **FastAPI + Uvicorn** | Los diccionarios de `estado()` y `reporte()` pasan a JSON casi sin trabajo |
| Frontend | **HTML + CSS + JavaScript plano** (módulos ES), **sin React** | Sin Node ni compilación; React no aporta a la materia |
| Mapa | Leaflet por CDN (necesita internet) | Zoom y desplazamiento ya resueltos. Revisar la política de uso de los mosaicos de OpenStreetMap |
| Pruebas | pytest | Ya existe |
| Se retira | Pillow | Era para los sprites de Tkinter |

Las versiones exactas de dependencias se fijan **después** de instalarlas (`pip freeze`) y se
verifican en la documentación oficial. No inventar APIs ni funciones: si hay duda, consultar.

## 6. Reglas de trabajo con el asistente de IA

### Qué SÍ hace el asistente (decisión del grupo para esta fase)
- Configurar el proyecto: carpetas, `requirements.txt`, `.gitignore`, README y paso a paso de instalación.
- Montar la **API FastAPI** (explicándola, porque el equipo quiere aprender a configurarla).
- Construir el **frontend** (HTML, CSS, JS): mapa, animación, panel de control, gráficas.
- Ayudar a **integrar** las piezas y a depurar.
- Revisar el código del equipo: errores, casos borde, complejidad (Big O), mejoras.
- Redactar con el equipo la documentación de cada pieza.

### Qué NO hace
- **No implementa las estructuras de datos** (`estructuras/`): las escribe el equipo. El asistente
  puede dar analogías, pistas, pseudocódigo y pruebas sugeridas, y revisar lo que el equipo escriba.
- No usa librerías para sustituir estructuras (`heapq`, `bisect`, `sortedcontainers`, `networkx`, etc.)
  como estructura de fondo. Las librerías sirven para interfaz, aleatoriedad, archivos y pruebas,
  y como apoyo para **validar** las estructuras propias.
- No reescribe el proyecto de una vez: trabaja por piezas pequeñas que el equipo entienda.
- No toma decisiones de alcance sin preguntar. Primero propone el plan y espera aprobación.

### Estilo
- Responder en español, claro y cercano. Explicar cada término nuevo la primera vez.
- Primero la idea (con analogía), luego pistas; el código completo solo cuando se pida,
  comentado línea por línea.
- Si algo excede lo visto en clase, proponer la versión simple y mencionar la avanzada como nota.
- Si una solución es insegura o dudosa, decirlo. Si no se sabe, decirlo.

## 7. Convenciones de código

- Python 3, clases y métodos **en español**, coherentes con lo ya existente.
- Cada estructura con **docstrings**, y cada método indicando su **complejidad**.
- La lógica del simulador **separada de la interfaz**, para probarla sin servidor ni navegador.
- Sin lógica en la API ni en el JS: el JS solo dibuja y manda órdenes.
- Comentarios en el JS y la API pensados para aprender (qué hace cada bloque y por qué).

## 8. Documentación y entregables

Todo en Markdown dentro de `docs/`:
- `explicacion_estructuras.md`: por qué y cómo se usó cada estructura, con su complejidad.
- `supuestos_y_datos_pendientes.md`: cada supuesto del modelo y cada dato real que falta, con su
  valor provisional, su fuente, quién lo define y en qué etapa. Sin cifras inventadas.
- `manual_usuario.md`: actualizado a la versión web.
- `registro_uso_ia.md`: **mantener al día** qué generó la IA y qué hizo el equipo, para calcular
  el porcentaje final. Corregir ahí cualquier descripción que ya no corresponda.
- `descripcion.md`: actualizar al terminar la fase.
- Documento de entrega de la fase (decisiones, fuentes en formato IEEE, interacciones con IA).
- Repositorio en GitHub con README claro, video de máximo 5 minutos y sustentación oral.

Pendientes de documentación detectados en la Fase 1 (aún sin resolver): `explicacion_estructuras.md`
dice "duplica" donde el código usa factor áureo; docstring de `bajar_en` dice O(n²) y es O(n);
`manual_usuario.md` menciona 20 % de prioritarios y el código usa 50 %; `.gitignore` tiene una línea
`.venv/.DS_Store` que probablemente son dos.

## 9. Plan de trabajo: 5 etapas (definido por Nicolás el 27-nov)

Se agota cada etapa antes de pasar a la siguiente. En **cada** etapa se hacen las pruebas con
pytest de las capas 1 y 2; para la capa 3 se evalúa Playwright.

| Etapa | Qué | Capa | Quién | Estado |
|---|---|---|---|---|
| 1 | Implementar de cero, como TDA y con lo visto en clase, cada estructura nueva (montículo, AVL, árbol de segmentos) | 1 | Equipo (IA revisa y prueba) | Lista; ajustes menores si una decisión posterior lo pide |
| 2 | Definir el uso y la aplicación de cada estructura nueva, con justificación, **sin quitar** ninguna estructura lineal de la Fase 1 | 1 | Equipo; la IA opina cuando se le pida | **Usos cerrados el 28-nov** (AVL, montículo y árbol de segmentos; ver §3.4–§3.6) |
| 3 | Implementar ese uso en `simulador/`; el cambio principal se refleja en `simulador.py` | 1 | Equipo / Nicolás en `simulador.py` (IA guía y revisa) | **En curso** (desde el 28-nov) |
| 4 | Configurar la API: todos los GET y POST del alcance, endpoints y enrutamiento | 2 | Nicolás con guía de la IA | Parcial (A1 y A2 hechos con la Fase 1 del simulador) |
| 5 | Interfaz web profesional (HTML, CSS, JS), ajustando el alcance a lo que el equipo imagina | 3 | IA en gran parte, con el equipo | Pendiente (solo esqueleto) |

El cronograma anterior por "Bloques" (17–28 nov) queda como historia en `plan_preparacion.md`.

**Orden de recortes si falta tiempo:** pulido visual y gráficas → funciones extra de la interfaz.
Nunca se sustituye una estructura por una librería.

## 10. Preguntas abiertas

1. ¿Para qué se usa cada estructura nueva y con qué justificación? (etapa 2)
2. ¿Existe servicio directo Portal Américas–Portal Norte y cuáles son sus estaciones?
3. ¿Qué sistema operativo usa cada integrante? (afecta los comandos del paso a paso)
4. ¿Se conserva `app.py` en `legacy/` o se elimina al final?