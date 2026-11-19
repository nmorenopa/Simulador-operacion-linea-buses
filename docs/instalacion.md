# Instalación paso a paso (Fase 2)

> Para Santiago, Pablo y cualquiera que clone el proyecto. Funciona en **Windows 10/11**,
> **macOS** y **Linux**. Tarda unos 10 minutos.
>
> **Regla de oro:** todos los comandos se escriben **en la carpeta raíz del proyecto**
> (la que contiene `requirements.txt`).

---

## 0. Requisitos previos (una sola vez)

- **Git** instalado: `git --version` debe mostrar un número.
- **Python 3.11 o superior** (el equipo usa 3.14):
  - Windows: `py -0` lista los Python instalados (o `python --version`).
  - macOS / Linux: `python3 --version`.
  - En Windows, al instalar Python marquen **"Add python.exe to PATH"**.
  - En Linux (Ubuntu/Debian) puede faltar el módulo de entornos: `sudo apt install python3-venv`.
- Un navegador moderno (Chrome, Edge, Firefox o Safari).

> **¿Por qué 3.11?** FastAPI 0.163 exige Python 3.11 o más nuevo. Con uno más viejo, la
> instalación falla con `Requires-Python >=3.11`.

---

## 1. Traer el código

**Primera vez (no tienen la carpeta):**
```bash
git clone https://github.com/nmorenopa/Simulador-operacion-linea-buses.git
cd Simulador-operacion-linea-buses
```

**Ya tienen la carpeta (de la Fase 1):**
```bash
cd Simulador-operacion-linea-buses
git checkout main
git pull
```

> ⚠️ Al hacer este `git pull`, Git **borra su copia de `.vscode/settings.json`** (salió del
> repositorio porque cada quien configura su editor). Solo tenía ajustes de autocompletado.
> Si los quieren conservar, copien ese archivo a otra carpeta **antes** del pull.

---

## 2. Crear el entorno virtual

Un **entorno virtual** (`.venv`) es una carpeta con un Python "privado" del proyecto y sus
librerías, para no mezclarlas con las de otros proyectos. Cada integrante crea el suyo y
**no se sube a Git**.

Si ya tenían un `.venv` de la Fase 1, **bórrenlo y créenlo de nuevo** (trae librerías viejas
que ya no usamos). Antes, cierren las terminales de VS Code que lo tengan activado, o Windows
no dejará borrarlo.

| Sistema | Borrar el `.venv` viejo (si existe) | Crear el nuevo |
|---|---|---|
| Windows – Git Bash | `rm -rf .venv` | `py -3.14 -m venv .venv` |
| Windows – PowerShell | `Remove-Item -Recurse -Force .venv` | `py -3.14 -m venv .venv` |
| macOS / Linux | `rm -rf .venv` | `python3 -m venv .venv` |

> En Windows, `py -3.14` elige exactamente Python 3.14 aunque tengan varias versiones
> instaladas. Si `py` no existe, usen `python -m venv .venv` (comprobando antes que
> `python --version` sea 3.11 o más).

---

## 3. Activar el entorno virtual (cada vez que abran una terminal nueva)

| Sistema | Comando |
|---|---|
| Windows – Git Bash | `source .venv/Scripts/activate` |
| Windows – PowerShell | `.venv\Scripts\Activate.ps1` |
| Windows – cmd | `.venv\Scripts\activate.bat` |
| macOS / Linux (bash o zsh) | `source .venv/bin/activate` |

✅ Funcionó si la línea de la terminal empieza con **`(.venv)`**.
Desde aquí, en **todos** los sistemas se escribe `python` (ya no `py` ni `python3`).

**En VS Code:** `Ctrl + Shift + P` (`Cmd + Shift + P` en macOS) → **Python: Select Interpreter**
→ elijan el que dice `.venv`. Así las terminales nuevas lo activan solas.

---

## 4. Instalar las dependencias

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Usamos `python -m pip` en lugar de `pip` a secas para asegurarnos de que se instala en el
Python **del entorno virtual** y no en otro.

Qué se instala (ver `requirements.txt`): **FastAPI** (la API), **Uvicorn** (el servidor, viene
dentro de `fastapi[standard]` junto con el comando `fastapi dev`), **pytest** y **httpx**
(para las pruebas).

---

## 5. Correr las pruebas

```bash
python -m pytest
```

✅ Debe terminar con **`135 passed`** y nada en rojo.

---

## 6. Arrancar el servidor

```bash
fastapi dev
```

Cómo funciona este comando:
- `fastapi dev` lee en `pyproject.toml` la línea `entrypoint = "api.main:app"`:
  - `api.main` → el archivo `api/main.py` (los `/` se escriben como `.`).
  - `:app` → dentro de ese archivo, el objeto que se llama `app` (el `app = FastAPI(...)`).
- `dev` = modo desarrollo: arranca **Uvicorn** (el programa que escucha las peticiones) y
  **se reinicia solo** cada vez que guardan un archivo.

Equivalente "a mano", por si algún día falla `fastapi dev`:
```bash
python -m uvicorn api.main:app --reload
```

El servidor se queda corriendo y esa terminal queda "ocupada". Para detenerlo: **Ctrl + C**.

---

## 7. Abrir la página

Con el servidor corriendo, abran en el navegador:
- **http://127.0.0.1:8000/** → la página del proyecto.
- **http://127.0.0.1:8000/docs** → la documentación automática de la API (Swagger UI), con un
  botón para probar cada endpoint.

`127.0.0.1` significa "este mismo computador" y `8000` es el puerto por el que escucha el
servidor. Solo lo ven ustedes: no queda publicado en internet.

---

## 8. Lista de verificación

- [ ] `python --version` muestra **3.11 o superior**.
- [ ] La terminal muestra `(.venv)` al inicio de la línea.
- [ ] `python -m pip install -r requirements.txt` termina sin errores en rojo.
- [ ] `python -m pytest` → **`135 passed`**, 0 fallidas.
- [ ] Al arrancar el servidor aparece `Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)`.
- [ ] En `http://127.0.0.1:8000/` se ve el título y el mensaje **"Conectado: la API respondió"**.
- [ ] En `http://127.0.0.1:8000/docs`, `GET /api/salud` → *Try it out* → *Execute* responde **200**.
- [ ] En la terminal del servidor aparece `GET /api/salud ... 200 OK` cada vez que recargan la página.

---

## 9. Versión anterior (Tkinter)

La interfaz de la Fase 1 se conserva en `legacy/`. Necesita Pillow, que ya no está en
`requirements.txt`:

```bash
python -m pip install pillow
python -m legacy.app
```

El `-m` le dice a Python "ejecuta `legacy/app.py` partiendo de la carpeta actual", y así
encuentra `estructuras/` y `simulador/`. **`python app.py` ya no funciona** (el archivo se movió).

---

## 10. Trabajo diario con Git

Todos trabajamos en `main`. Reglas del equipo:

```bash
# Antes de empezar a programar
git pull

# Al terminar
python -m pytest            # que no se rompa nada
git add <archivos>          # nombrar los archivos, no usar "git add ."
git commit -m "Qué hice"
git push
```

Si `git push` es rechazado porque otro subió algo antes: `git pull` y luego `git push` de nuevo.
Si aparece un conflicto y no se entiende el mensaje, **paren y avisen** antes de forzar nada.

---

## 11. Problemas frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `python` no se reconoce (Windows) o abre la Microsoft Store | Python no está en el PATH, o Windows usa su "alias" de la tienda | Usar `py` en lugar de `python`, o reinstalar Python marcando "Add python.exe to PATH". Desactivar los alias en *Configuración → Aplicaciones → Alias de ejecución de aplicaciones* |
| `python3: command not found` (macOS) | Falta Python | Instalarlo desde python.org |
| PowerShell: "la ejecución de scripts está deshabilitada en este sistema" | Política de seguridad de PowerShell | Una sola vez: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` y volver a activar |
| `ensurepip is not available` (Linux) | Falta el paquete `venv` | `sudo apt install python3-venv` |
| `Remove-Item`/`rm` falla con *"being used by another process"* | Una terminal o VS Code tiene el `.venv` en uso | Cerrar las terminales (o VS Code) y repetir |
| `ERROR: ... Requires-Python >=3.11` al instalar | Python demasiado viejo | Instalar Python 3.11+ y crear el `.venv` de nuevo con ese Python |
| `ModuleNotFoundError: No module named 'fastapi'` | El entorno no está activado, o se instaló en otro Python | Activar `.venv` (debe verse `(.venv)`) y repetir el paso 4 |
| `ModuleNotFoundError: No module named 'api'` o `'simulador'` | El comando se ejecutó desde otra carpeta | `cd` a la raíz del proyecto (donde está `requirements.txt`) |
| `fastapi` no se reconoce como comando | El entorno no está activado o falta la instalación | Activar `.venv` y repetir el paso 4 |
| `[Errno 10048]` / `address already in use` | Ya hay otro servidor en el puerto 8000 (otra terminal abierta) | Cerrar la otra con Ctrl + C, o usar otro puerto: `fastapi dev --port 8001` |
| La página dice "No se pudo conectar con la API" | Abrieron `index.html` con doble clic (`file:///...`) o el servidor está apagado | Arrancar `fastapi dev` y abrir **siempre** `http://127.0.0.1:8000/` |
| Cambié el JS o el CSS y no veo el cambio | El navegador guardó una copia vieja (caché) | Recarga forzada: **Ctrl + Shift + R** (Windows/Linux) o **Cmd + Shift + R** (macOS) |
| `RuntimeError: Directory '...web' does not exist` | Falta la carpeta `web/` (pull incompleto) | `git pull` de nuevo y revisar que exista `web/index.html` |
| `No module named 'PIL'` al abrir `legacy` | Pillow no está instalado | `python -m pip install pillow` |
| `git pull` dice que hay cambios locales que se sobrescribirían | Modificaron archivos que también cambiaron en GitHub | `git status` para verlos; `git stash`, `git pull`, `git stash pop`. Si no entienden el mensaje, **paren y pregunten** |
| `git push` pide usuario y contraseña en la terminal | GitHub ya no acepta la contraseña normal | Usar la ventana de inicio de sesión del navegador (Git Credential Manager) o un *token* |
