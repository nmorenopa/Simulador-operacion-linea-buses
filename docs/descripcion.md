# Descripción del proyecto: Simulador de operación de una línea de buses

> Documento técnico y conceptual del proyecto **en su estado actual** (commit `80003fb`, noviembre de 2026).
> Resume qué hace el sistema, cómo está construido, qué estructuras de datos usa y por qué,
> cómo se conectan las piezas y qué diferencias hay entre el código y la documentación existente.

---

## Índice

1. [Visión general](#1-visión-general)
2. [Tecnologías y requisitos](#2-tecnologías-y-requisitos)
3. [Organización del repositorio](#3-organización-del-repositorio)
4. [Arquitectura por capas](#4-arquitectura-por-capas)
5. [Capa 1 — Estructuras de datos (`estructuras/`)](#5-capa-1--estructuras-de-datos-estructuras)
6. [Capa 2 — Modelo del dominio (`simulador/`)](#6-capa-2--modelo-del-dominio-simulador)
7. [El motor: un minuto de simulación](#7-el-motor-un-minuto-de-simulación)
8. [Capa 3 — Interfaz gráfica (`app.py`)](#8-capa-3--interfaz-gráfica-apppy)
9. [Mapa de estructuras: dónde y por qué](#9-mapa-de-estructuras-dónde-y-por-qué)
10. [Resumen de complejidades](#10-resumen-de-complejidades)
11. [Pruebas automáticas (`tests/`)](#11-pruebas-automáticas-tests)
12. [Documentación existente (`docs/`)](#12-documentación-existente-docs)
13. [Observaciones y diferencias detectadas](#13-observaciones-y-diferencias-detectadas)
14. [Limitaciones actuales](#14-limitaciones-actuales)

---

## 1. Visión general

El proyecto es un **simulador visual de una línea de buses** desarrollado para la asignatura de
**Estructuras de Datos**. Una flota de buses recorre un **circuito cerrado de 8 paradas** en sentido
horario. Minuto a minuto:

- llegan pasajeros a las paradas (de forma aleatoria, con una semilla fija para que sea repetible);
- cada pasajero tiene un **destino** distinto de su parada de origen y puede ser **prioritario**
  (adulto mayor, movilidad reducida…) o **normal**;
- los buses bajan a quienes llegaron a su destino, suben a los que esperan (primero los prioritarios
  y, entre iguales, por orden de llegada) respetando su **capacidad**, y avanzan a la siguiente parada.

El usuario actúa como **operador**: inicia, pausa y reanuda la simulación, **agrega buses**,
**deshace** sus últimas acciones, la **termina** para ver estadísticas en gráficas y la **reinicia**
con otra tasa de llegada y otra capacidad.

El objetivo académico es que **cada necesidad del problema se resuelva con una estructura de datos
implementada a mano** (sin usar `list`, `deque`, `heapq` ni similares como estructura de fondo):
arreglo dinámico, pila, cola, cola circular y cola con prioridad, todas sobre un único `Nodo`
de lista enlazada (salvo el arreglo dinámico).

---

## 2. Tecnologías y requisitos

| Elemento | Detalle |
|---|---|
| Lenguaje | Python 3.10 o superior (usa anotaciones `X \| None`) |
| Interfaz gráfica | **Tkinter** (incluido con Python): un único `Canvas` para el mapa y una ventana `Toplevel` para las estadísticas |
| Imágenes | **Pillow** (`PIL.Image`, `PIL.ImageTk`) para cargar PNG |
| Pruebas | **pytest** |
| Dependencias (`requirements.txt`) | `pytest==9.1.1`, `pillow==12.3.0` |
| Aleatoriedad | `random.Random` con semilla (instancia propia, no el generador global) |

Comandos principales:

```bash
python -m venv .venv
source .venv/Scripts/activate      # Windows (Git Bash)
pip install -r requirements.txt
python app.py                      # Ejecutar la aplicación
pytest                             # Ejecutar las pruebas
```

---

## 3. Organización del repositorio

```
Simulador-operacion-linea-buses/
├── app.py                      # Interfaz gráfica Tkinter (≈1460 líneas)
├── requirements.txt            # pytest, pillow
├── README.md                   # Instalación, ejecución y pruebas (breve)
├── CLAUDE.md                   # Reglas de trabajo con el asistente de IA
├── estructuras/                # Estructuras de datos implementadas a mano
│   ├── nodo.py                 # Nodo de lista enlazada simple
│   ├── arreglo_dinamico.py     # Arreglo que crece por el número áureo
│   ├── pila.py                 # Pila LIFO enlazada
│   ├── cola.py                 # Cola FIFO enlazada
│   ├── cola_circular.py        # Cola FIFO con lista enlazada circular
│   └── cola_prioridad.py       # Cola con prioridad: arreglo de colas
├── simulador/                  # Modelo del dominio y motor (sin interfaz)
│   ├── pasajero.py             # Pasajero + constantes de prioridad
│   ├── parada.py               # Parada con su fila de prioridad
│   ├── bus.py                  # Bus con su ruta circular y sus pasajeros
│   └── simulador.py            # Reloj, motor, acciones del operador, estado y reporte
├── tests/                      # 10 archivos de pruebas pytest (132 casos)
├── imagenes/
│   ├── FONDO.png               # Mapa de 900x600 px con el circuito
│   └── bus/{norte,sur,este,oeste}.png   # Sprites del bus de 60x60 px
└── docs/
    ├── explicacion_estructuras.md   # Explicación didáctica de las estructuras
    ├── manual_usuario.md            # Manual de uso de la aplicación
    ├── registro_uso_ia.md           # Registro del uso de IA en el proyecto
    └── descripcion.md               # Este documento
```

---

## 4. Arquitectura por capas

El proyecto sigue una separación estricta en **tres capas**, donde cada una solo depende de la de abajo:

```
┌─────────────────────────────────────────────────────────────┐
│ 3. INTERFAZ  (app.py)                                       │
│    Dibuja, anima y recibe clics. No contiene lógica.        │
│    Lee:    estado(), reporte(), serie_esperando,            │
│            serie_ocupacion                                  │
│    Llama:  avanzar_tick(), pausar(), reanudar(),            │
│            agregar_bus(), deshacer()                        │
├─────────────────────────────────────────────────────────────┤
│ 2. DOMINIO  (simulador/)                                    │
│    Simulador ─ usa ─> Bus, Parada, Pasajero                 │
│    No dibuja ni imprime: todo se puede probar sin ventana.  │
├─────────────────────────────────────────────────────────────┤
│ 1. ESTRUCTURAS  (estructuras/)                              │
│    Nodo, ArregloDinamico, Pila, Cola, ColaCircular,         │
│    ColaPrioridad. No saben nada de buses ni pasajeros.      │
└─────────────────────────────────────────────────────────────┘
```

**Por qué esta separación:**

- **Capa 1** es genérica y reutilizable: una `Cola` sirve igual para pasajeros que para operaciones de
  la interfaz (de hecho se usa en ambos lugares).
- **Capa 2** concentra toda la lógica de negocio. Como no depende de Tkinter, las pruebas automáticas
  pueden ejecutar cientos de minutos de simulación en milisegundos.
- **Capa 3** es reemplazable: el historial del repositorio muestra que la interfaz pasó de Streamlit a
  Tkinter sin tocar el modelo.

Dependencias entre módulos:

```
app.py ──> simulador.simulador ──> simulador.bus ──────> estructuras.arreglo_dinamico
   │               │                    │           └──> estructuras.cola_circular ──> nodo
   │               │                    └──> simulador.pasajero
   │               ├──> simulador.parada ──> estructuras.cola_prioridad ──> cola ──> nodo
   │               │                                                  └──> arreglo_dinamico
   │               ├──> estructuras.pila ──> nodo
   │               ├──> estructuras.arreglo_dinamico
   │               └──> estructuras.cola_circular
   └──> estructuras.cola   (Cola de operaciones pendientes de la interfaz)
```

---

## 5. Capa 1 — Estructuras de datos (`estructuras/`)

Todas las estructuras enlazadas guardan un **contador interno `_tamano`** para que consultar el
tamaño sea O(1) sin recorrer la lista. Las operaciones sobre estructuras vacías devuelven `None`
(colas y pila) o lanzan `IndexError` (arreglo dinámico).

### 5.1 `Nodo` (`nodo.py`)

- **Concepto:** la pieza mínima de una lista enlazada simple: un `dato` y una referencia `siguiente`.
- **Uso:** es el **único nodo del proyecto**; lo comparten `Pila`, `Cola`, `ColaCircular` y,
  indirectamente, `ColaPrioridad` (a través de las `Cola` de sus niveles).

### 5.2 `ArregloDinamico` (`arreglo_dinamico.py`)

- **Concepto:** bloque de posiciones consecutivas (`self.datos`, una lista de tamaño fijo
  `capacidad` rellena con `None`) más un contador `n` de elementos reales. Da **acceso por índice en O(1)**.
- **Crecimiento:** empieza con `capacidadinicial = 1` y, cuando se llena, crece a
  `int(capacidad × 1.618) + 1` (factor **número áureo**). Secuencia de capacidades:
  `1 → 2 → 4 → 7 → 12 → 20 → …`. Copiar al crecer es O(n), pero como ocurre cada vez con menos
  frecuencia, `agregaralfinal` es **O(1) amortizado**.
- **Decisión de diseño clave — operaciones O(1) que NO conservan el orden:**
  - `insertar(k, valor)`: en vez de correr elementos a la derecha, **manda el elemento de la posición k
    al final** y pone el nuevo en k.
  - `borrarposicion(k)`: en vez de correr elementos a la izquierda, **trae el último elemento a la
    posición k** y reduce `n`.

  Esto es válido porque en el único lugar donde se borra en medio (pasajeros a bordo de un bus) el orden
  no importa.
- **Operaciones:** `longitud`, `vacio`, `posicion`, `cambiarposicion` (O(1));
  `contiene`, `buscar`, `contar`, `mostrar` (O(n)); `agrandar` (O(n));
  `agregaralfinal` (O(1) amortizado); `insertar`, `borrarposicion`, `borraralfinal` (O(1)).
- `mostrar()` devuelve una **copia** en una lista de Python; así la interfaz puede leer los datos sin
  tocar la estructura real.

### 5.3 `Pila` (`pila.py`) — LIFO

- **Concepto:** el último en entrar es el primero en salir. Solo se guarda el `tope`.
- **Operaciones (todas O(1) salvo `mostrar`):** `apilar`, `desapilar`, `ver_tope`, `esta_vacia`,
  `longitud`; `mostrar` imprime de tope a fondo (O(n)).

### 5.4 `Cola` (`cola.py`) — FIFO

- **Concepto:** se agrega por el `final` y se saca por el `frente`. Guardar los dos extremos hace que
  agregar y sacar sean O(1).
- **Operaciones:** `agregar`, `borrar`, `ver_frente`, `esta_vacia`, `longitud` (O(1)); `mostrar` (O(n)).
- Al sacar el último elemento también se reinicia `final = None`, para no dejar una referencia colgante.

### 5.5 `ColaCircular` (`cola_circular.py`)

- **Concepto:** cola FIFO sobre una lista enlazada **circular**.
  **Invariante:** si no está vacía, `ultimo.siguiente` es `cabeza`.
- **Operación característica — `siguiente()` (rotar):** la cabeza pasa a ser el último y la cabeza
  avanza un nodo. **No crea ni borra nodos**, solo mueve dos referencias: O(1). Así se recorre una
  secuencia **infinitamente** sin reconstruirla.
- **Operaciones:** `encolar`, `desencolar`, `frente`, `siguiente`, `tamano`, `esta_vacia` (todas O(1)).

### 5.6 `ColaPrioridad` (`cola_prioridad.py`)

- **Concepto:** cola en la que sale primero el elemento de **mayor prioridad** y, entre iguales, el que
  llegó antes (estable).
- **Implementación:** un **`ArregloDinamico` de `Cola`**, una cola por nivel de prioridad
  (técnica de *colas por niveles* o *bucket queue*).
  **Convención: MENOR número = MAYOR prioridad** (el nivel 0 sale primero).
- **Operaciones:**
  - `encolar(dato, prioridad)`: va directo a la cola de su nivel → **O(1)**. Valida el rango de
    prioridad (y si falla no deja rastro).
  - `desencolar()` y `frente()`: buscan el primer nivel no vacío → **O(k)**, con k = número de niveles.
    Como en el proyecto k = 2 y es fijo, en la práctica es O(1).
  - `tamano`, `esta_vacia` (O(1)).
- **Por qué no un *heap*:** con pocos niveles fijos, el arreglo de colas es más simple de explicar,
  garantiza estabilidad (FIFO dentro de cada nivel) de forma natural y encolar es O(1) en vez de O(log n).

---

## 6. Capa 2 — Modelo del dominio (`simulador/`)

### 6.1 `Pasajero` (`pasajero.py`)

Es casi solo datos. Define las constantes globales de prioridad:

| Constante | Valor | Significado |
|---|---|---|
| `PRIORIDAD_ALTA` | `0` | Prioritario (sale primero de la cola) |
| `PRIORIDAD_NORMAL` | `1` | Normal |
| `NIVELES_PRIORIDAD` | `2` | Niveles de la `ColaPrioridad` de cada parada |

Atributos: `id`, `origen`, `destino`, `prioridad`, `minuto_llegada`, `minuto_abordaje` (`None` hasta
que sube). Métodos: `es_prioritario()`, `tiempo_espera()` (= abordaje − llegada, o `None`), `__repr__`.
Valida que `origen != destino` y que la prioridad sea una de las dos constantes.

### 6.2 `Parada` (`parada.py`)

Representa una parada y **su fila**, que es una `ColaPrioridad(NIVELES_PRIORIDAD)`.

- **Idea conceptual clave:** el pasajero se **clasifica por prioridad en el momento en que llega**
  (`recibir`), no cuando llega el bus. Por eso, al abordar, basta con desencolar en orden.
- `recibir(pasajero)`: encola según su prioridad y actualiza contadores. O(1).
- `abordar(bus, minuto)`: mientras el bus tenga cupo y haya gente, desencola, anota el minuto de
  abordaje, sube al pasajero y acumula su espera. Los que no caben **se quedan en la fila sin perder
  su lugar**. O(m) con m = pasajeros que suben.
- `esperando()`: tamaño de la fila, O(1).
- Contadores que alimentan el reporte y la interfaz: `total_llegados`, `total_abordados`,
  `suma_espera` (para la espera promedio) y `prioritarios_esperando` (para que la interfaz pinte los
  puntos azules **sin recorrer la cola**).
- Valida que `tasa_llegada` esté entre 0 y 1.

### 6.3 `Bus` (`bus.py`)

- `ruta`: **su propia `ColaCircular`** con las paradas (las mismas referencias a objetos `Parada` que
  los demás buses). **El frente de la cola es la parada donde está el bus** y avanzar es rotar la cola.
  Cada bus tiene su propia instancia para poder estar en una posición distinta del circuito.
- `pasajeros`: `ArregloDinamico` de los que van a bordo.
- `parada_actual`, `capacidad_maxima`, `total_transportados`.
- Métodos: `cantidad_pasajeros`, `cupos_libres`, `ocupacion` (fracción 0–1), `subir` (lanza
  `ValueError` si está lleno), `bajar_en(id_parada)` y `avanzar()` (rota la ruta, O(1)).
- **`bajar_en`** recorre el arreglo **de atrás hacia adelante**: como `borrarposicion(i)` trae el
  último elemento a la posición i, al ir hacia atrás ese elemento ya fue revisado, y así nadie se
  salta ni se revisa dos veces.

### 6.4 `Simulador` (`simulador.py`)

Es el **director**: tiene el reloj, crea y coordina todo, guarda estadísticas y expone una API para la
interfaz. **No dibuja ni imprime nada.**

**Parámetros del constructor** (todos validados, lanzan `ValueError` si no tienen sentido):

| Parámetro | Restricción | Significado |
|---|---|---|
| `numero_paradas` | ≥ 2 | Paradas del circuito |
| `numero_buses` | ≥ 1 | Buses al iniciar |
| `capacidad_bus` | ≥ 1 | Capacidad de cada bus (también de los agregados después) |
| `tasa_llegada` | 0 a 1 | Probabilidad de llegada por sorteo |
| `probabilidad_prioritario` | 0 a 1 | Probabilidad de que un pasajero nuevo sea prioritario |
| `semilla` | opcional | Semilla del `Random` (misma semilla ⇒ misma simulación) |
| `intentos_llegada` | entero ≥ 1 | Sorteos por parada y minuto (máximo de llegadas por minuto) |

**Atributos principales y su estructura:**

| Atributo | Estructura | Contenido |
|---|---|---|
| `paradas` | `ArregloDinamico` | Objetos `Parada`; el id de cada una es su índice |
| `buses` | `ArregloDinamico` | Objetos `Bus` |
| `historial` | `Pila` | Acciones del operador para deshacer |
| `serie_esperando` | `ArregloDinamico` | Una muestra por minuto: total de pasajeros esperando |
| `serie_ocupacion` | `ArregloDinamico` | Una muestra por minuto: ocupación promedio de la flota |
| `eventos` | `ArregloDinamico` | Lo ocurrido en cada bus en el último minuto (para animar) |
| `minuto`, `en_pausa` | escalares | Reloj y estado de pausa |

**Reparto inicial de los buses:** el bus k arranca rotando su ruta `(k × P) // B` veces.
Con 8 paradas y 5 buses quedan en P1, P2, P4, P5 y P7, repartidos de forma pareja.

**Acciones del operador** (todas registradas en la `Pila` `historial` como cadenas
`"agregar_bus"`, `"pausar"`, `"reanudar"`):

| Método | Efecto | Al deshacer |
|---|---|---|
| `agregar_bus()` | Crea un bus en la **parada con más gente esperando** (la primera si hay empate) | Se quita el último bus, **solo si va vacío**; si lleva pasajeros la acción se conserva en la pila y se informa |
| `pausar()` | Pone `en_pausa = True` (si ya estaba en pausa no hace nada ni apila) | Reanuda |
| `reanudar()` | Pone `en_pausa = False` (si no estaba en pausa no hace nada) | Vuelve a pausar |
| `deshacer()` | Mira el **tope** de la pila, revierte y desapila | Devuelve un mensaje de texto, o `None` si la pila está vacía |

**API de lectura para la interfaz:**

- `estado()` → diccionario con `minuto`, `en_pausa`, `paradas` (id, nombre, esperando, prioritarios),
  `buses` (id, parada, pasajeros, capacidad, ocupación), `eventos`, `historial` (tamaño de la pila) y
  `ultima_accion` (tope de la pila, sin sacarlo). Usa listas y diccionarios de Python **solo como
  formato de entrega**; el estado real vive en las estructuras propias. O(P + B).
- `reporte()` → `minuto`, `pasajeros_generados`, `pasajeros_abordados`, `pasajeros_esperando`,
  `espera_promedio` (min), `ocupacion_promedio` (0–1) y `buses`. Si no hay datos, los promedios valen
  `0.0` (evita dividir entre cero). O(P + T), con T minutos simulados.

---

## 7. El motor: un minuto de simulación

`avanzar_tick()` ejecuta un minuto. Si está en pausa solo vacía `eventos` y regresa.

```
avanzar_tick()
│
├─ 1. eventos = ArregloDinamico() nuevo (los eventos son solo del minuto actual)
│
├─ 2. _generar_llegadas()
│      para cada parada, K = intentos_llegada sorteos:
│        si random() < tasa_llegada:
│          destino  = randrange(P-1); si destino >= origen: destino += 1
│                     (uniforme entre las OTRAS paradas, nunca el origen)
│          prioridad = ALTA si random() < probabilidad_prioritario, si no NORMAL
│          parada.recibir(Pasajero(...))           → ColaPrioridad.encolar  O(1)
│
├─ 3. para cada bus (en orden de la flota):
│        parada   = bus.parada_actual
│        bajaron  = bus.bajar_en(parada.id)        → primero BAJAN (libera cupo)
│        (se miden esperando/prioritarios/cupos ANTES de abordar)
│        subieron = parada.abordar(bus, minuto)    → luego SUBEN (prioridad + FIFO)
│        bus.avanzar()                             → ColaCircular.siguiente()  O(1)
│        eventos.agregaralfinal({bus, parada, bajaron, subieron, ..., siguiente_parada})
│
├─ 4. _registrar_estadisticas()   → una muestra en serie_esperando y serie_ocupacion
│
└─ 5. minuto += 1
```

Propiedades que garantiza el diseño (y que las pruebas verifican):

- **Conservación:** ningún pasajero se pierde ni se inventa (generados = esperando + a bordo + entregados).
- **Capacidad:** un bus nunca supera su capacidad.
- **Prioridad:** si en una parada hay prioritarios y normales, suben primero los prioritarios.
- **Equidad:** entre pasajeros del mismo tipo sube primero el que llegó antes.
- **Reproducibilidad:** misma semilla y mismos parámetros ⇒ misma simulación. Con `intentos_llegada = 1`
  las llamadas al generador son las mismas que en versiones anteriores.
- Cada bus avanza **exactamente una parada por minuto**.

---

## 8. Capa 3 — Interfaz gráfica (`app.py`)

### 8.1 Parámetros de la demostración

| Constante | Valor | Comentario |
|---|---|---|
| `NUMERO_PARADAS` | 8 | Fijo por el dibujo del fondo |
| `NUMERO_BUSES` | 5 | Buses al iniciar/reiniciar |
| `CAPACIDAD_BUS` | 10 | Editable desde la barra |
| `TASA_LLEGADA` | 0.5 | Editable desde la barra |
| `PROBABILIDAD_PRIORITARIO` | 0.5 | Solo en código |
| `INTENTOS_LLEGADA` | 3 | De 0 a 3 llegadas por parada y minuto |
| `SEMILLA` | 42 | Simulación repetible |
| `MAX_BUSES` | 10 | Tope de la interfaz (el `Simulador` no tiene tope) |
| `MOSTRAR_DEPURACION` | `True` | Dibuja la grilla, índices de celdas, paradas en rojo y esquinas E1–E4 |
| `MOSTRAR_PLACAS` | `False` | Placas P1..P8 (el fondo ya trae letreros) |

### 8.2 Geometría del mapa

- El fondo `FONDO.png` (900 × 600 px) se trata como una **grilla de 15 × 10 celdas de 60 px**.
- `construir_ruta()` arma la lista `RUTA` con las **32 celdas** del circuito en sentido horario
  (11 arriba + 6 derecha + 10 abajo + 5 izquierda).
- `PARADAS = [1, 5, 9, 13, 17, 21, 25, 29]`: cada parada es un índice dentro de `RUTA`,
  **una cada 4 celdas** (32 / 8), así todas quedan a la misma distancia.
- `punto_en_ruta(distancia)`: convierte una distancia en píxeles a lo largo del circuito en un punto
  `(x, y)` y una dirección (`norte/sur/este/oeste`), usando **módulo** sobre el largo total
  (32 × 60 px) e **interpolación lineal** entre centros de celdas. Así las vueltas y las esquinas
  funcionan sin casos especiales.
- `direccion_entre()` elige el sprite según hacia dónde se mueve el bus.
- Si varios buses coinciden en una parada, `desplazamientos_buses()` los separa 60 px a lo largo de la
  vía, centrados en la parada.

### 8.3 Dibujo

- **Un único `Canvas`** con: fondo, marcas de depuración, marcador de minuto, leyenda, pasajeros y buses.
- **Referencias a imágenes:** el fondo se guarda en la lista `imagenes_guardadas` y los sprites en el
  diccionario `sprites_bus`, ambos a nivel de módulo, para que el recolector de basura no borre los
  `PhotoImage` (si no, desaparecen de la pantalla).
- **Etiquetas (tags) del Canvas** para manipular grupos de objetos: `"bus"`, `"bus_<id>"`,
  `"sprite_<id>"`, `"contador_<id>"`, `"pasajero"`, `"texto_minuto"`. Ejemplo:
  `canvas.delete("pasajero")` borra todos los puntos antes de redibujarlos.
- **Pasajeros esperando:** un punto por pasajero sobre la acera (azul = prioritario, gris = normal),
  máximo 12 por parada y luego `+N`. `puntos_de_parada()` calcula posiciones **sin dibujar**
  (separación entre cálculo y dibujo).
- **Contador `c/n`** sobre cada bus (pasajeros a bordo / capacidad).

### 8.4 Animación (sin `time.sleep`)

`avanzar_tick()` del modelo cambia el estado **de golpe**; la interfaz anima el paso entre el estado de
antes y el de después:

1. Se toma `estado_antes`, se llama `simulador.avanzar_tick()` y se toma `estado_despues`.
2. `calcular_trayectos()` obtiene, para cada evento, desde qué distancia sale el bus y cuántos píxeles
   recorre (siempre hacia adelante gracias al módulo: de P8 a P1 son 4 celdas, no −28).
3. `animar_cuadro()` mueve todos los sprites a la fracción correspondiente y se reprograma con
   `canvas.after(16 ms)` durante ≈ 38 cuadros (600 ms, ~60 fps). Los objetos **se mueven**
   (`coords`, `move`, `itemconfigure`), no se borran y recrean, para evitar parpadeo.
4. En el último cuadro llama a `terminar_tick()`, que dibuja filas, contadores y minuto nuevos.

**Por qué `after()` y no `time.sleep()`:** Tkinter dibuja y atiende clics en su `mainloop`. Un `sleep`
congelaría la ventana; con `after()` cada cuadro es una llamada corta que devuelve el control a Tkinter.

### 8.5 Bucle automático y operaciones pendientes

```
Play ─> ciclo() ─> avanzar_un_tick() ─> animación (≈38 after) ─> terminar_tick()
          ^                                                         │
          └──── after(200 ms)  o  after(100 ms) si está en pausa ───┘
```

- La clase `InterfazSimulador` guarda el estado de la interfaz: `iniciado`, `terminada`, `animando`,
  `id_ciclo` (para cancelar el `after` pendiente con `after_cancel`), etc.
- **Cola de operaciones pendientes:** cada clic (Play/Pausa, Agregar bus, Deshacer, Terminar, Aplicar)
  se mete como tupla en una `Cola` propia (`estructuras/cola.py`). Si no hay animación se ejecuta de
  inmediato; si la hay, se ejecutan **todas en orden FIFO** al terminar el movimiento. Así nunca se
  mezcla un cambio de estado con una animación a medias.
- **Primer Play** no llama a `reanudar()` (el simulador no estaba en pausa), para no meter en la pila
  una acción que no ocurrió. **Terminar** tampoco llama a `pausar()`, para que Deshacer no pueda
  "revivir" una simulación terminada; solo detiene el bucle de la interfaz.
- **Aplicar y reiniciar** valida los campos (`validar_parametros`, acepta coma decimal) y crea un
  **`Simulador` nuevo**, en vez de modificar atributos del anterior desde fuera.
- La barra muestra el **estado de la `Pila`**: `Historial: N acciones - última: X`, leído de `estado()`.

### 8.6 Ventana de estadísticas

Al pulsar **Terminar** se abre un `tk.Toplevel` con su propio `Canvas` (900 × 640 px). Las gráficas se
dibujan **a mano** con primitivas del Canvas (rectángulos, líneas, polígonos, arcos, textos), sin
librerías de gráficos, para poder explicarlas línea a línea:

| Parte | Fuente de datos |
|---|---|
| Encabezado (minuto, tasa, capacidad) | `reporte()` + parámetros de la interfaz |
| 6 tarjetas: generados, abordaron, esperando, espera promedio, ocupación promedio, buses | `reporte()` |
| Gráfica de línea "Pasajeros esperando" con área rellena | `serie_esperando.mostrar()` |
| Gráfica de línea "Ocupación de la flota" (0–100 %) con promedio punteado | `serie_ocupacion.mostrar()` |
| Barras apiladas por parada (prioritarios / normales) | `estado()["paradas"]` |
| Anillo "¿Qué pasó con los generados?" (abordaron vs. esperando) | `reporte()` |

`paso_escala()` elige divisiones "redondas" (1, 2, 5, 10, 20, 50…) para el eje Y.

---

## 9. Mapa de estructuras: dónde y por qué

| Necesidad del problema | Estructura | Dónde | Justificación |
|---|---|---|---|
| Pasajeros a bordo; en cada parada baja **cualquiera** según su destino | `ArregloDinamico` | `Bus.pasajeros` | Acceso por índice y borrado en cualquier posición (O(1) con intercambio). Una cola o pila solo permiten sacar por un extremo |
| Paradas y flota, recorridas por índice | `ArregloDinamico` | `Simulador.paradas`, `Simulador.buses` | Acceso O(1) por id; agregar bus al final O(1) amortizado; deshacer quita el último |
| Series de estadísticas por minuto | `ArregloDinamico` | `serie_esperando`, `serie_ocupacion` | Crecen sin límite conocido y se recorren en orden |
| Niveles de la cola con prioridad | `ArregloDinamico` de `Cola` | `ColaPrioridad.niveles` | Acceso directo al nivel por su número |
| **Deshacer** la última acción del operador | `Pila` (LIFO) | `Simulador.historial` | Solo se deshace lo último que se hizo, en orden inverso |
| Fila de una parada por orden de llegada | `Cola` (FIFO) | Dentro de cada nivel de `ColaPrioridad` | Se atiende por orden de llegada |
| Orden de abordaje: prioritarios primero | `ColaPrioridad` | `Parada.fila` | Sale el de mayor prioridad y, entre iguales, el que llegó antes |
| Ruta que se repite sin fin (P1 → … → P8 → P1) | `ColaCircular` | `Bus.ruta` (una por bus) | Rotar es O(1) y nunca se acaba |
| Clics del operador durante una animación | `Cola` (FIFO) | `InterfazSimulador.pendientes` | Ejecutar las operaciones en el orden en que se pidieron |

---

## 10. Resumen de complejidades

Notación: n = elementos de la estructura, k = niveles de prioridad (2), P = paradas, B = buses,
K = intentos de llegada, m = pasajeros que suben, T = minutos simulados.

| Operación | Complejidad |
|---|---|
| `ArregloDinamico.agregaralfinal` | O(1) amortizado |
| `ArregloDinamico.posicion / insertar / borrarposicion / borraralfinal` | O(1) |
| `ArregloDinamico.buscar / contiene / contar / mostrar / agrandar` | O(n) |
| `Pila.apilar / desapilar / ver_tope` | O(1) |
| `Cola.agregar / borrar / ver_frente` | O(1) |
| `ColaCircular.encolar / desencolar / siguiente` | O(1) |
| `ColaPrioridad.encolar` | O(1) |
| `ColaPrioridad.desencolar / frente` | O(k) |
| `Parada.recibir` | O(1) |
| `Parada.abordar` | O(m·k) = O(m) con k fijo |
| `Bus.bajar_en` | O(n) (cada borrado es O(1)) |
| `Bus.avanzar` | O(1) |
| `Simulador.__init__` | O(P + B·P) |
| `Simulador.avanzar_tick` | O(P·K + Σ pasajeros a bordo + Σ que suben + B) |
| `Simulador.agregar_bus` | O(P + B) |
| `Simulador.deshacer / pausar / reanudar` | O(1) |
| `Simulador.estado` | O(P + B) |
| `Simulador.reporte` | O(P + T) |

---

## 11. Pruebas automáticas (`tests/`)

- **10 archivos, 113 funciones de prueba, 132 casos** (algunas están parametrizadas).
  Estado actual: **132 aprobadas** (`pytest -q`, en ≈ 0,4 s).
- No abren ventanas: prueban las capas 1 y 2.

| Archivo | Funciones | Qué verifica |
|---|---|---|
| `test_nodo.py` | 2 | Creación y enlace de nodos |
| `test_arreglo_dinamico.py` | 9 | Crecimiento áureo (1→2→4→7→12), índices inválidos, `insertar`/`borrarposicion` O(1) |
| `test_pila.py` | 4 | Orden LIFO, vacía |
| `test_cola.py` | 4 | Orden FIFO, vacía |
| `test_cola_circular.py` | 11 | Invariante circular, rotación, encolar/desencolar |
| `test_cola_prioridad.py` | 22 | Prioridad, estabilidad FIFO, niveles vacíos, validaciones y comparación contra una referencia ordenada con datos al azar |
| `test_pasajero.py` | 7 | Validaciones, prioridad, tiempo de espera |
| `test_parada.py` | 8 | Fila con prioridad, abordaje con cupo, contadores |
| `test_bus.py` | 7 | Subir, bajar por destino, capacidad, avanzar |
| `test_simulador.py` | 39 | Reparto inicial, llegadas, semillas, conservación de pasajeros, capacidad, pausa, deshacer, `estado()`, `reporte()`, eventos |

Según `docs/registro_uso_ia.md`, las pruebas fueron generadas con IA y revisadas por el equipo.

---

## 12. Documentación existente (`docs/`)

| Archivo | Contenido |
|---|---|
| `explicacion_estructuras.md` | Explicación didáctica de cada estructura: idea, uso, justificación, analogía y cómo se ve en la demo |
| `manual_usuario.md` | Manual completo: requisitos, instalación, pantalla, controles, funcionamiento, guía paso a paso, mensajes, ajustes, problemas frecuentes y limitaciones |
| `registro_uso_ia.md` | Porcentaje de uso de IA por actividad (pruebas 100 %, animaciones 70 %, documentación 30 %) y responsables de cada estructura y clase |
| `descripcion.md` | Este documento: descripción técnica y conceptual integral |

---

## 13. Observaciones y diferencias detectadas

Al contrastar el código con la documentación se encontraron estas diferencias. **No se modificó ningún
archivo de código**; se dejan anotadas para que el equipo decida si corregir la documentación o el código.

| # | Dónde | Qué dice | Qué hace el código |
|---|---|---|---|
| 1 | `explicacion_estructuras.md` §1.1 | El arreglo dinámico **duplica** su capacidad (×2) | Crece por el **número áureo**: `int(capacidad × 1.618) + 1`, empezando en 1 |
| 2 | `explicacion_estructuras.md` §1.1 | `bajar_en` va al revés porque "los demás se correrían" | `borrarposicion` no corre elementos: trae el último al hueco. Ir al revés sigue siendo necesario, pero porque el elemento traído ya fue revisado |
| 3 | `explicacion_estructuras.md` | Dos secciones numeradas **1.4** (cola con prioridad y cola circular) | — (la segunda debería ser 1.5) |
| 4 | `manual_usuario.md` §6.1 y §9 | Probabilidad de prioritario **20 %** / `0.2` | `PROBABILIDAD_PRIORITARIO = 0.5` en `app.py` |
| 5 | `simulador/bus.py`, docstring de `bajar_en` | O(n²) porque "cada borrado desplaza elementos" | Cada borrado es O(1), así que `bajar_en` es **O(n)** |
| 6 | `simulador/parada.py`, docstring de la clase | "La Parada no importa Bus" | Sí lo importa (`from simulador.bus import Bus`), aunque solo usa `cupos_libres()` y `subir()` |
| 7 | `estructuras/arreglo_dinamico.py` | — | `import random` no se usa |
| 8 | `app.py`, docstring del módulo | "FASE 3" | Ya incluye estadísticas, reinicio y deshacer (fases posteriores) |
| 9 | `app.py` | `MOSTRAR_DEPURACION = True` | La demo muestra la grilla verde, índices y bordes rojos; para presentar puede ponerse en `False` |
| 10 | `CLAUDE.md` | La interfaz solo lee `estado()` y `reporte()` | La ventana de estadísticas también lee `serie_esperando` y `serie_ocupacion` (con `mostrar()`, que devuelve una copia y no modifica el simulador) |
| 11 | `.gitignore` | Línea `.venv/.DS_Store` | Probablemente debían ser dos líneas (`.venv/` y `.DS_Store`). Hoy `.venv` no se sube porque el propio entorno virtual trae su `.gitignore` |
| 12 | `README.md` | Instrucciones mínimas | Podría enlazar al manual y a este documento |

---

## 14. Limitaciones actuales

- Circuito y número de paradas (8) **fijos**, atados al dibujo de `FONDO.png`.
- Ventana de tamaño fijo (mapa de 900 × 600 px).
- Desde la interfaz solo se cambian la tasa de llegada y la capacidad; el resto de parámetros está en
  constantes de `app.py`.
- Todos los buses tienen la misma capacidad y recorren la misma ruta en el mismo sentido.
- Las estadísticas solo se ven al **terminar**; no se actualizan en vivo ni se pueden exportar.
- Una simulación terminada no se puede continuar, y nada se guarda al cerrar la aplicación.
- Deshacer solo cubre acciones del operador (agregar bus, pausar, reanudar), no el avance del tiempo
  ni el reinicio; un bus agregado solo se puede quitar si va vacío.
- La interfaz limita la flota a 10 buses; el `Simulador` no tiene tope.
