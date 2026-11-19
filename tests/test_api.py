"""
Pruebas del esqueleto de la API (capa 3).

TestClient simula un navegador: hace peticiones a la app SIN arrancar el
servidor, así que estas pruebas corren con un simple "python -m pytest".
(TestClient necesita la librería httpx, que está en requirements.txt.)
"""

from fastapi.testclient import TestClient

from api.main import app

# Un solo cliente para todas las pruebas del archivo.
client = TestClient(app)


def test_salud_responde_ok():
    """GET /api/salud devuelve código 200 y estado "ok"."""
    respuesta = client.get("/api/salud")

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "ok"


def test_pagina_principal():
    """GET / entrega web/index.html (gracias a html=True en el mount)."""
    respuesta = client.get("/")

    assert respuesta.status_code == 200
    assert "Simulador TransMilenio" in respuesta.text


def test_api_no_la_tapa_la_web():
    """
    La web está montada en "/", que atrapa cualquier dirección. Si el mount
    se hubiera registrado ANTES que el endpoint, /api/salud devolvería un 404
    o un HTML en vez de nuestro JSON. Esta prueba confirma el orden correcto.
    """
    respuesta = client.get("/api/salud")

    assert respuesta.headers["content-type"].startswith("application/json")
    assert set(respuesta.json()) == {"estado", "mensaje", "version_python"}
