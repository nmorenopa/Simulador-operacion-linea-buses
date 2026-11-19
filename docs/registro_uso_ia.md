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