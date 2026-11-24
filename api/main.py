"""
Capa 3: la API (la "ventanilla" del simulador).

Esta capa SOLO traduce: recibe una petición del navegador, llama a un método
del Simulador y devuelve su resultado como JSON. Aquí nunca va lógica de
negocio (si aparece un "if" sobre buses o pasajeros, está en el lugar
equivocado: eso pertenece a simulador/).

Endpoints actuales:
    GET /api/salud    -> comprueba que navegador, servidor y Python se hablan.
    GET /api/estado   -> Simulador.estado()   (foto del momento, para dibujar)
    GET /api/reporte  -> Simulador.reporte()  (resumen con promedios)

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

# Simulador: la capa 2. La API (capa 3) solo conoce la capa de abajo; nunca
# importa nada de estructuras/ directamente.
from simulador.simulador import Simulador


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


# --- 4. El único Simulador en memoria ---------------------------------------

# Por ahora usamos los mismos valores que la versión Tkinter (legacy/app.py),
# con 8 paradas genéricas. Cuando el Simulador se adapte a las estaciones
# reales (Bloque 2), lo único que cambia en la API es esta parte.
NUMERO_PARADAS = 8
NUMERO_BUSES = 5
CAPACIDAD_BUS = 10
TASA_LLEGADA = 0.5              # probabilidad de que llegue un pasajero en cada sorteo
PROBABILIDAD_PRIORITARIO = 0.5
INTENTOS_LLEGADA = 3            # sorteos por parada y minuto: llegan de 0 a 3 pasajeros
SEMILLA = 42                    # con la misma semilla, la simulación se repite igual

# Esta variable se crea UNA sola vez, cuando el servidor carga este archivo, y
# todas las peticiones de todos los navegadores usan el mismo objeto. Por eso
# el estado se conserva entre una petición y la siguiente: es "el" simulador.
#
# Ojo: vive en la memoria del servidor. Si el servidor se reinicia (con
# "fastapi dev" pasa cada vez que se guarda un archivo), vuelve al minuto 0.
simulador = Simulador(
    numero_paradas=NUMERO_PARADAS,
    numero_buses=NUMERO_BUSES,
    capacidad_bus=CAPACIDAD_BUS,
    tasa_llegada=TASA_LLEGADA,
    probabilidad_prioritario=PROBABILIDAD_PRIORITARIO,
    semilla=SEMILLA,
    intentos_llegada=INTENTOS_LLEGADA,
)


# --- 5. Endpoints (SIEMPRE antes del mount del paso 6) ----------------------

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


# Fíjate en la forma de los dos endpoints siguientes: UNA línea que llama a un
# método del Simulador y devuelve su resultado. Esa es la regla de la API: si
# aquí apareciera un cálculo o un "if" sobre buses, iría en simulador/.
#
# Son GET porque solo CONSULTAN: pedirlos mil veces no cambia la simulación
# (la prueba test_consultar_no_cambia_nada lo comprueba).

@app.get("/api/estado")
def ver_estado():
    """
    Foto del momento: minuto, pausa, paradas, buses, eventos del último minuto
    e historial. Es lo que la web usa para dibujar. O(P + B).
    """
    return simulador.estado()


@app.get("/api/reporte")
def ver_reporte():
    """
    Resumen de lo ocurrido: pasajeros generados, abordados y esperando,
    espera promedio y ocupación promedio. O(P + T).
    """
    return simulador.reporte()


# --- 6. Servir la página web (SIEMPRE AL FINAL) -----------------------------

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
