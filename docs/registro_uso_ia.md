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
| 2026-11-05 | `docs/descripcion.md` | Creado. Descripción técnica y conceptual de todo el proyecto (arquitectura, estructuras, simulador, interfaz, pruebas) y lista de diferencias entre el código y la documentación. No se modificó código. |
| 2026-11-17 | `docs/plan_preparacion.md` | Creado. Plan del Bloque 1 de la Fase 2: estructura de carpetas, dependencias verificadas en la documentación oficial, paso a paso de instalación, esqueleto comentado (sin código), Git, cronograma y preguntas. Luego actualizado con las 12 decisiones del equipo (`fastapi dev`, rangos `~=`, solo Pull Requests, `.vscode/` ignorado, `legacy/` conservado, etc.). No se modificó código. |
| 2026-11-17 | `docs/preparar_maquina.md` | Creado. Guía para dejar lista la máquina de Nicolás (Windows 10, Python 3.14) antes de crear la arquitectura: guardar documentos en la rama `esqueleto`, recrear `.venv`, medir la línea base (132 pruebas y app Tkinter) y configurar VS Code. No se modificó código. |
| 2026-11-19 | `requirements.txt` | Devuelto a la versión de la Fase 1 (`pytest==9.1.1`, `pillow==12.3.0`) con `git checkout`, porque se había editado por error antes de la pieza P2. Se recreó el `.venv` con Python 3.14.7, se instaló ese archivo y se midió la línea base: 132 pruebas aprobadas. Se creó la rama `esqueleto`. |
| 2026-11-19 | `legacy/app.py`, `legacy/imagenes/`, `legacy/__init__.py` | Pieza P1: `app.py` e `imagenes/` movidos a `legacy/` con `git mv` (sin cambiar ninguna línea; `app.py` busca las imágenes junto a sí mismo). Creado `legacy/__init__.py` (solo un comentario) para ejecutar con `python -m legacy.app`. Borrado `__pycache__/` de la raíz (no estaba en Git). 132 pruebas aprobadas. |
| 2026-11-19 | `requirements.txt` | Pieza P2: reescrito para la Fase 2 con rangos `~=`: `fastapi[standard]~=0.163.1`, `pytest~=9.2`, `httpx~=0.28.1`, con comentarios que explican cada línea. Se quitó Pillow (solo lo usa `legacy/`; se instala aparte). Instalado en el `.venv` sin errores en Windows 10 + Python 3.14.7: quedaron fastapi 0.163.2, uvicorn 0.54.0, starlette 1.10.0, httpx 0.28.1, pytest 9.2.0, fastapi-cli 0.0.34. 132 pruebas aprobadas. |
| 2026-11-19 | `.gitignore`, `.vscode/settings.json` | Pieza P3: `.gitignore` reescrito con comentarios: se separó la línea `.venv/.DS_Store` (eran dos reglas) y se agregaron `*.pyc`, `.pytest_cache/`, `.vscode/` y `Thumbs.db`. `.vscode/settings.json` se sacó del repositorio con `git rm --cached` (sigue en el disco de Nicolás). Verificado con `git status --ignored`: `.venv/`, `.vscode/`, cachés de pytest y `__pycache__/` quedan ignorados. |
| 2026-11-19 | `api/__init__.py`, `api/main.py`, `web/index.html`, `web/css/estilos.css`, `web/js/main.js`, `tests/test_api.py`, `datos/README.md`, `pyproject.toml` | Pieza P4: esqueleto de la Fase 2 con comentarios didácticos. API con un endpoint `GET /api/salud` y la carpeta `web/` montada en `/` al final; página que consulta la API con `fetch`; 3 pruebas con `TestClient`; README de `datos/`; `pyproject.toml` con `[tool.fastapi] entrypoint`. Verificado: 135 pruebas aprobadas; `fastapi dev` lee el entrypoint del paquete (`Using import string: api.main:app`); `/`, `/css/estilos.css`, `/js/main.js`, `/api/salud` y `/docs` responden 200. |
| 2026-11-19 | `docs/instalacion.md`, `README.md` | Pieza P5: creado el paso a paso de instalación para Windows, macOS y Linux (basado en la §3 del plan): requisitos, entorno virtual con `py -3.14`, activación por sistema, dependencias, pruebas (135), `fastapi dev`, lista de verificación, versión `legacy/`, rutina de Git del equipo (pull antes, pytest y push al terminar, todos en `main`) y tabla de problemas frecuentes. README reescrito para la Fase 2: inicio rápido, estructura por capas, enlaces a la documentación, `legacy/` y equipo. |
| 2026-11-19 | `CLAUDE.md` | Pieza P6: reescrito para la Fase 2, con el texto aprobado por Nicolás: reglas generales, quién escribe qué (el equipo implementa `estructuras/` y `simulador/`; Nicolás es el único que toca `simulador.py` y los endpoints), arquitectura de 4 capas, reglas de la API y de la web, `fastapi dev`, y las reglas de Tkinter reducidas a `legacy/`. |
| 2026-11-19 | `docs/registro_uso_ia.md` | Pieza P6: versiones exactas instaladas tras el Bloque 1 (`pip freeze`, Windows 10, Python 3.14.7). Directas: fastapi 0.163.2, pytest 9.2.0, httpx 0.28.1. Principales transitivas: uvicorn 0.54.0, starlette 1.10.0, pydantic 2.14.4, fastapi-cli 0.0.34, watchfiles 1.3.0, httptools 0.9.0. Aparte (solo para `legacy/`): pillow 12.3.0. |
| 2026-11-19 | `docs/plan_preparacion.md` | Decisión 6 y §5.3 actualizadas a la forma de trabajar real: la rama `esqueleto` solo para P1–P6 y después todos directo en `main`, con tabla de quién toca qué archivos, rutina pull → pytest → push y reglas mínimas. Anotado en §7 que la rama `esqueleto` se unió a `main`. Unión hecha con `git merge --no-ff esqueleto` en `main` y subida a GitHub; la rama `esqueleto` se borró (local y en GitHub). |
| 2026-11-24 | `api/main.py`, `tests/test_api.py` | Pieza A1 (Bloque 4): un único `Simulador` en memoria creado al cargar la API (mismos parámetros que `legacy/app.py`: 8 paradas, 5 buses, capacidad 10, tasa 0.5, prioritarios 0.5, 3 intentos, semilla 42) y dos endpoints de consulta: `GET /api/estado` → `Simulador.estado()` y `GET /api/reporte` → `Simulador.reporte()`, sin lógica de negocio. 5 pruebas nuevas con `TestClient` (claves esperadas, respuesta idéntica a la del `Simulador`, y que un GET no cambia el estado). Verificado: 140 pruebas aprobadas; con `fastapi run` los dos endpoints responden y aparecen en `/docs`. |
| 2026-11-24 | `docs/contexto_fase2.md`, `docs/plan_preparacion.md` | Fecha de entrega actualizada: se aplazó del jueves 26 al **sábado 28 de noviembre de 2026** (aviso de Nicolás). Corregidos el encabezado de ambos documentos, el título del cronograma (y su enlace en el índice) y la fila de la entrega; agregada una nota de que el reparto de los dos días ganados lo decide el equipo. |
| 2026-11-24 | `api/main.py`, `tests/test_api.py` | Pieza A2 (Bloque 4). **Implementada por Nicolás con guía de la IA** (pasos 1–5 de la guía): `import threading`, un `candado = threading.Lock()`, los dos GET protegidos con `with candado:` y 5 endpoints POST (`/api/avanzar`, `/api/pausar`, `/api/reanudar`, `/api/agregar-bus`, `/api/deshacer`) que llaman a un método del `Simulador` y devuelven `estado()`. **Revisión y correcciones de la IA:** (1) error en `/api/deshacer`: usaba `historial.esta_vacia` sin paréntesis (un método siempre es verdadero, así que el mensaje siempre era `None`) y armaba su propio texto leyendo la Pila, lo que es lógica de negocio en la API y nombraba la acción equivocada; ahora entrega tal cual el texto de `Simulador.deshacer()`; (2) `import threading` movido a las importaciones de la biblioteca estándar, con comentario; (3) comentarios didácticos del candado (analogía y advertencia de bloqueo si se llama a otro endpoint dentro del `with`), docstrings de los 5 POST y lista de endpoints del docstring del módulo. Pruebas (IA): 7 nuevas (avanzar, pausar, reanudar, agregar bus, deshacer bus, mensaje de deshacer y que un GET a una ruta POST no ejecuta nada). Corrección de la guía: un GET a una ruta POST responde 404 y no 405, porque lo atiende la web montada en `/`. Verificado: 147 pruebas aprobadas (también cada prueba de la API por separado) y el recorrido del paso 5 contra un servidor real. || 2026-11-25 | `tests/test_monticulo.py`, `tests/test_arbol_balanceado.py` | Revisión (sin editar el código) de `estructuras/monticulo.py` (de Nicolás) y `estructuras/arbol_balanceado.py` (de Santiago), y pruebas nuevas hechas por la IA. **Montículo, 114 pruebas:** constructor y tipo, errores con el montículo vacío, orden de salida en min/max-heap, repetidos, la propiedad del montículo después de cada operación, 50 casos al azar comparados con `sorted()`, número de comparaciones O(log n) al insertar y al extraer, y los dos usos del proyecto: despachos `(minuto, contador, id_bus)` con desempate por orden de llegada (y por qué sin contador da `TypeError`) y ranking de andenes. **AVL, 62 pruebas + 2 `xfail`:** vacío, insertar y buscar, clave repetida, los 4 casos de rotación, cada rotación probada por separado, altura con claves crecientes (1023 claves dan altura 10) y por debajo del límite de 1,44·log2(n+2), `verificar_balance` con árboles mal armados a mano, 20 casos al azar comparados con un diccionario y el índice de estaciones. Los 2 `xfail` (pruebas que hoy "fallan a propósito") señalan errores que el equipo debe corregir: `en_orden()` devuelve `None` en vez de `[]` con el árbol vacío, y `len()` cuenta de más al repetir una clave cuyo valor es `None`. Se comprobó que las pruebas detectan errores metidos a propósito en una copia temporal del código. Verificado: 323 pruebas aprobadas y 2 `xfail`. |
| 2026-11-25 | `estructuras/monticulo.py`, `tests/test_monticulo.py` | Con el visto bueno de Nicolás, la IA aplicó las correcciones menores de la revisión: los tipos pasan de `"min-heap"`/`"max-heap"` a `"minimos"`/`"maximos"`, `is_min_heap`/`is_max_heap` pasan a `es_de_minimos`/`es_de_maximos` (todo en español), `_hundir` ahora usa `_hijo_derecho` (antes calculaba `izq + 1`) y se agregaron comentarios didácticos (técnica del "hueco"). Pruebas adaptadas (115). Commit `b1ff534`. |
| 2026-11-25 | `estructuras/arbol_balanceado.py`, `tests/test_arbol_balanceado.py` | Con el visto bueno de Nicolás, la IA corrigió el AVL de Santiago: (1) `en_orden()` devuelve `[]` con el árbol vacío; (2) el tamaño se cuenta dentro de `_insertar`, solo donde nace un nodo, y ya no con `buscar()`, que confundía "no existe" con "su valor es None" (además recorre el árbol una sola vez); (3) nuevo `_buscar_nodo` (iterativo) y `contiene(clave)`; (4) nuevo `rango(desde, hasta)`, ambos extremos incluidos, O(log n + k); (5) nuevo `piso(clave)`: la mayor clave menor o igual a la pedida, O(log n), para "la última estación en o antes del km X"; (6) anotaciones de tipos, comentarios y dibujo de la rotación. Se conservaron sus rotaciones y la forma de elegir los 4 casos. Pruebas: se quitaron los 2 `xfail` (ya pasan) y se agregaron pruebas de `contiene`, `rango` y `piso`, también comparadas al azar con un diccionario. Se volvió a hacer la prueba de mutantes: todos los errores metidos a propósito se detectan. |
| 2026-11-25 | `estructuras/*.py`, `simulador/bus.py`, `simulador/parada.py`, `simulador/simulador.py`, `legacy/app.py`, `tests/*.py`, `docs/descripcion.md` | Estandarización de nombres acordada por el equipo: en todas las estructuras "¿está vacía?" se llama `esta_vacio()` (antes `vacio`, `esta_vacia` o `esta_vacio`) y el tamaño, `tamano()` (antes `longitud`, `tamano` o `__len__`). En el AVL el contador pasó a `_tamano` para no chocar con el método. Se cambiaron todas las llamadas en `simulador/`, las pruebas y la lista de operaciones de `docs/descripcion.md`. **Excepción aprobada por Nicolás:** en `legacy/app.py` se cambió una sola palabra (línea 1235, `esta_vacia` → `esta_vacio`) para que la versión Tkinter siga funcionando; compila sin errores. También se revirtieron los cambios accidentales en `api/main.py` y `web/index.html`. Verificado: 348 pruebas aprobadas. |
