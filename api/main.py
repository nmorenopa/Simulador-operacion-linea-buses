"""
Capa 3: la API (la "ventanilla" del simulador).

Esta capa SOLO traduce: recibe una petición del navegador, llama a un método
del Simulador y devuelve su resultado como JSON. Aquí nunca va lógica de
negocio (si aparece un "if" sobre buses o pasajeros, está en el lugar
equivocado: eso pertenece a simulador/).

Por ahora es un esqueleto: solo tiene el endpoint /api/salud para comprobar
que el navegador, el servidor y Python están conectados. El Simulador se
conecta en el Bloque 4.

Cómo arrancarla (desde la raíz del proyecto, con el .venv activo):
    fastapi dev
"""

# --- 1. Importaciones -------------------------------------------------------

# platform: módulo estándar de Python. Lo usamos solo para devolver la versión
# de Python que corre el servidor (un dato real, no inventado).
import platform

# Path: para armar rutas de carpetas sin preocuparnos por "/" o "\".
from pathlib import Path

# FastAPI: la clase que representa toda nuestra aplicación web.
from fastapi import FastAPI

# StaticFiles: sirve archivos "tal cual" (html, css, js, imágenes).
from fastapi.staticfiles import StaticFiles


# --- 2. Ubicación de la carpeta web/ ----------------------------------------

# Path(__file__) es la ubicación de ESTE archivo (api/main.py).
# .resolve() la vuelve una ruta completa; .parent sube una carpeta (a api/)
# y el segundo .parent sube otra (a la raíz del proyecto).
# Así encontramos web/ sin importar desde qué carpeta se lance el comando
# (es la misma idea que usaba app.py para encontrar sus imágenes).
CARPETA_PROYECTO = Path(__file__).resolve().parent.parent
CARPETA_WEB = CARPETA_PROYECTO / "web"


# --- 3. Crear la aplicación -------------------------------------------------

# "app" es el nombre que aparece en pyproject.toml (api.main:app).
# title y description se muestran en la página automática /docs.
app = FastAPI(
    title="Simulador TransMilenio",
    description="API del simulador Portal Américas ↔ Portal Norte (Fase 2).",
)


# --- 4. Endpoints (SIEMPRE antes del mount del paso 5) ----------------------

# El decorador @app.get(...) significa: "cuando llegue una petición GET a
# /api/salud, ejecuta la función de abajo".
# GET = "dame información" (no cambia nada en el servidor).
# El prefijo /api/ separa las direcciones de la API de las de la página.
@app.get("/api/salud")
def salud():
    """Comprueba que la API está viva. Complejidad: O(1)."""
    # Devolvemos un diccionario normal de Python; FastAPI lo convierte
    # a JSON automáticamente antes de enviarlo al navegador.
    return {
        "estado": "ok",
        "mensaje": "La API del simulador está funcionando",
        "version_python": platform.python_version(),
    }


# --- 5. Servir la página web (SIEMPRE AL FINAL) -----------------------------

# app.mount conecta una "sub-aplicación" completa en una ruta. Aquí, todo lo
# que está en web/ queda disponible desde "/":
#   http://127.0.0.1:8000/            -> web/index.html
#   http://127.0.0.1:8000/js/main.js  -> web/js/main.js
# html=True: al pedir una carpeta (como "/") entrega su index.html.
#
# ¿Por qué al final? FastAPI revisa las rutas en el orden en que se
# registraron. "/" atrapa cualquier dirección, así que si estuviera antes
# se "comería" las peticiones a /api/... La prueba
# test_api_no_la_tapa_la_web (tests/test_api.py) comprueba este orden.
app.mount("/", StaticFiles(directory=CARPETA_WEB, html=True), name="web")
