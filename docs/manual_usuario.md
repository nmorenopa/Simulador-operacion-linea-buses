# Manual de usuario — Simulador de operación de una línea de buses

## 1. ¿Qué es esta aplicación?

Es un simulador visual de una línea de buses que recorre un circuito cerrado con
**8 paradas**. Minuto a minuto llegan pasajeros a las paradas, los buses los recogen
(los **prioritarios** primero), los llevan a su destino y siguen dando vueltas.

El usuario actúa como **operador** de la línea: puede iniciar y pausar la simulación,
agregar buses, deshacer sus últimas acciones y reiniciar con otros valores de tasa de
llegada y capacidad de los buses.

---

## 2. Requisitos

| Requisito | Detalle |
|---|---|
| Python | 3.10 o superior (con Tkinter, que viene incluido en el instalador oficial de Windows) |
| Librerías | `pillow` (imágenes) y `pytest` (pruebas), listadas en `requirements.txt` |
| Pantalla | Al menos 900 × 700 px libres (la ventana no se puede cambiar de tamaño) |

---

## 3. Instalación

Desde la carpeta del proyecto, en una terminal (Git Bash en Windows):

```bash
python -m venv .venv
source .venv/Scripts/activate      # En PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 4. Cómo ejecutar

```bash
python app.py
```

Se abre la ventana **"Simulador de buses"**. Al abrirla la simulación **no corre
todavía**: se ven los buses detenidos en sus paradas iniciales y el mensaje
*"Pulse Play para empezar"*.

---

## 5. La pantalla

La ventana tiene dos zonas: el **mapa** (arriba, 900 × 600 px) y la **barra de
controles** (abajo).

```
┌──────────────────────────────────────────────────────────┐
│ [Minuto: 12]                                             │
│ [● Prioritario]                                          │
│ [● Normal     ]        ●●●●○○○  (pasajeros esperando)    │
│                ┌──────────────────────────┐              │
│                │  🚌 8/20 →               │              │
│                │      (circuito)          │   MAPA       │
│                │                          │              │
│                └──────────────────────────┘              │
├──────────────────────────────────────────────────────────┤
│ [▶ Play] [Agregar bus] [Deshacer]  Historial: 2 acciones │
│ Tasa de llegada (0 a 1) [0.4]  Capacidad [20] [Aplicar…] │
│ Mensaje para el usuario                                  │
└──────────────────────────────────────────────────────────┘
```

### 5.1 El mapa

| Elemento | Qué significa |
|---|---|
| **Circuito** (vía con línea amarilla) | La ruta de los buses. Se recorre en **sentido horario**: arriba de izquierda a derecha, baja por la derecha, abajo de derecha a izquierda y sube por la izquierda. |
| **Paradas P1 a P8** | Repartidas a la misma distancia sobre el circuito: P1, P2 y P3 en el lado de arriba; P4 en el lado derecho; P5, P6 y P7 en el lado de abajo; P8 en el lado izquierdo. |
| **Bus** (sprite azul) | Cambia de imagen según la dirección en que avanza (norte, sur, este, oeste). |
| **Contador `c/n` sobre el bus** | `c` = pasajeros a bordo, `n` = capacidad del bus. Ejemplo: `8/20`. |
| **Puntos junto a cada parada** | Cada punto es un pasajero esperando. **Azul** = prioritario (adulto mayor, movilidad reducida…); **gris** = normal. Los azules se dibujan primero, más cerca de la parada. |
| **`+N`** | Si en una parada esperan más de **12** personas, solo se dibujan 12 puntos y `+N` indica cuántas más hay. |
| **Recuadro "Minuto: X"** | Reloj de la simulación (esquina superior izquierda). |
| **Leyenda** | Debajo del minuto, recuerda el color de cada tipo de pasajero. |

> **Marcas de depuración.** En la versión actual se muestran encima del mapa unas
> marcas de ayuda: un cuadro verde con su número (0 a 31) en cada celda del circuito,
> un borde **rojo** en las celdas donde están las 8 paradas y los marcadores azules
> **E1–E4** en las esquinas. El borde rojo es la forma más segura de ubicar las
> paradas, porque algunos letreros dibujados en el fondo no coinciden con una parada
> real. Estas marcas se pueden ocultar (ver sección 9).

### 5.2 La barra de controles

**Fila 1 — Operación**

| Control | Función |
|---|---|
| **▶ Play / ⏸ Pausa** | Inicia, pausa o reanuda la simulación. El texto cambia según el estado. |
| **Agregar bus** | Añade un bus nuevo a la flota. |
| **Deshacer** | Revierte la última acción del operador. |
| **Historial: N acciones - última: X** | Muestra cuántas acciones hay guardadas en el historial (para deshacer) y cuál es la más reciente. |

**Fila 2 — Parámetros**

| Control | Función |
|---|---|
| **Tasa de llegada (0 a 1)** | Probabilidad de que llegue un pasajero en cada sorteo. Valor inicial: `0.4`. |
| **Capacidad del bus (entero ≥ 1)** | Cuántos pasajeros caben en cada bus. Valor inicial: `20`. |
| **Aplicar y reiniciar** | Empieza una simulación nueva con esos valores. |

**Fila 3 — Mensajes**: una línea de texto azul donde la aplicación informa qué pasó
con cada acción (ver sección 8).

---

## 6. Cómo funciona la simulación

### 6.1 Qué pasa en cada minuto

Cada minuto de simulación ocurre, en este orden:

1. **Llegan pasajeros.** En cada parada se hacen 3 sorteos; en cada uno llega un
   pasajero con probabilidad igual a la *tasa de llegada*. Por eso a cada parada llegan
   **entre 0 y 3** pasajeros por minuto. Cada pasajero tiene un destino al azar
   (siempre una parada distinta de la suya) y un **20 %** de probabilidad de ser
   prioritario.
2. **En cada bus, primero bajan** los pasajeros cuyo destino es la parada donde está
   (así se libera espacio).
3. **Después suben** los que esperan, mientras haya cupo:
   - primero **todos los prioritarios**, y
   - entre pasajeros del mismo tipo, **el que llegó antes sube antes**.
   - Los que no caben se quedan esperando al siguiente bus.
4. **El bus avanza** a la siguiente parada.
5. El reloj suma un minuto.

En pantalla esto se ve así: los buses se **desplazan suavemente** hasta la siguiente
parada (unos 0,6 s) y, al llegar, se actualizan los puntos de las paradas, los
contadores `c/n` y el minuto. Hay una pequeña espera (0,2 s) antes del minuto
siguiente. Cada bus avanza exactamente **una parada por minuto**.

### 6.2 Estado inicial

- **5 buses**, repartidos de forma pareja: arrancan en P1, P2, P4, P5 y P7.
- Todos los buses vacíos y ninguna persona esperando.
- Minuto 0.

Si varios buses coinciden en la misma parada, se dibujan uno al lado del otro sobre
la vía para que no se tapen.

### 6.3 Simulación repetible

La simulación usa una **semilla fija** para los números al azar. Esto significa que, con
los mismos parámetros, los pasajeros llegan siempre igual: si reinicia con los mismos
valores verá la misma secuencia de llegadas. Es útil para comparar, por ejemplo, qué
pasa con capacidad 10 frente a capacidad 20.

---

## 7. Guía de uso paso a paso

### 7.1 Iniciar la simulación

1. Pulse **▶ Play**.
2. El mensaje cambia a *"Simulación en marcha"* y los buses empiezan a moverse.
3. El botón pasa a decir **⏸ Pausa**.

> El primer Play **no** se guarda en el historial: solo arranca el reloj.

### 7.2 Pausar y reanudar

- Pulse **⏸ Pausa**: los buses se detienen al terminar el movimiento que estaban
  haciendo. Mensaje: *"Simulación en pausa"*.
- Pulse **▶ Play** otra vez para continuar. Mensaje: *"Simulación reanudada"*.
- Cada pausa y cada reanudación **sí** quedan en el historial y se pueden deshacer.

### 7.3 Agregar un bus

1. Pulse **Agregar bus** (funciona con la simulación corriendo, en pausa o antes del
   primer Play).
2. El bus nuevo aparece, vacío, en la **parada con más gente esperando** (si hay
   empate, en la de número menor). Así ayuda donde más se necesita.
3. Mensaje, por ejemplo: *"Se agregó el bus 6 en la parada P3"*.

Límite: la interfaz permite como máximo **10 buses**. Al llegar a ese número aparece
*"No se pueden agregar más buses: el máximo es 10"*.

### 7.4 Deshacer

**Deshacer** revierte la **última** acción del historial (la más reciente primero, como
una pila de platos). Puede pulsarlo varias veces para ir deshaciendo hacia atrás.

| Última acción | Qué hace Deshacer | Mensaje |
|---|---|---|
| Agregar bus (y el bus va **vacío**) | Quita ese bus | *"Se quitó el último bus agregado"* |
| Agregar bus (y el bus **lleva pasajeros**) | **No** lo quita; la acción sigue en el historial. Espere a que el bus se vacíe e intente de nuevo. | *"No se puede deshacer: el último bus agregado lleva pasajeros a bordo"* |
| Pausar | Reanuda la simulación | *"Se reanudó la simulación"* |
| Reanudar | Vuelve a pausar | *"Se volvió a pausar la simulación"* |
| (historial vacío) | Nada | *"No hay nada que deshacer"* |

Después de deshacer, el contador **Historial** y el botón Play/Pausa se actualizan
para reflejar el estado real.

### 7.5 Cambiar parámetros y reiniciar

1. Escriba la nueva **tasa de llegada** (número entre 0 y 1; se acepta coma decimal,
   por ejemplo `0,5`).
2. Escriba la nueva **capacidad del bus** (entero mayor o igual a 1).
3. Pulse **Aplicar y reiniciar**.

Si los valores son válidos se crea una **simulación completamente nueva**: minuto 0,
5 buses, paradas vacías e historial vacío. Queda **detenida** hasta que pulse Play.
Mensaje: *"Reiniciado con tasa 0.5 y capacidad 10. Pulse Play para empezar"*.

Si algún valor no es válido, **no se cambia nada** y aparece el error correspondiente
(ver sección 8).

**Ideas para experimentar**

| Para ver… | Pruebe |
|---|---|
| Filas largas y `+N` en las paradas | Tasa `0.8` y capacidad `5` |
| Buses casi vacíos | Tasa `0.1` y capacidad `30` |
| El efecto de reforzar la flota | Con filas largas, pulse **Agregar bus** varias veces |
| Prioritarios adelantándose | Capacidad baja (`3`–`5`) y observe que los puntos azules desaparecen primero |

### 7.6 Acciones durante el movimiento de los buses

Si pulsa un botón **mientras los buses se están moviendo**, la acción no se ejecuta en
ese instante: aparece *"Se hará al terminar el movimiento de los buses"* y se realiza
apenas lleguen a la parada. Si pulsa varios botones, se ejecutan **en el mismo orden**
en que los pulsó. Así nunca se mezcla un cambio con una animación a medias.

### 7.7 Cerrar la aplicación

Cierre la ventana con la **X**. La simulación no se guarda.

---

## 8. Mensajes de la aplicación

| Mensaje | Cuándo aparece |
|---|---|
| Pulse Play para empezar | Al abrir la aplicación |
| Simulación en marcha | Primer Play |
| Simulación en pausa / Simulación reanudada | Al pulsar Pausa / Play |
| Se agregó el bus N en la parada PX | Bus agregado con éxito |
| No se pueden agregar más buses: el máximo es 10 | Ya hay 10 buses |
| Se quitó el último bus agregado | Deshacer de un bus vacío |
| No se puede deshacer: el último bus agregado lleva pasajeros a bordo | Deshacer de un bus con pasajeros |
| Se reanudó la simulación / Se volvió a pausar la simulación | Deshacer de una pausa / reanudación |
| No hay nada que deshacer | Deshacer con historial vacío |
| Se hará al terminar el movimiento de los buses | Botón pulsado durante la animación |
| Reiniciado con tasa T y capacidad C. Pulse Play para empezar | Reinicio correcto |
| La tasa de llegada debe ser un número entre 0 y 1 | La tasa no es un número (ej. `abc`) |
| La tasa de llegada debe estar entre 0 y 1 | La tasa es un número fuera de rango (ej. `1.5`, `-0.2`) |
| La capacidad del bus debe ser un número entero | La capacidad no es entera (ej. `2.5`, `x`) |
| La capacidad del bus debe ser 1 o más | La capacidad es 0 o negativa |

---

## 9. Ajustes avanzados (en el código)

Algunos valores no están en la barra de controles, pero se pueden cambiar editando las
constantes del inicio de `app.py` y volviendo a ejecutar la aplicación:

| Constante | Valor actual | Qué controla |
|---|---|---|
| `NUMERO_BUSES` | `5` | Buses al iniciar o reiniciar |
| `CAPACIDAD_BUS` | `20` | Capacidad inicial (también editable en la barra) |
| `TASA_LLEGADA` | `0.4` | Tasa inicial (también editable en la barra) |
| `PROBABILIDAD_PRIORITARIO` | `0.2` | Probabilidad de que un pasajero sea prioritario |
| `INTENTOS_LLEGADA` | `3` | Sorteos por parada y minuto (máximo de llegadas por minuto) |
| `SEMILLA` | `42` | Semilla del azar; con `None` cada ejecución es distinta |
| `MAX_BUSES` | `10` | Tope de buses que deja agregar la interfaz |
| `MOSTRAR_DEPURACION` | `True` | Muestra u oculta las marcas de depuración del mapa |
| `DURACION_ANIMACION_MS` | `600` | Duración del movimiento de un minuto (ms) |
| `PAUSA_ENTRE_TICKS_MS` | `200` | Espera entre un minuto y el siguiente (ms) |
| `MAX_PUNTOS_POR_PARADA` | `12` | Puntos visibles por parada antes de mostrar `+N` |

---

## 10. Pruebas automáticas

Para verificar que las estructuras de datos y la lógica del simulador funcionan:

```bash
pytest
```

Las pruebas están en la carpeta `tests/` y no abren ninguna ventana.

---

## 11. Problemas frecuentes

| Problema | Solución |
|---|---|
| `ModuleNotFoundError: No module named 'PIL'` | Active el entorno virtual e instale las dependencias: `pip install -r requirements.txt` |
| `No module named 'tkinter'` | Reinstale Python marcando la opción *tcl/tk and IDLE* |
| Los buses no se mueven | Pulse **▶ Play**. Si el botón ya dice Play después de haber arrancado, la simulación está en pausa. |
| Pulsé un botón y no pasó nada | Si ve *"Se hará al terminar el movimiento de los buses"*, se ejecutará en menos de un segundo. |
| Deshacer no quita el bus que agregué | El bus lleva pasajeros; espere a que se bajen en sus destinos y vuelva a intentarlo. |
| Hay letreros en el fondo sin pasajeros | Algunos letreros del dibujo no son paradas reales; las paradas son las celdas con borde rojo. |

---

## 12. Limitaciones actuales

- El tamaño de la ventana es fijo (900 × 600 px de mapa).
- El número de paradas (8) y la forma del circuito son fijos.
- Desde la barra solo se pueden cambiar la tasa de llegada y la capacidad; el resto de
  parámetros se cambia en el código (sección 9).
- El simulador calcula un **reporte** con estadísticas (pasajeros generados, abordados,
  espera promedio, ocupación promedio), pero en esta versión **todavía no se muestra
  en la interfaz**.
- La simulación no se guarda al cerrar la aplicación.
