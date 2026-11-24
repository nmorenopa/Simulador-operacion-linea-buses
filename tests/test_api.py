"""
Pruebas de la API (capa 3).

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


# --- Pieza A2: dar órdenes al Simulador (POST) -------------------------------
# Todas las pruebas comparten el MISMO simulador (el de api/main.py). Por eso:
#   1. Ninguna supone que empieza en el minuto 0: miden "antes" y "después".
#   2. Cada una deja el simulador como lo encontró (si pausa, reanuda al final).
#   3. Las de deshacer solo confían en la acción que ELLAS acaban de apilar,
#      que es la que queda en el tope de la Pila.

def test_avanzar_suma_un_minuto():
    """POST /api/avanzar mueve el reloj un minuto y devuelve el estado nuevo."""
    antes = client.get("/api/estado").json()["minuto"]

    respuesta = client.post("/api/avanzar")

    assert respuesta.status_code == 200
    assert respuesta.json()["minuto"] == antes + 1
    # Lo que devuelve es exactamente el estado del Simulador después del tick
    assert respuesta.json() == simulador.estado()


def test_pausar_detiene_el_reloj():
    """Con la simulación en pausa, avanzar no cambia el minuto."""
    respuesta = client.post("/api/pausar")
    assert respuesta.status_code == 200
    assert respuesta.json()["en_pausa"] is True

    minuto_en_pausa = respuesta.json()["minuto"]
    despues = client.post("/api/avanzar").json()
    assert despues["minuto"] == minuto_en_pausa

    client.post("/api/reanudar")   # se deja como estaba, para las demás pruebas


def test_reanudar_vuelve_a_mover_el_reloj():
    """Después de pausar y reanudar, avanzar vuelve a sumar un minuto."""
    client.post("/api/pausar")

    respuesta = client.post("/api/reanudar")
    assert respuesta.status_code == 200
    assert respuesta.json()["en_pausa"] is False

    antes = respuesta.json()["minuto"]
    assert client.post("/api/avanzar").json()["minuto"] == antes + 1


def test_agregar_bus_suma_un_bus():
    """POST /api/agregar-bus devuelve el estado (no el Bus) con un bus más."""
    antes = len(client.get("/api/estado").json()["buses"])

    respuesta = client.post("/api/agregar-bus")

    assert respuesta.status_code == 200
    assert len(respuesta.json()["buses"]) == antes + 1

    client.post("/api/deshacer")   # se quita el bus, para las demás pruebas


def test_deshacer_quita_el_bus_agregado():
    """
    Agregar un bus y deshacer SEGUIDOS (sin avanzar en medio, así el bus nuevo
    no alcanza a subir pasajeros) deja la flota como estaba.
    """
    antes = len(client.get("/api/estado").json()["buses"])
    client.post("/api/agregar-bus")

    respuesta = client.post("/api/deshacer")

    assert respuesta.status_code == 200
    assert set(respuesta.json()) == {"mensaje", "estado"}
    assert respuesta.json()["mensaje"] == "Se quitó el último bus agregado"
    assert len(respuesta.json()["estado"]["buses"]) == antes


def test_deshacer_devuelve_el_mensaje_del_simulador():
    """
    El mensaje no lo arma la API: es el texto que devuelve Simulador.deshacer().
    Deshacer una pausa reanuda la simulación y lo dice.
    """
    client.post("/api/pausar")

    respuesta = client.post("/api/deshacer").json()

    assert respuesta["mensaje"] == "Se reanudó la simulación"
    assert respuesta["estado"]["en_pausa"] is False


def test_get_a_una_ruta_post_no_hace_nada():
    """
    La barra del navegador siempre pide con GET. Como /api/avanzar solo acepta
    POST, la petición la termina atendiendo la web montada en "/", que busca un
    archivo "api/avanzar", no lo encuentra y responde 404. Lo importante: un
    GET nunca ejecuta la acción (el reloj no se mueve). Por eso los POST se
    prueban en /docs.
    """
    antes = client.get("/api/estado").json()["minuto"]

    respuesta = client.get("/api/avanzar")

    assert respuesta.status_code == 404
    assert client.get("/api/estado").json()["minuto"] == antes
