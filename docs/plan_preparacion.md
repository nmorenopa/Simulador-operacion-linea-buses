# Plan de preparación — Fase 2 (Bloque 1: entorno y esqueleto)

> **Estado: APROBADO con ajustes (17-nov-2026).** Las respuestas del equipo están en la
> sección [Decisiones tomadas](#decisiones-tomadas-17-nov-2026) y ya se aplicaron al resto del documento.
> Antes de ejecutar las piezas, Nicolás prepara su máquina con `docs/preparar_maquina.md`.
> Fecha: 17 de noviembre de 2026. Entrega: **sábado 28 de noviembre de 2026** (aplazada el
> 24-nov; antes era el jueves 26).
> Equipo: Pablo José Cárdenas, Nicolás Moreno Parra y Santiago Rodríguez Ortega.

Este documento propone **cómo dejar el repositorio listo** para la Fase 2 (TransMilenio,
Portal Américas ↔ Portal Norte, API en FastAPI y web en HTML/CSS/JS plano). Se ejecuta por
**piezas pequeñas (P1, P2, …)**; cada pieza se aprueba antes de hacerla.

---

## Decisiones tomadas (17-nov-2026)

| # | Tema | Decisión del equipo | Qué cambia en el plan |
|---|---|---|---|
| 1 | Máquinas | Nicolás: Windows 10, Python 3.14 · Santiago: Windows 11, Python 3.14 · Pablo: macOS, Python 3.14 | Todos cumplen el mínimo de FastAPI (3.11+). El mínimo del proyecto pasa a **Python 3.11** |
| 2 | Prefijo `/api` | Aceptado | Todos los endpoints empiezan por `/api/` |
| 3 | `legacy/` | Se conserva funcionando | Pillow se instala aparte solo para abrirlo (§1) |
| 4 | Comando de arranque | **`fastapi dev`** (no importa que instale más cosas) | `requirements.txt` usa `fastapi[standard]`; se agrega un `pyproject.toml` mínimo con el punto de entrada (§2, §3.6) |
| 5 | Versiones | **Rangos** | Se usa `~=` (ver §2.1) |
| 6 | Git | ~~Solo Pull Requests~~ **Actualizada el 19-nov:** la rama `esqueleto` solo para P1–P6; después todos trabajan directo en `main`, repartidos por archivos. Nicolás es dueño de `simulador/simulador.py` y de los endpoints | §5.3 reescrito |
| 7 | `.vscode/` | Se ignora | Se agrega a `.gitignore` y se saca del repositorio (§5.1) |
| 8 | Reparto | Lo define el grupo | El cronograma ya no tiene nombres |
| 9 | Pruebas de la API | Cuentan dentro de "Pruebas con Pytest (100 % IA)" del registro | Se anotan ahí |
| 10 | `CLAUDE.md` | Sí, actualizarlo para la versión web | Pieza P6 |
| 11 | `estructuras/` y `simulador/` | **El equipo los implementa** para aprender; el asistente **revisa y corrige** lo implementado | El asistente propone cada corrección y la aplica solo con su visto bueno |
| 12 | `datos/` | Vacía | Solo con un `README.md` (Git no guarda carpetas vacías) |

---

## Índice

0. [Glosario: palabras nuevas](#0-glosario-palabras-nuevas)
1. [Estructura de carpetas final](#1-estructura-de-carpetas-final)
2. [Dependencias (`requirements.txt`)](#2-dependencias-requirementstxt)
3. [Paso a paso para los compañeros](#3-paso-a-paso-para-los-compañeros)
4. [Esqueleto mínimo (plan comentado, sin código final)](#4-esqueleto-mínimo-plan-comentado)
5. [Cambios de configuración del repositorio](#5-cambios-de-configuración-del-repositorio)
6. [Cronograma del 17 al 28 de noviembre](#6-cronograma-del-17-al-28-de-noviembre)
7. [Orden de ejecución de este plan (piezas)](#7-orden-de-ejecución-de-este-plan-piezas)
8. [Preguntas y decisiones pendientes](#8-preguntas-y-decisiones-pendientes)

---

## 0. Glosario: palabras nuevas

| Término | Qué significa, en sencillo |
|---|---|
| **API** | "Ventanilla" del programa: un conjunto de direcciones (URL) a las que otro programa (aquí, la página web) le pide cosas. Nuestra API recibe la petición, le pregunta al `Simulador` y devuelve la respuesta. |
| **Endpoint** | Una ventanilla concreta de la API: un **método** + una **ruta**, por ejemplo `GET /api/estado`. |
| **Método HTTP** | El "verbo" de la petición. `GET` = "dame información" (no cambia nada). `POST` = "haz algo" (cambia el estado, p. ej. avanzar un minuto). |
| **JSON** | Formato de texto para enviar datos: `{"minuto": 5, "en_pausa": false}`. Es casi igual a un diccionario de Python; por eso `estado()` y `reporte()` encajan tan bien. |
| **FastAPI** | Librería de Python para escribir APIs. Uno escribe una función normal, le pone encima un *decorador* (`@app.get("/ruta")`) y FastAPI se encarga de recibir la petición y convertir el diccionario que devolvemos a JSON. |
| **Decorador** | La línea con `@` encima de una función. Aquí significa: "cuando llegue una petición `GET` a esta ruta, ejecuta esta función". |
| **Servidor / Uvicorn** | FastAPI define *qué* responder; **Uvicorn** es el programa que se queda escuchando en un puerto de tu computador y entrega las peticiones a FastAPI. Es como el mesero (Uvicorn) que lleva los pedidos a la cocina (FastAPI). |
| **`fastapi dev`** | Comando que trae `fastapi[standard]`. Por dentro arranca Uvicorn en modo desarrollo (se reinicia solo al guardar un archivo). Es un atajo: no reemplaza a Uvicorn, lo usa. |
| **`pyproject.toml`** | Archivo de configuración estándar de proyectos Python. Aquí solo lo usaremos para decirle a `fastapi dev` dónde está nuestra app (`api.main:app`). |
| **ASGI** | El "idioma" estándar con el que Uvicorn y FastAPI se hablan. No hay que hacer nada con él; basta saber que por eso funcionan juntos. |
| **Puerto / `127.0.0.1:8000`** | `127.0.0.1` (o `localhost`) es "este mismo computador". `8000` es la "puerta" por la que escucha el servidor. Solo tú puedes verlo; no queda publicado en internet. |
| **Archivos estáticos** | Archivos que se envían tal cual al navegador, sin procesarlos: `index.html`, `.css`, `.js`, imágenes. FastAPI los sirve con `StaticFiles`. |
| **Montar (`app.mount`)** | Conectar una "sub-aplicación" completa en una ruta. Montamos la carpeta `web/` en `/` para que al abrir `http://127.0.0.1:8000/` se vea la página. |
| **CORS** | Regla de seguridad del navegador que bloquea peticiones entre "orígenes" distintos (otro puerto u otro dominio). Como la página y la API salen del **mismo** servidor, no hay que configurarla. |
| **`fetch`** | Función de JavaScript del navegador para hacer peticiones HTTP a la API y leer la respuesta. |
| **Módulos ES** | Forma moderna de separar el JS en archivos (`import`/`export`) sin herramientas extra. Se activan con `<script type="module">`. |
| **Entorno virtual (`.venv`)** | Una carpeta con un Python "privado" del proyecto y sus librerías, para no mezclarlas con las de otros proyectos. Cada integrante crea el suyo; **no se sube a Git**. |
| **`TestClient`** | Herramienta de FastAPI para probar la API **desde pytest, sin arrancar el servidor**: simula peticiones y revisa las respuestas. Necesita la librería `httpx`. |
| **Swagger UI (`/docs`)** | Página que FastAPI genera sola en `http://127.0.0.1:8000/docs`, con la lista de endpoints y un botón para probarlos. Muy útil para aprender y depurar. |
| **Rama (branch)** | Línea de trabajo paralela en Git, para que cada uno avance sin pisar el trabajo de los otros. |

---

## 1. Estructura de carpetas final

```
Simulador-operacion-linea-buses/
├── estructuras/          NO SE TOCA. Capa 1. Aquí el equipo agregará heap, AVL, segmentos…
├── simulador/            NO SE TOCA en este bloque. Capa 2. (Se adapta en el Bloque 2, por el equipo)
├── api/                  SE CREA. Capa 3: FastAPI, solo traduce.
│   ├── __init__.py       Vacío; marca la carpeta como paquete de Python
│   └── main.py           Crea la app, define endpoints y monta web/
├── web/                  SE CREA. Capa 4: lo que ve el navegador.
│   ├── index.html
│   ├── css/
│   │   └── estilos.css
│   └── js/
│       └── main.js       Llama a la API con fetch y pinta la respuesta
├── datos/                SE CREA (vacía, con un README.md que explica qué irá: JSON de la ruta)
├── tests/                SE CONSERVA. Se AGREGA tests/test_api.py (pruebas del esqueleto)
├── docs/                 SE CONSERVA. Se agrega este plan y docs/instalacion.md (paso a paso)
├── legacy/               SE CREA. Aquí se MUEVE la versión Tkinter, sin editarla:
│   ├── app.py            (movido desde la raíz)
│   └── imagenes/         (movida desde la raíz: FONDO.png y bus/*.png)
├── requirements.txt      SE MODIFICA
├── pyproject.toml        SE CREA (solo 2 líneas: el punto de entrada de `fastapi dev`)
├── .gitignore            SE CORRIGE
├── README.md             SE ACTUALIZA
└── CLAUDE.md             SE ACTUALIZA (aprobado, ver §5.4)
```

### Resumen por acción

| Acción | Qué |
|---|---|
| **No se toca** | `estructuras/` (todo), `simulador/` (todo), las 10 pruebas actuales de `tests/`, `docs/explicacion_estructuras.md`, `docs/manual_usuario.md` |
| **Se mueve (con `git mv`, para conservar el historial)** | `app.py` → `legacy/app.py` · `imagenes/` → `legacy/imagenes/` |
| **Se crea** | `api/__init__.py`, `api/main.py`, `web/index.html`, `web/css/estilos.css`, `web/js/main.js`, `datos/README.md`, `tests/test_api.py`, `docs/instalacion.md`, `pyproject.toml` |
| **Se modifica** | `requirements.txt`, `.gitignore`, `README.md`, `CLAUDE.md`, `docs/registro_uso_ia.md` |
| **Sale del repositorio** (queda en cada computador) | `.vscode/settings.json` |

### ¿Por qué `app.py` sigue funcionando después de moverlo?

- `app.py` busca las imágenes con `Path(__file__).resolve().parent / "imagenes"`, o sea, **junto a sí
  mismo**. Si `imagenes/` se mueve con él a `legacy/`, las encuentra sin cambiar una línea.
- Sus `import` (`from estructuras.cola import Cola`, `from simulador.simulador import Simulador`)
  necesitan que Python arranque desde la **raíz** del proyecto. Por eso, en vez de
  `python legacy/app.py`, se ejecutará como módulo desde la raíz: **`python -m legacy.app`**
  (el `-m` le dice a Python "busca `legacy/app.py` partiendo de la carpeta actual", y así
  `estructuras/` y `simulador/` quedan visibles).
- Necesita Pillow, que sale de `requirements.txt` (ver §2). Quien quiera abrir la versión vieja
  instala Pillow aparte: `python -m pip install pillow`.

---

## 2. Dependencias (`requirements.txt`)

### 2.1 Propuesta (ajustada a las decisiones 4 y 5)

```text
# --- API y servidor (capa 3) ---
# [standard] trae Uvicorn, el comando "fastapi dev" y otras utilidades.
fastapi[standard]~=0.163.1

# --- Pruebas ---
pytest~=9.2
httpx~=0.28.1    # TestClient lo necesita; lo dejamos explícito para no depender de [standard]
```

**Cómo leer los rangos `~=`** (se llama "versión compatible"):
- `fastapi[standard]~=0.163.1` significa **≥ 0.163.1 y < 0.164**: acepta arreglos de errores
  (0.163.2, 0.163.3…) pero no la siguiente versión "menor". En FastAPI, que todavía está en 0.x,
  los cambios que rompen cosas suelen llegar justo en esas versiones menores; por eso el rango es
  estrecho.
- `pytest~=9.2` significa **≥ 9.2 y < 10**.
- `httpx~=0.28.1` significa **≥ 0.28.1 y < 0.29** (así no se cuela la versión 1.0, que aún es de prueba).

Otras notas:
- **Se quita `pillow`**: solo lo usa la interfaz Tkinter, que pasa a `legacy/`. Para abrirla:
  `python -m pip install pillow` y luego `python -m legacy.app`.
- **No se agrega Leaflet** a este archivo: es JavaScript y se cargará por CDN (un enlace en el HTML)
  en el Bloque 4, no con `pip`.
- Después de instalar se corre `python -m pip freeze` para **anotar** en el registro qué versiones
  exactas quedaron, pero en `requirements.txt` solo van las 3 dependencias directas con su rango.

### 2.2 Por qué `fastapi[standard]` (decisión 4)

La página de FastAPI recomienda `fastapi[standard]`. Según PyPI instala: Uvicorn (con su versión
`[standard]`), httpx, Jinja2, python-multipart, email-validator y `fastapi-cli[standard]`, que es
el que da el comando **`fastapi`** (incluye también una herramienta para su servicio en la nube,
*FastAPI Cloud*, que no usaremos). Instala más cosas, pero el arranque queda en un comando corto:
`fastapi dev`.

Para que `fastapi dev` sepa dónde está nuestra app sin escribirlo cada vez, la documentación
recomienda declararlo en `pyproject.toml`:

```toml
[tool.fastapi]
entrypoint = "api.main:app"   # archivo api/main.py, objeto app
```

### 2.3 Qué verifiqué y qué no

**Verificado en la documentación oficial (consultada el 17-nov-2026):**

| Dato | Fuente | Resultado |
|---|---|---|
| Versión de FastAPI | pypi.org/project/fastapi | 0.163.1 (15-nov-2026). **Requiere Python ≥ 3.11** |
| Versión de Uvicorn | pypi.org/project/uvicorn | 0.54.0 (25-sep-2026). Requiere Python ≥ 3.10. `[standard]` agrega uvloop y httptools "si es posible", websockets, **watchfiles (para `--reload`)**, python-dotenv y PyYAML |
| Versión de pytest | pypi.org/project/pytest | 9.2.0 (27-oct-2026). Requiere Python ≥ 3.10 |
| Versión de httpx | pypi.org/project/httpx | 0.28.1 estable (dic-2024). Existe un 1.0 en *pre-release*: no lo usamos |
| `TestClient` necesita httpx | fastapi.tiangolo.com/tutorial/testing | "To use TestClient, first install httpx". Import: `from fastapi.testclient import TestClient`. Las pruebas son `def` normales, sin `async` |
| Archivos estáticos | fastapi.tiangolo.com/tutorial/static-files | `from fastapi.staticfiles import StaticFiles` y `app.mount("/static", StaticFiles(directory="static"), name="static")`. No pide paquetes extra |
| Parámetro `html=True` | starlette.dev/staticfiles | `StaticFiles(directory=None, packages=None, html=False, check_dir=True, follow_symlink=False)`. `html=True`: "Automatically loads index.html for directories" |
| Comando de Uvicorn | fastapi.tiangolo.com/deployment/manually | `uvicorn main:app --host 0.0.0.0 --port 80` (`main` = archivo, `app` = objeto). `--reload` se menciona como opción solo para desarrollo |
| URL por defecto y `/docs` | fastapi.tiangolo.com/tutorial/first-steps | `http://127.0.0.1:8000`, Swagger en `/docs`, ReDoc en `/redoc` |
| Activar el entorno virtual | docs.python.org/3/library/venv.html | bash/zsh: `source <venv>/bin/activate`; cmd: `<venv>\Scripts\activate.bat`; PowerShell: `<venv>\Scripts\Activate.ps1`; y `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` si PowerShell bloquea el script |
| `APIRouter` | fastapi.tiangolo.com/tutorial/bigger-applications | Existe y se une con `app.include_router(...)`. **No lo usaremos aún** (un solo archivo es más fácil de explicar); queda como nota para cuando `api/main.py` crezca |

**No pude verificar (o verifiqué solo de forma indirecta):**

1. **Que `fastapi[standard]` (y con él `uvicorn[standard]`) instale sin problemas con Python 3.14**
   en Windows 10/11 y macOS. La página de Uvicorn dice que uvloop y httptools se instalan "si es
   posible"; uvloop no funciona en Windows y simplemente se omite. Lo comprobaremos en la pieza P2.
   **Plan B:** `fastapi~=0.163.1` + `uvicorn~=0.54.0` sueltos y arrancar con
   `python -m uvicorn api.main:app --reload`.
1b. **Que `fastapi dev` lea `[tool.fastapi] entrypoint` con una app dentro de un paquete
   (`api.main:app`)**. La documentación muestra `entrypoint = "main:app"`; con un paquete lo
   comprobaremos en P4. **Plan B:** `fastapi dev --entrypoint api.main:app` (la opción
   `--entrypoint` sí aparece en la documentación).
2. **`app.frontend()`**: la página de archivos estáticos menciona un `app.frontend()` nuevo "para
   alojar un frontend". No leí su documentación completa, así que **no lo usaremos**; nos quedamos
   con `StaticFiles`, que sí está documentado y es más fácil de explicar.
3. **El orden de las rutas** (que el `mount` en `/` vaya **después** de los endpoints): lo sé por cómo
   Starlette revisa las rutas en orden, pero no lo encontré escrito en las páginas consultadas. Lo
   comprobaremos con una prueba en `tests/test_api.py`.
4. **La política de uso de los mosaicos de OpenStreetMap y la versión de Leaflet**: corresponde al
   Bloque 4; no la revisé todavía.

> ⚠️ **Hallazgo importante:** `contexto_fase2.md` dice "Python 3.10+", pero **FastAPI 0.163.1
> exige Python 3.11 o superior**. El mínimo del proyecto pasa a **Python 3.11**. Los tres
> integrantes tienen Python 3.14, así que no hay problema.

---

## 3. Paso a paso para los compañeros

> Esto se guardará como `docs/instalacion.md` (pieza P5) y el README enlazará ahí.
> **Regla de oro:** todos los comandos se escriben **en la carpeta raíz del proyecto**
> (la que contiene `requirements.txt`).

### 3.0 Requisitos previos (una sola vez)

- **Git** instalado (`git --version` debe mostrar un número).
- **Python 3.11 o superior** (`python --version` en Windows; `python3 --version` en macOS/Linux).
  - En Windows, al instalar Python marquen **"Add python.exe to PATH"**.
  - En Linux (Ubuntu/Debian) puede faltar el módulo de entornos: `sudo apt install python3-venv`.
- Un navegador moderno (Chrome, Edge, Firefox o Safari).

### 3.1 Traer el código

**Primera vez (no tienen la carpeta):**
```bash
git clone https://github.com/nmorenopa/Simulador-operacion-linea-buses.git
cd Simulador-operacion-linea-buses
```

**Ya tienen la carpeta:**
```bash
cd Simulador-operacion-linea-buses
git checkout main
git pull
```

### 3.2 Crear el entorno virtual

Si ya tenían un `.venv` de la Fase 1, **bórrenlo y créenlo de nuevo** (puede traer librerías
viejas de Streamlit o Pillow que ya no usamos):

| Sistema | Borrar el `.venv` viejo (si existe) | Crear el nuevo |
|---|---|---|
| Windows – Git Bash | `rm -rf .venv` | `python -m venv .venv` |
| Windows – PowerShell | `Remove-Item -Recurse -Force .venv` | `python -m venv .venv` |
| macOS / Linux | `rm -rf .venv` | `python3 -m venv .venv` |

### 3.3 Activar el entorno virtual (cada vez que abran una terminal nueva)

| Sistema | Comando |
|---|---|
| Windows – Git Bash | `source .venv/Scripts/activate` |
| Windows – PowerShell | `.venv\Scripts\Activate.ps1` |
| Windows – cmd | `.venv\Scripts\activate.bat` |
| macOS / Linux (bash o zsh) | `source .venv/bin/activate` |

✅ Sabrán que funcionó porque la línea de la terminal empieza con **`(.venv)`**.
Desde aquí, en **todos** los sistemas se puede escribir `python` (ya no hace falta `python3`).

### 3.4 Instalar dependencias

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Usamos `python -m pip` en lugar de `pip` a secas para asegurarnos de que se instala en el Python
**del entorno virtual** y no en otro.

### 3.5 Correr las pruebas

```bash
python -m pytest
```

### 3.6 Arrancar el servidor

```bash
fastapi dev
```

Cómo funciona este comando:
- `fastapi dev` lee en `pyproject.toml` la línea `entrypoint = "api.main:app"`:
  - `api.main` → el archivo `api/main.py` (los `/` se escriben como `.`).
  - `:app` → dentro de ese archivo, el objeto que se llama `app` (el `app = FastAPI()`).
- `dev` = modo desarrollo: arranca Uvicorn y **se reinicia solo** cada vez que guardan un archivo.
  (Para producción existe `fastapi run`; no lo necesitamos.)

Equivalente "a mano", por si algún día falla `fastapi dev`:
`python -m uvicorn api.main:app --reload`.

El servidor se queda corriendo: esa terminal queda "ocupada". Para detenerlo: **Ctrl + C**.

### 3.7 Abrir la página

Con el servidor corriendo, abran en el navegador:
- **http://127.0.0.1:8000/** → la página del proyecto.
- **http://127.0.0.1:8000/docs** → la documentación automática de la API (Swagger UI).

### 3.8 Lista de verificación (si todo salió bien)

- [ ] `python --version` muestra **3.11 o superior**.
- [ ] La terminal muestra `(.venv)` al inicio de la línea.
- [ ] `python -m pip install -r requirements.txt` termina sin errores en rojo.
- [ ] `python -m pytest` termina con **todas aprobadas**: las 132 de antes + las nuevas de la API
      (alrededor de 135 en total) y **0 fallidas**.
- [ ] Al arrancar el servidor aparece una línea parecida a
      `Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)`.
- [ ] En `http://127.0.0.1:8000/` se ve el título del proyecto y el mensaje
      **"Conectado: la API respondió"** con los datos que devolvió la API.
- [ ] En `http://127.0.0.1:8000/docs` aparece el endpoint `GET /api/salud` y, al pulsar
      "Try it out" → "Execute", responde con código **200**.
- [ ] En la terminal del servidor aparece una línea `GET /api/salud ... 200 OK` cada vez que se
      recarga la página.

### 3.9 Problemas frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `python` no se reconoce (Windows) o abre la Microsoft Store | Python no está en el PATH, o Windows usa su "alias" de la tienda | Reinstalar Python marcando "Add python.exe to PATH", o probar con `py` en lugar de `python`. Desactivar los alias en *Configuración → Aplicaciones → Alias de ejecución de aplicaciones* |
| `python3: command not found` (macOS) | Falta Python | Instalarlo desde python.org |
| PowerShell: "la ejecución de scripts está deshabilitada en este sistema" | Política de seguridad de PowerShell | Una sola vez: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` y volver a activar |
| `The virtual environment was not created successfully because ensurepip is not available` (Linux) | Falta el paquete `venv` | `sudo apt install python3-venv` |
| `ERROR: ... Requires-Python >=3.11` al instalar | Python demasiado viejo | Instalar Python 3.11+ y crear el `.venv` de nuevo con ese Python |
| `ModuleNotFoundError: No module named 'fastapi'` | El entorno no está activado, o se instaló en otro Python | Activar `.venv` (debe verse `(.venv)`) y repetir `python -m pip install -r requirements.txt` |
| `ModuleNotFoundError: No module named 'api'` o `'simulador'` | El comando se ejecutó desde otra carpeta | Hacer `cd` a la raíz del proyecto (donde está `requirements.txt`) |
| `fastapi: command not found` / "no se reconoce como nombre de un cmdlet" | El entorno no está activado o no se instaló `fastapi[standard]` | Activar `.venv` y repetir la instalación |
| `[Errno 10048]` / `address already in use` | Ya hay otro servidor en el puerto 8000 (quizás otra terminal abierta) | Cerrar la otra terminal con Ctrl + C, o usar otro puerto: `fastapi dev --port 8001` |
| La página carga pero dice "No se pudo conectar con la API" | Abrieron el `index.html` con doble clic (`file:///...`) | Abrir **siempre** `http://127.0.0.1:8000/`; la página debe venir del servidor |
| Cambié el JS o el CSS y no veo el cambio | El navegador guardó una copia vieja (caché) | Recarga forzada: **Ctrl + Shift + R** (Windows/Linux) o **Cmd + Shift + R** (macOS) |
| `RuntimeError: Directory 'web' does not exist` | Falta la carpeta `web/` (pull incompleto) | `git pull` de nuevo y revisar que exista `web/index.html` |
| Error instalando `fastapi[standard]` en Windows | Alguna pieza opcional sin soporte | Avisar al grupo; plan B en §2.3 |
| `git pull` dice que hay cambios locales que se sobrescribirían | Modificaron archivos que también cambiaron en GitHub | `git status` para verlos; `git stash`, luego `git pull`, luego `git stash pop`. Si no entienden el mensaje, **paren y pregunten** antes de forzar nada |

---

## 4. Esqueleto mínimo (plan comentado)

Objetivo: **comprobar que las 4 piezas están conectadas** (Python → FastAPI → navegador → JS)
antes de meter lógica real. **Todavía no se conecta el `Simulador`**: eso es el Bloque 4.

### 4.1 El recorrido de una petición

```
Navegador                        Servidor (un solo comando: fastapi dev)
─────────                        ───────────────────────────────────
1. Abre http://127.0.0.1:8000/ ─► StaticFiles (montado en "/") entrega web/index.html
2. index.html pide css y js    ─► StaticFiles entrega web/css/estilos.css y web/js/main.js
3. main.js hace fetch("/api/salud") ─► endpoint salud() en api/main.py
4.                             ◄── devuelve {"estado": "ok", "mensaje": "...", "version_python": "3.x.y"}
5. main.js escribe esa respuesta dentro de la página
```

### 4.2 `api/main.py` — plan comentado (pseudocódigo, no es el código final)

```text
# 1. Importaciones
#    - FastAPI (la aplicación) y StaticFiles (para servir la carpeta web/).
#    - Path, para armar la ruta a web/ a partir de la ubicación de ESTE archivo
#      (igual que hacía app.py con sus imágenes). Así funciona sin importar desde
#      qué carpeta se lance el comando.
#    - platform, solo para devolver la versión de Python (dato de prueba real, no inventado).
#
# 2. Crear la aplicación
#    app = FastAPI(title="Simulador TransMilenio", ...)
#    -> "app" es el nombre que usamos en el comando  api.main:app
#
# 3. Endpoint de prueba (ANTES del mount)
#    @app.get("/api/salud")
#    def salud():
#        devolver un diccionario: estado "ok", un mensaje y la versión de Python
#    -> FastAPI convierte el diccionario a JSON solo.
#    -> Prefijo /api/: separa las direcciones de la API de las de la página.
#    -> Aquí NO habrá lógica de negocio nunca. En el Bloque 4, cada endpoint será
#       una línea que llama a un método del Simulador y devuelve su resultado.
#
# 4. Montar la carpeta web/ en "/"  (SIEMPRE AL FINAL)
#    app.mount("/", StaticFiles(directory=CARPETA_WEB, html=True), name="web")
#    -> html=True: al pedir "/" entrega index.html automáticamente.
#    -> Va al final porque "/" atrapa cualquier dirección; si estuviera antes,
#       se "comería" las peticiones a /api/... (lo comprobamos con una prueba).
```

### 4.3 `web/index.html` — plan comentado

```text
- <!doctype html>, idioma "es", charset UTF-8 y viewport (para que se vea bien en el celular).
- <title>Simulador TransMilenio</title> y enlace a css/estilos.css.
- <h1> con el nombre del proyecto y un <p> que diga "Fase 2 – esqueleto".
- Un <section id="resultado"> que al inicio diga "Consultando la API…".
- Un botón "Volver a consultar" (para ver que la API responde cada vez).
- <script type="module" src="js/main.js"></script> al final.
- Sin librerías externas todavía (Leaflet llega en el Bloque 4).
```

### 4.4 `web/js/main.js` — plan comentado

```text
// 1. Buscar en la página el <section id="resultado"> y el botón.
// 2. Función async consultarSalud():
//      - respuesta = await fetch("/api/salud")      // pide al servidor
//      - si respuesta.ok es falso -> mostrar "La API respondió con error <código>"
//      - datos = await respuesta.json()              // convierte el texto JSON en objeto JS
//      - mostrar "Conectado: la API respondió" y los datos (estado, mensaje, versión)
//      - si fetch falla (servidor apagado o página abierta con doble clic):
//        mostrar "No se pudo conectar con la API. ¿Está corriendo fastapi dev?"
// 3. Llamar consultarSalud() al cargar la página y cada vez que se pulse el botón.
//
// Regla: el JS solo dibuja y manda órdenes. No calcula nada del simulador.
// Se usa textContent (no innerHTML) para escribir texto: es más seguro y más simple.
```

### 4.5 `web/css/estilos.css` — plan comentado

```text
- Variables de color (:root) con los tonos de TransMilenio (rojo) y fondo claro.
- Tipografía del sistema, contenido centrado con ancho máximo, márgenes de 16 px en celular.
- Una clase .ok (verde) y .error (rojo) para el mensaje de resultado.
- Nada más: lo visual se pule al final (es lo primero que se recorta).
```

### 4.6 `tests/test_api.py` — plan comentado

```text
- client = TestClient(app)      # simula el navegador, sin arrancar el servidor
- test_salud_responde_ok:       GET /api/salud -> código 200 y "estado" == "ok"
- test_pagina_principal:        GET / -> código 200 y el texto contiene "Simulador TransMilenio"
- test_api_no_la_tapa_la_web:   confirma que /api/salud sigue devolviendo JSON aunque
                                la web esté montada en "/" (verifica el orden del mount)
```

---

## 5. Cambios de configuración del repositorio

### 5.1 `.gitignore`

Hoy tiene:
```
__pycache__/
.venv/.DS_Store
.DS_Store
```
La línea 2 junta dos reglas y no ignora `.venv/` (hoy funciona solo porque el propio entorno trae
un `.gitignore` interno). `.DS_Store` ya está en la línea 3. Propuesta:

```gitignore
# Python
__pycache__/
*.pyc
.pytest_cache/

# Entorno virtual (cada quien crea el suyo)
.venv/

# Configuración personal del editor (decisión 7)
.vscode/

# Archivos del sistema operativo
.DS_Store
Thumbs.db
```

**Ojo con `.vscode/`:** como `settings.json` **ya está** en el repositorio, agregarlo a
`.gitignore` no basta (Git sigue vigilando lo que ya conoce). Hay que sacarlo del repositorio
**sin borrarlo del disco**: `git rm --cached .vscode/settings.json`. Efecto secundario: cuando
Santiago y Pablo hagan `git pull`, Git **borrará su copia** de ese archivo. Solo tiene ajustes de
autocompletado del editor; si alguien los quiere, que los copie antes del pull.

### 5.2 `README.md`

Contenido propuesto (corto; el detalle vive en `docs/`):

```text
# Simulador de operación de TransMilenio (Portal Américas ↔ Portal Norte)
Una o dos líneas: qué es y para qué curso.

## Inicio rápido
  python -m venv .venv
  (activar: ver tabla en docs/instalacion.md)
  python -m pip install -r requirements.txt
  python -m pytest
  fastapi dev
  -> abrir http://127.0.0.1:8000/

## Documentación
- Paso a paso de instalación (Windows, macOS, Linux): docs/instalacion.md
- Contexto de la Fase 2: docs/contexto_fase2.md
- Descripción técnica: docs/descripcion.md
- Estructuras de datos: docs/explicacion_estructuras.md
- Manual de usuario: docs/manual_usuario.md
- Registro de uso de IA: docs/registro_uso_ia.md

## Estructura del proyecto
(árbol corto de la §1)

## Versión anterior (Tkinter)
  python -m pip install pillow
  python -m legacy.app

## Equipo
```

### 5.3 Trabajo con Git: todos en `main`, repartidos por archivos (decisión 6, actualizada el 19-nov)

**Idea:** `main` siempre debe funcionar (es lo que se entrega). Como el equipo es de tres y cada
uno tiene sus archivos, se trabaja **directo en `main`**. La rama `esqueleto` se usó solo para
las piezas P1–P6 (que dejaban el proyecto a medias) y se unió a `main` al terminar.

**Reparto (quién toca qué):**
| Archivos | Quién |
|---|---|
| `simulador/simulador.py` y los endpoints de `api/` | Solo **Nicolás** |
| `estructuras/` | Los tres (cada uno su archivo; avisar antes de tocar `estructuras/__init__.py`) |
| Todo lo demás (`web/`, `docs/`, configuración) | Nicolás, con ayuda del asistente |
| `docs/registro_uso_ia.md` | Lo actualiza Nicolás (Santiago y Pablo no lo editan directamente) |

**Rutina (comandos):**
```bash
# Antes de empezar a programar
git pull

# Al terminar
python -m pytest            # que no se rompa nada
git add <archivos>          # nombrar los archivos, no usar "git add ."
git commit -m "Heap: insertar y extraer mínimo con pruebas"
git push
```

Reglas mínimas:
1. Nunca `git push --force` sobre `main`.
2. No se sube nada con pruebas fallando (`python -m pytest` antes de cada `push`).
3. Usar `git add <archivos>` en vez de `git add .` para no subir cosas por accidente.
4. Si `git push` es rechazado porque otro subió algo antes: `git pull` y `git push` de nuevo.
5. Si aparece un conflicto y no se entiende, **parar y avisar**; resolverlo entre dos.
6. Para un cambio grande y arriesgado (p. ej. integrar el AVL en el simulador) se puede abrir una
   rama solo para eso, de forma opcional.

### 5.4 Actualización de `CLAUDE.md` (aprobada, decisión 10)

`CLAUDE.md` aún habla de Tkinter, `ventana.after()` y `ImageTk.PhotoImage`. Esas reglas pasan a
aplicar solo a `legacy/`. En la pieza P6 se reescriben para la web, por ejemplo:
- La API no tiene lógica de negocio: cada endpoint llama a un método del `Simulador`.
- La animación es del JS (con `requestAnimationFrame`, sin bloquear la página); el JS solo dibuja
  y manda órdenes.
- `estructuras/` y `simulador/` los escribe el equipo; el asistente revisa y **propone**
  correcciones, y las aplica solo con el visto bueno del equipo (decisión 11).
- Arranque con `fastapi dev`; endpoints con prefijo `/api/`.

Les mostraré el texto nuevo antes de guardarlo.

---

## 6. Cronograma del 17 al 28 de noviembre

> **Actualización (24-nov-2026):** la entrega se aplazó del jueves 26 al **sábado 28 de
> noviembre**. La tabla conserva el plan original día por día; cómo se reparten los dos días
> ganados (congelar funciones, ensayo general) lo decide el equipo.

Supuestos: ~3–4 horas por persona por día. El reparto de tareas lo define el grupo (decisión 8);
la columna "Quién" solo distingue lo que hace el equipo de lo que guía el asistente.

| Día | Fecha | Bloque | Tarea | Quién | Listo cuando… |
|---|---|---|---|---|---|
| Lun | 17-nov | 1 | Aprobar el plan (hecho). Nicolás prepara su máquina (`docs/preparar_maquina.md`) | Nicolás | Lista de verificación completa |
| Mar | 18-nov | 1 | Piezas P1–P6 (§7): carpetas, dependencias, esqueleto, docs. Santiago y Pablo siguen `docs/instalacion.md` | Asistente + Nicolás; los otros dos prueban | Los 3 ven "Conectado" en su navegador |
| Mar–Mié | 18–19 nov | 2 | Confirmar estaciones de la ruta (fuente oficial) y guardar el JSON en `datos/` | Equipo | JSON revisado a mano y citado |
| Mar–Vie | 18–21 nov | 3 | **Estructuras núcleo** con pruebas: heap, AVL, árbol de segmentos | **Equipo** (asistente revisa) | Pruebas propias pasando; complejidades en docstrings |
| Mié–Jue | 19–20 nov | 2 | Adaptar `Simulador` a estaciones reales y ruta ida/vuelta (`ColaCircular` de 2N) | **Nicolás** (dueño de `simulador.py`; asistente revisa) | Pruebas del simulador pasando |
| Jue–Sáb | 20–22 nov | 4 | API completa (endpoints `/api/...`) + mapa Leaflet + buses animados | Asistente, con revisión del equipo | Se ve la ruta y los buses moviéndose |
| Sáb–Lun | 22–24 nov | 5 | Integrar estructuras al simulador y mostrarlas en el panel | Equipo + asistente | Cada estructura se usa en algo visible |
| Lun | 24-nov | — | **Congelar funciones.** Solo arreglos de errores desde aquí | Equipo | `main` estable |
| Lun–Mar | 24–25 nov | 6 | Documentación, `registro_uso_ia.md`, video ≤ 5 min, ensayo de sustentación | Equipo | Video grabado; cada uno explica su estructura sin leer |
| Mié | 25-nov | 6 | Ensayo general y revisión final del repositorio | Equipo | Lista de entregables completa |
| **Sáb** | **28-nov** | — | **Entrega** (aplazada; antes era el jueves 26-nov) | — | — |

**Puntos de control** (si no se cumplen, se aplica el siguiente recorte):
- **Mié 19-nov noche:** los 3 con el entorno funcionando y la ruta en `datos/`.
- **Sáb 22-nov noche:** las 3 estructuras núcleo con pruebas y la API respondiendo con el simulador real.
- **Lun 24-nov noche:** todo integrado en `main`.

**Orden de recortes si vamos justos** (de primero a último):
1. Pulido visual: animación suave, colores, gráficas en vivo, diseño en celular.
2. Árbol B+ (extra).
3. Una de las estructuras núcleo (la que menos se vea en la demo; decisión del equipo).
4. Funciones extra de la interfaz (reiniciar con parámetros, deshacer desde la web).

**Nunca:** reemplazar una estructura propia por una librería (`heapq`, `bisect`, `sortedcontainers`…).

---

## 7. Orden de ejecución de este plan (piezas)

Cada pieza es un commit pequeño en una rama `esqueleto`, que al final se une a `main` con un solo
Pull Request. Pido su visto bueno antes de cada pieza. **Requisito previo:** haber completado
`docs/preparar_maquina.md`.

| Pieza | Qué hago | Archivos |
|---|---|---|
| **P1** | Mover la versión Tkinter a `legacy/` y comprobar que `python -m legacy.app` abre | `git mv app.py legacy/app.py`, `git mv imagenes legacy/imagenes` |
| **P2** | Nuevo `requirements.txt`, instalar en el `.venv` nuevo y correr las 132 pruebas actuales | `requirements.txt` |
| **P3** | Corregir `.gitignore` y sacar `.vscode/settings.json` del repositorio | `.gitignore` |
| **P4** | Esqueleto: API + web + pruebas de la API (§4), con comentarios didácticos, y `pyproject.toml` | `api/`, `web/`, `tests/test_api.py`, `datos/README.md`, `pyproject.toml` |
| **P5** | Paso a paso para los compañeros y README | `docs/instalacion.md`, `README.md` |
| **P6** | Registro de uso de IA y `CLAUDE.md` | `docs/registro_uso_ia.md`, `CLAUDE.md` |

Al final de P6: `pip freeze` para anotar versiones y unir `esqueleto` a `main`. **Hecho el 19-nov-2026** (unión local con `git merge --no-ff`, porque `gh` no está instalado; la rama se borró después).

---

## 8. Preguntas y decisiones pendientes

Las 12 preguntas de la primera versión ya se respondieron: ver
[Decisiones tomadas](#decisiones-tomadas-17-nov-2026). Quedan abiertas:

1. **Reparto de tareas** (estructuras núcleo, datos de la ruta): lo define el grupo.
2. **Servicio directo Portal Américas–Portal Norte y sus estaciones:** sigue por confirmar
   (pregunta 2 de `contexto_fase2.md`). Hace falta antes de llenar `datos/`.
3. **Texto nuevo de `CLAUDE.md`:** se les mostrará en la pieza P6 antes de guardarlo.
