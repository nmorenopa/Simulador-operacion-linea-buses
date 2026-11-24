"""
Pruebas del esqueleto de la API (capa 3).

TestClient simula un navegador: hace peticiones a la app SIN arrancar el
servidor, así que estas pruebas corren con un simple "python -m pytest".
(TestClient necesita la librería httpx, que está en requirements.txt.)
"""

from fastapi.testclient import TestClient

# Importamos también "simulador": el MISMO objeto que usa la API, para
# comparar lo que responde cada endpoint con lo que dice el Simulador.
from api.main import app, simulador

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


# --- Pieza A1: consultar el Simulador ---------------------------------------
# Estas pruebas no dependen de cuántas paradas o buses haya, para que sigan
# valiendo cuando el Simulador pase a las estaciones reales.

def test_estado_responde_con_las_claves_esperadas():
    """
    GET /api/estado devuelve 200 y las claves que la web va a usar para
    dibujar. Si alguien cambia estado() en el Simulador, esta prueba avisa.
    """
    respuesta = client.get("/api/estado")

    assert respuesta.status_code == 200
    assert set(respuesta.json()) == {
        "minuto", "en_pausa", "paradas", "buses",
        "eventos", "historial", "ultima_accion",
    }


def test_estado_es_el_mismo_del_simulador():
    """
    La API no inventa ni calcula nada: entrega exactamente lo que devuelve
    Simulador.estado(), solo que convertido a JSON.
    """
    respuesta = client.get("/api/estado")

    assert respuesta.json() == simulador.estado()


def test_reporte_responde_con_las_claves_esperadas():
    """GET /api/reporte devuelve 200 y las claves del resumen."""
    respuesta = client.get("/api/reporte")

    assert respuesta.status_code == 200
    assert set(respuesta.json()) == {
        "minuto", "pasajeros_generados", "pasajeros_abordados",
        "pasajeros_esperando", "espera_promedio", "ocupacion_promedio", "buses",
    }


def test_reporte_es_el_mismo_del_simulador():
    """Igual que con el estado: la API solo traduce Simulador.reporte() a JSON."""
    respuesta = client.get("/api/reporte")

    assert respuesta.json() == simulador.reporte()


def test_consultar_no_cambia_nada():
    """
    Un GET solo consulta. Pedir el estado dos veces seguidas debe dar lo mismo:
    el reloj no avanza ni aparecen pasajeros por el simple hecho de mirar.
    """
    primera = client.get("/api/estado").json()
    segunda = client.get("/api/estado").json()

    assert primera == segunda
