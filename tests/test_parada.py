import pytest
from estructuras.cola_circular import ColaCircular
from simulador.bus import Bus
from simulador.parada import Parada
from simulador.pasajero import Pasajero, PRIORIDAD_ALTA, PRIORIDAD_NORMAL


def bus_con_capacidad(capacidad, parada):
    ruta = ColaCircular()
    ruta.encolar(parada)
    ruta.encolar(Parada(99, "otra", 0.1))
    return Bus(1, ruta, capacidad)


def pas(id, prioridad, llegada=0):
    return Pasajero(id, 0, 1, prioridad, llegada)


def test_parada_nueva():
    p = Parada(0, "Centro", 0.3)
    assert p.esperando() == 0
    assert p.total_llegados == 0 and p.total_abordados == 0 and p.suma_espera == 0


def test_tasa_de_llegada_invalida():
    with pytest.raises(ValueError):
        Parada(0, "Centro", 1.5)


def test_recibir_cuenta_llegados_y_esperando():
    p = Parada(0, "Centro", 0.3)
    p.recibir(pas(1, PRIORIDAD_NORMAL))
    p.recibir(pas(2, PRIORIDAD_NORMAL))
    assert p.esperando() == 2 and p.total_llegados == 2


def test_abordar_sube_prioritarios_primero_y_respeta_cupo():
    p = Parada(0, "Centro", 0.3)
    p.recibir(pas(1, PRIORIDAD_NORMAL))
    p.recibir(pas(2, PRIORIDAD_NORMAL))
    p.recibir(pas(3, PRIORIDAD_ALTA))
    bus = bus_con_capacidad(2, p)
    assert p.abordar(bus, 5) == 2
    abordo = [x.id for x in bus.pasajeros.mostrar()]
    assert abordo == [3, 1]                      # el prioritario y el normal más antiguo
    assert p.esperando() == 1                    # el 2 se queda
    assert p.total_abordados == 2


def test_los_que_no_caben_conservan_el_orden_de_llegada():
    p = Parada(0, "Centro", 0.3)
    for i in range(1, 5):
        p.recibir(pas(i, PRIORIDAD_NORMAL))
    bus = bus_con_capacidad(1, p)
    p.abordar(bus, 0)
    assert [p.fila.desencolar().id for _ in range(3)] == [2, 3, 4]


def test_abordar_registra_minuto_y_espera():
    p = Parada(0, "Centro", 0.3)
    p.recibir(pas(1, PRIORIDAD_NORMAL, llegada=2))
    p.recibir(pas(2, PRIORIDAD_NORMAL, llegada=4))
    bus = bus_con_capacidad(5, p)
    p.abordar(bus, 10)
    assert [x.minuto_abordaje for x in bus.pasajeros.mostrar()] == [10, 10]
    assert p.suma_espera == (10 - 2) + (10 - 4)


def test_abordar_con_bus_lleno_o_fila_vacia_no_sube_a_nadie():
    p = Parada(0, "Centro", 0.3)
    bus = bus_con_capacidad(1, p)
    assert p.abordar(bus, 0) == 0                # fila vacía
    p.recibir(pas(1, PRIORIDAD_NORMAL))
    p.recibir(pas(2, PRIORIDAD_NORMAL))
    bus.subir(pas(9, PRIORIDAD_NORMAL))          # bus lleno
    assert p.abordar(bus, 0) == 0
    assert p.esperando() == 2


def test_contador_de_prioritarios_sube_al_recibir_y_baja_al_abordar():
    p = Parada(0, "Centro", 0.3)
    p.recibir(pas(1, PRIORIDAD_NORMAL))
    p.recibir(pas(2, PRIORIDAD_ALTA))
    p.recibir(pas(3, PRIORIDAD_ALTA))
    assert p.prioritarios_esperando == 2
    bus = bus_con_capacidad(1, p)
    p.abordar(bus, 0)                            # sube un prioritario
    assert p.prioritarios_esperando == 1 and p.esperando() == 2
    bus2 = bus_con_capacidad(5, p)
    p.abordar(bus2, 1)
    assert p.prioritarios_esperando == 0 and p.esperando() == 0