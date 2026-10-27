# Registro de uso de IA

Este documento registra en qué partes del proyecto se usó inteligencia artificial, para qué, y qué hizo el equipo por su cuenta. Está basado en la diapositiva de cierre de la presentación y en el trabajo de depuración y revisión hecho con un asistente de IA durante el desarrollo.

---

## 1. Resumen del uso

| Actividad | Porcentaje con IA | Qué hizo la IA |
|---|---|---|
| Generación de pruebas con la librería Pytest | 100 % | Escribió las pruebas automáticas de las estructuras y clases |
| Desarrollo de animaciones de la interfaz gráfica | 70 % | Generó la mayor parte del código de animación de la interfaz |
| Documentación en línea de código y tipado de funciones | 30 % | Redactó parte de los docstrings, comentarios y anotaciones de tipos |

**Cómo se interpretan los porcentajes:** cada porcentaje indica qué parte *de esa actividad concreta* se hizo con IA, no qué parte del proyecto completo. Son los valores declarados por el equipo; no se calcularon a partir de líneas de código.

## 2. Lo que se implementó sin IA

Según la presentación: *"Cada estructura fue implementada por algún integrante del equipo; no fueron usadas librerías del lenguaje para implementarlas."*

| Componente | Archivo | Responsable |
|---|---|---|
| Nodo | `estructuras/nodo.py` | Pablo |
| Cola | `estructuras/cola.py` | Santiago |
| Pila | `estructuras/pila.py` | Santiago |
| Cola circular | `estructuras/cola_circular.py` | Nicolás |
| Cola con prioridad | `estructuras/cola_prioridad.py` | Nicolás |
| Arreglo dinámico | `estructuras/arreglo_dinamico.py` | Pablo |
| Pasajero | `simulador/pasajero.py` | Santiago |
| Parada | `simulador/parada.py` | Nicolás |
| Bus | `simulador/bus.py` | Pablo |
| Simulador | `simulador/simulador.py` | Nicolás |


## 3. Detalle por actividad

### 3.1 Pruebas con Pytest (100 % IA)

- **Qué se hizo:** la IA generó las pruebas de cada estructura y entidad del dominio.
- **Dónde está:** carpeta `tests/`. Se probaron todos los archivos correspondientes a las carpetas de `simulador/` y `estructuras/`
- **Qué hizo el equipo:** ejecutar las pruebas, revisar que verificaran el comportamiento correcto.
- **Herramienta usada:** Claude

### 3.2 Animaciones de la interfaz gráfica (70 % IA)

- **Qué se hizo:** la IA generó la mayor parte del código que dibuja y anima el mapa (buses, paradas, ocupación 0/20, botones Play, Agregar bus y Deshacer, controles de tasa de llegada y capacidad).
- **Dónde está:** interfaz en Tkinter. El historial del repositorio registra el cambio de Streamlit a Tkinter. Archivo principal: `app.py` y los módulos de interfaz.
- **Qué hizo el equipo (30 %):** conectar la interfaz con las clases `Bus`, `Parada` y `Simulador`, ajustar parámetros y probar el resultado. Diseñar los elementos gráficos de la interfaz.
- **Herramienta usada:** Claude

### 3.3 Documentación y tipado (30 % IA)

- **Qué se hizo:** la IA redactó parte de los docstrings (con la complejidad O() de cada método), comentarios explicativos y anotaciones de tipos como `ruta: ColaCircular`.
- **Qué hizo el equipo (70 %):** el resto de comentarios y docstrings, y la revisión de que describan correctamente lo que hace el código.
- **Herramienta usada:** Claude

## 4. Registro de cambios hechos con IA

| Fecha | Archivo | Qué se hizo |
|---|---|---|
| 2026-10-26 | `tests/test_arreglo_dinamico.py` | Se actualizaron las pruebas al nuevo `ArregloDinamico`: crecimiento por número áureo (1 → 2 → 4 → 7 → 12), `insertar` y `borrarposicion` en O(1) que no conservan el orden, y se quitó la prueba de `moda()` porque el método se eliminó. Se agregó una prueba de borrar el último y el único elemento. |
| 2026-10-26 | `tests/test_bus.py` | En `test_bajar_en_solo_baja_a_los_de_ese_destino` se comparan los pasajeros que quedan **ordenados**, porque `borrarposicion` ya no conserva el orden. |
| 2026-10-26 | `app.py` | Ventana de estadísticas (`tk.Toplevel` con su propio Canvas) que se abre al pausar y al pulsar el botón nuevo **Terminar**: 6 tarjetas con `reporte()`, gráficas de línea de `serie_esperando` y `serie_ocupacion` (leídas con `mostrar()`), barras de pasajeros por parada (de `estado()`) y anillo de abordados vs. esperando. Todo dibujado a mano en el Canvas, sin librerías nuevas. Se cierra al reanudar o reiniciar. No se modificó `simulador/` ni `estructuras/`. |
| 2026-10-26 | `app.py` | La ventana de estadísticas ahora se abre **solo al pulsar Terminar** (ya no al pausar, deshacer ni agregar bus). Valores por defecto cambiados a tasa de llegada 0.5 y capacidad 10 por bus (escenario estable para el video de demostración). |
| 2026-10-26 | `docs/manual_usuario.md` | Se documentó el botón **Terminar** y la ventana de estadísticas (nueva sección 7.6; las siguientes pasan a 7.7 y 7.8), con sus mensajes y un problema frecuente. Se actualizaron los valores por defecto (tasa 0.5, capacidad 10) en el diagrama, las tablas y los ajustes avanzados; se agregó la idea de experimento "línea saturada" (0.5 y 8) y se cambió la limitación que decía que el reporte no se mostraba en la interfaz. |
