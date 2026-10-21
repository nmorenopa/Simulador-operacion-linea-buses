import pytest
from simulador.pasajero import Pasajero, PRIORIDAD_ALTA, PRIORIDAD_NORMAL
from estructuras.cola_prioridad import ColaPrioridad


def test_pasajero_nuevo_no_ha_abordado():
    p = Pasajero(1, 0, 2, PRIORIDAD_NORMAL, 5)
    assert p.minuto_abordaje is None
    assert p.tiempo_espera() is None


def test_es_prioritario():
    assert Pasajero(1, 0, 2, PRIORIDAD_ALTA, 0).es_prioritario()
    assert not Pasajero(2, 0, 2, PRIORIDAD_NORMAL, 0).es_prioritario()


def test_tiempo_espera():
    p = Pasajero(1, 0, 2, PRIORIDAD_NORMAL, 5)
    p.minuto_abordaje = 12
    assert p.tiempo_espera() == 7


def test_origen_igual_a_destino_lanza_error():
    with pytest.raises(ValueError):
        Pasajero(1, 3, 3, PRIORIDAD_NORMAL, 0)


def test_prioridad_invalida_lanza_error():
    with pytest.raises(ValueError):
        Pasajero(1, 0, 2, 7, 0)
    with pytest.raises(ValueError):
        Pasajero(1, 0, 2, True and "alta", 0)


def test_prioridad_alta_sale_primero_en_la_cola_con_prioridad():
    """Comprueba que las constantes concuerdan con ColaPrioridad."""
    cola = ColaPrioridad()
    normal = Pasajero(1, 0, 2, PRIORIDAD_NORMAL, 0)
    alto = Pasajero(2, 0, 2, PRIORIDAD_ALTA, 1)
    cola.encolar(normal, normal.prioridad)
    cola.encolar(alto, alto.prioridad)
    assert cola.desencolar() is alto
    assert cola.desencolar() is normal


def test_repr_incluye_datos_basicos():
    texto = repr(Pasajero(7, 1, 3, PRIORIDAD_ALTA, 4))
    assert "7" in texto and "prioritario" in texto