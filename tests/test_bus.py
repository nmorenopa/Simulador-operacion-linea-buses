import pytest
from estructuras.cola_circular import ColaCircular
from simulador.bus import Bus
from simulador.parada import Parada
from simulador.pasajero import Pasajero, PRIORIDAD_NORMAL


def ruta_de(n):
    paradas = [Parada(i, f"P{i}", 0.5) for i in range(n)]
    ruta = ColaCircular()
    for p in paradas:
        ruta.encolar(p)
    return paradas, ruta


def pasajero(id, origen, destino):
    return Pasajero(id, origen, destino, PRIORIDAD_NORMAL, 0)


def test_bus_nuevo_empieza_en_el_frente_de_su_ruta():
    paradas, ruta = ruta_de(3)
    bus = Bus(1, ruta, 10)
    assert bus.parada_actual is paradas[0]
    assert bus.cantidad_pasajeros() == 0
    assert bus.cupos_libres() == 10
    assert bus.ocupacion() == 0


def test_validaciones_del_constructor():
    _, ruta = ruta_de(3)
    with pytest.raises(ValueError):
        Bus(1, ruta, 0)
    with pytest.raises(ValueError):
        Bus(1, ColaCircular(), 10)


def test_subir_cupos_y_ocupacion():
    _, ruta = ruta_de(3)
    bus = Bus(1, ruta, 2)
    bus.subir(pasajero(1, 0, 1))
    assert bus.cupos_libres() == 1 and bus.ocupacion() == 0.5
    bus.subir(pasajero(2, 0, 2))
    assert bus.cupos_libres() == 0 and bus.ocupacion() == 1


def test_subir_con_bus_lleno_lanza_error():
    _, ruta = ruta_de(3)
    bus = Bus(1, ruta, 1)
    bus.subir(pasajero(1, 0, 1))
    with pytest.raises(ValueError):
        bus.subir(pasajero(2, 0, 2))


def test_bajar_en_solo_baja_a_los_de_ese_destino():
    _, ruta = ruta_de(4)
    bus = Bus(1, ruta, 10)
    for id, destino in [(1, 1), (2, 2), (3, 1), (4, 3), (5, 1)]:
        bus.subir(pasajero(id, 0, destino))
    assert bus.bajar_en(1) == 3          # consecutivos y separados: ninguno se salta
    assert bus.cantidad_pasajeros() == 2
    assert bus.total_transportados == 3
    assert bus.bajar_en(1) == 0
    assert [p.id for p in bus.pasajeros.mostrar()] == [2, 4]


def test_avanzar_recorre_la_ruta_y_da_la_vuelta():
    paradas, ruta = ruta_de(3)
    bus = Bus(1, ruta, 10)
    visitadas = []
    for _ in range(4):
        bus.avanzar()
        visitadas.append(bus.parada_actual.id)
    assert visitadas == [1, 2, 0, 1]


def test_dos_buses_con_rutas_propias_no_se_estorban():
    paradas, _ = ruta_de(3)
    rutas = []
    for _ in range(2):
        r = ColaCircular()
        for p in paradas:
            r.encolar(p)
        rutas.append(r)
    rutas[1].siguiente()                 # se rota ANTES de crear el bus
    b1, b2 = Bus(1, rutas[0], 5), Bus(2, rutas[1], 5)
    assert (b1.parada_actual.id, b2.parada_actual.id) == (0, 1)
    b1.avanzar()
    assert (b1.parada_actual.id, b2.parada_actual.id) == (1, 1)