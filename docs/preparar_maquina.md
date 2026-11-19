# Preparar la máquina de Nicolás antes de crear la arquitectura

> **Para quién:** Nicolás (Windows 10, Python 3.14). Es el computador donde el asistente va a crear
> la arquitectura de la Fase 2 (piezas P1 a P6 de `docs/plan_preparacion.md`).
> **Cuánto tarda:** unos 15 minutos.
> **Qué NO hace esta guía:** no crea carpetas nuevas, no cambia `requirements.txt` ni toca código.
> Solo deja el computador limpio y comprobado, para que si algo falla después sepamos que es por
> los cambios nuevos y no por algo que ya venía mal.
>
> Santiago y Pablo **no** necesitan esta guía: ellos seguirán `docs/instalacion.md`, que se crea
> en la pieza P5, cuando la arquitectura ya esté en GitHub.

Todos los comandos se escriben **en la carpeta raíz del proyecto**
(`C:\Users\W541\Desktop\Simulador-operacion-linea-buses`). Para cada paso hay versión para
**Git Bash** y para **PowerShell**; usen solo una de las dos, la que prefieran.

---

## Paso 1. Cerrar lo que pueda estar usando archivos del proyecto

Windows no deja borrar ni mover archivos que algún programa tiene abiertos. Antes de empezar:

- Cierren la ventana del simulador Tkinter si está abierta.
- En VS Code, cierren **todas las terminales** (icono de la papelera en el panel de terminal).
  Si alguna tenía el `.venv` activado, Windows no dejará borrarlo en el paso 4.
- Abran **una sola terminal nueva** en la carpeta del proyecto.

---

## Paso 2. Comprobar Git y Python

```bash
git --version
py -0
```

Qué debe verse:
- `git --version` → algo como `git version 2.xx...`.
- `py -0` lista los Python instalados. En su computador aparecen **3.14 y 3.13**. Usaremos el **3.14**.

> **¿Qué es `py`?** Es el "lanzador de Python" de Windows. Sirve para elegir una versión exacta
> cuando hay varias instaladas: `py -3.14` significa "usa Python 3.14". Así evitamos que el
> entorno virtual se cree, por accidente, con el 3.13.

Comprueben también que Git sabe quién eres (sale en cada commit):

```bash
git config user.name
git config user.email
```

Si alguno sale vacío:
```bash
git config --global user.name "Nicolás Moreno Parra"
git config --global user.email "su-correo@ejemplo.com"
```

---

## Paso 3. Guardar en Git los documentos que ya existen

Ahora mismo hay documentos **sin guardar en Git**: `CLAUDE.md` y `docs/registro_uso_ia.md`
(modificados), y `docs/contexto_fase2.md`, `docs/descripcion.md`, `docs/plan_preparacion.md` y
esta guía (nuevos). Los guardamos **antes** de que el asistente empiece, para que cada pieza
posterior quede como un cambio separado y fácil de revisar.

Como acordamos trabajar con Pull Requests, todo el trabajo de preparación va en **una rama
llamada `esqueleto`**, que al final se une a `main` con un solo PR.

**3.1 Comprobar que `main` está al día con GitHub**

```bash
git checkout main
git pull
git status
```

- `git pull` debe decir `Already up to date.` (o traer cambios sin errores).
- `git status` debe listar solo los documentos de arriba. **Si aparece cualquier otro archivo
  modificado, paren y avísenle al asistente** antes de seguir.

**3.2 Crear la rama y guardar los documentos**

```bash
git checkout -b esqueleto
git add CLAUDE.md docs/registro_uso_ia.md docs/contexto_fase2.md docs/descripcion.md docs/plan_preparacion.md docs/preparar_maquina.md
git commit -m "Docs: contexto de la Fase 2, descripción, plan de preparación y guía de la máquina"
git push -u origin esqueleto
```

Qué hace cada línea:
- `git checkout -b esqueleto` → crea la rama `esqueleto` a partir de `main` y se pasa a ella.
- `git add ...` → elige **exactamente** qué archivos entran en el commit (por eso no usamos `git add .`).
- `git commit -m "..."` → guarda una "foto" de esos archivos con un mensaje.
- `git push -u origin esqueleto` → sube la rama a GitHub. La primera vez puede abrirse una
  ventana para iniciar sesión en GitHub; acéptenla. El `-u` hace que los siguientes `git push`
  ya no necesiten el nombre de la rama.

✅ Al terminar, `git status` debe decir `On branch esqueleto` y `nothing to commit, working tree clean`.

---

## Paso 4. Borrar el entorno virtual viejo y crear uno nuevo con Python 3.14

El `.venv` actual tiene librerías de la Fase 1 que ya no usamos (por ejemplo altair y numpy, de
cuando la interfaz era Streamlit). Empezar con uno limpio evita errores raros.

**Git Bash**
```bash
rm -rf .venv
py -3.14 -m venv .venv
source .venv/Scripts/activate
```

**PowerShell**
```powershell
Remove-Item -Recurse -Force .venv
py -3.14 -m venv .venv
.venv\Scripts\Activate.ps1
```

- Si PowerShell dice *"la ejecución de scripts está deshabilitada en este sistema"*, ejecuten
  **una sola vez** `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` y
  vuelvan a activar.
- Si `rm` o `Remove-Item` dice que el archivo está en uso: volver al paso 1 (queda alguna terminal
  o programa usando el `.venv`).

Comprobar:
```bash
python --version
```
✅ La línea de la terminal empieza con `(.venv)` y la versión es **Python 3.14.x**.
Desde aquí ya se escribe `python` (no `py`), porque el entorno activado manda.

---

## Paso 5. Instalar las dependencias ACTUALES y medir la línea base

Todavía instalamos el `requirements.txt` **de la Fase 1** (pytest y Pillow). La idea es comprobar
que el proyecto funciona **tal como está hoy**; a esto se le llama **línea base**: el punto de
comparación para saber si un cambio posterior rompió algo.

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest -q
```

✅ La última línea de pytest debe decir **`132 passed`** (y nada en rojo).

Luego abran la versión Tkinter **una vez** para confirmar que se ve:

```bash
python app.py
```

✅ Se abre la ventana del simulador con el mapa y los buses. Ciérrenla.

> Si aparece algún error en este paso, **no sigan**: copien el mensaje completo y pásenselo al
> asistente. Es justo lo que la línea base quiere detectar.

---

## Paso 6. Decirle a VS Code que use el `.venv` nuevo

1. `Ctrl + Shift + P` → escriban **Python: Select Interpreter**.
2. Elijan el que dice `.venv` (ruta `.\.venv\Scripts\python.exe`).
3. Abran una terminal nueva en VS Code (`Ctrl + Ñ` o menú *Terminal → New Terminal*): debe salir
   `(.venv)` sola. Si no, actívenla como en el paso 4.

Esto hace que el editor marque bien los errores y encuentre las librerías que instalemos después.

---

## Paso 7. Lista de verificación final

- [ ] `py -0` muestra Python 3.14.
- [ ] `git config user.name` y `git config user.email` tienen valor.
- [ ] `git status` dice `On branch esqueleto` y `working tree clean`.
- [ ] La rama `esqueleto` aparece en GitHub (pestaña *Branches* del repositorio).
- [ ] La terminal muestra `(.venv)` y `python --version` dice 3.14.x.
- [ ] `python -m pytest -q` → `132 passed`.
- [ ] `python app.py` abre el simulador Tkinter.
- [ ] VS Code usa el intérprete `.venv`.

Cuando todo esté marcado, escríbanle al asistente: **"Máquina lista, empieza con P1"**.
A partir de ahí el asistente ejecuta las piezas P1 a P6 del plan, una por una y pidiendo
visto bueno en cada una:

| Pieza | Qué se hará |
|---|---|
| P1 | Mover `app.py` e `imagenes/` a `legacy/` |
| P2 | Nuevo `requirements.txt` (FastAPI, pytest, httpx) e instalación |
| P3 | Corregir `.gitignore` y sacar `.vscode/` del repositorio |
| P4 | Esqueleto: `api/`, `web/`, `datos/`, `tests/test_api.py`, `pyproject.toml` |
| P5 | `docs/instalacion.md` para Santiago y Pablo, y README nuevo |
| P6 | Actualizar `docs/registro_uso_ia.md` y `CLAUDE.md` |

---

## Problemas frecuentes en esta preparación

| Síntoma | Causa probable | Solución |
|---|---|---|
| `py` no se reconoce | El lanzador de Python no se instaló | Usar `python --version`; si dice 3.14, cambiar `py -3.14` por `python` en el paso 4 |
| `git pull` dice *"Your local changes would be overwritten"* | Alguien cambió en GitHub los mismos documentos | No forzar nada: copiar el mensaje y avisar al asistente |
| `git push` pide usuario y contraseña en la terminal | GitHub ya no acepta la contraseña normal | Usar la ventana de inicio de sesión del navegador (Git Credential Manager) o un *token*; avisar si no aparece |
| `git commit` dice *"Please tell me who you are"* | Falta el nombre o el correo | Paso 2, `git config --global ...` |
| `Remove-Item`/`rm` falla con *"being used by another process"* | Una terminal o VS Code tiene el `.venv` en uso | Cerrar terminales (paso 1) o cerrar VS Code y repetir |
| pytest dice `No module named pytest` | El `.venv` no está activado | Activarlo (paso 4) y repetir el paso 5 |
| `python app.py` dice `No module named 'PIL'` | Pillow no se instaló | `python -m pip install -r requirements.txt` con el `.venv` activo |
| Las pruebas no dan 132 | Algo cambió en el código desde el commit `80003fb` | Copiar la salida de pytest y pasársela al asistente |
