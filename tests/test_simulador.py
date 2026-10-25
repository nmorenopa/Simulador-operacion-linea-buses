import pytest
from simulador.simulador import Simulador
from simulador.pasajero import Pasajero, PRIORIDAD_ALTA, PRIORIDAD_NORMAL


def crear(paradas=4, buses=2, capacidad=10, tasa=0.5, prob=0.2, semilla=1):
    return Simulador(paradas, buses, capacidad, tasa, prob, semilla)


def ids_de_parada_de_buses(sim):
    return [sim.buses.posicion(i).parada_actual.id for i in range(sim.buses.longitud())]


def total_en_sistema(sim):
    """Pasajeros esperando + a bordo + que ya bajaron."""
    e = sum(sim.paradas.posicion(i).esperando() for i in range(sim.paradas.longitud()))
    a = sum(sim.buses.posicion(i).cantidad_pasajeros() for i in range(sim.buses.longitud()))
    b = sum(sim.buses.posicion(i).total_transportados for i in range(sim.buses.longitud()))
    return e + a + b


# ---------------------------- constructor ----------------------------
def test_crea_las_paradas_y_buses_pedidos():
    sim = crear(paradas=5, buses=3)
    assert sim.paradas.longitud() == 5 and sim.buses.longitud() == 3
    assert [sim.paradas.posicion(i).id for i in range(5)] == [0, 1, 2, 3, 4]
    assert sim.minuto == 0 and not sim.en_pausa and sim.historial.esta_vacia()


def test_los_buses_arrancan_repartidos_con_la_formula_de_rotaciones():
    assert ids_de_parada_de_buses(crear(paradas=4, buses=2)) == [0, 2]
    assert ids_de_parada_de_buses(crear(paradas=10, buses=4)) == [0, 2, 5, 7]


def test_cada_bus_tiene_su_propia_ruta():
    sim = crear(buses=3)
    rutas = [sim.buses.posicion(i).ruta for i in range(3)]
    assert rutas[0] is not rutas[1] and rutas[1] is not rutas[2]


@pytest.mark.parametrize("kwargs", [
    dict(paradas=1), dict(buses=0), dict(capacidad=0),
    dict(tasa=1.5), dict(tasa=-0.1), dict(prob=2),
])
def test_parametros_invalidos_lanzan_error(kwargs):
    with pytest.raises(ValueError):
        crear(**kwargs)


# ---------------------------- llegadas ----------------------------
def test_con_tasa_1_llega_un_pasajero_por_parada_y_por_tick():
    sim = crear(paradas=3, buses=1, tasa=1)
    sim._generar_llegadas()
    assert [sim.paradas.posicion(i).esperando() for i in range(3)] == [1, 1, 1]


@pytest.mark.parametrize("intentos", [0, -1, 2.5, "3", None])
def test_intentos_llegada_invalidos_lanzan_error(intentos):
    with pytest.raises(ValueError):
        Simulador(4, 2, 10, 0.5, 0.2, 1, intentos_llegada=intentos)


@pytest.mark.parametrize("extra", [{}, {"intentos_llegada": 1}])
def test_con_un_intento_la_simulacion_es_igual_que_antes(extra):
    # Valores tomados con el código ANTES de agregar intentos_llegada (misma semilla).
    sim = Simulador(5, 2, 4, 0.6, 0.3, 123, **extra)
    for _ in range(50):
        sim.avanzar_tick()
    assert sim.reporte() == {
        "minuto": 50, "pasajeros_generados": 143, "pasajeros_abordados": 136,
        "pasajeros_esperando": 7, "espera_promedio": 1.8088235294117647,
        "ocupacion_promedio": 0.845, "buses": 2,
    }
    assert [sim.paradas.posicion(i).esperando() for i in range(5)] == [0, 0, 1, 0, 6]
    assert sim.serie_esperando.mostrar() == [
        2, 3, 3, 1, 2, 5, 4, 3, 4, 3, 2, 2, 3, 4, 3, 4, 5, 6, 5, 8, 6, 6, 4, 5, 8,
        9, 9, 7, 8, 12, 10, 8, 7, 6, 8, 6, 6, 6, 7, 6, 5, 5, 6, 7, 8, 8, 8, 9, 9, 7,
    ]


def test_con_3_intentos_y_tasa_1_llegan_3_por_parada():
    sim = Simulador(4, 1, 10, 1.0, 0.2, 1, intentos_llegada=3)
    sim._generar_llegadas()
    assert [sim.paradas.posicion(i).esperando() for i in range(4)] == [3, 3, 3, 3]


def test_nunca_llegan_mas_de_k_por_parada_en_un_tick():
    k = 3
    sim = Simulador(5, 1, 10, 0.7, 0.2, 7, intentos_llegada=k)
    for _ in range(200):
        antes = [sim.paradas.posicion(i).total_llegados for i in range(5)]
        sim.avanzar_tick()
        despues = [sim.paradas.posicion(i).total_llegados for i in range(5)]
        assert all(0 <= d - a <= k for a, d in zip(antes, despues))


def test_con_tasa_0_no_llega_nadie():
    sim = crear(tasa=0)
    for _ in range(20):
        sim.avanzar_tick()
    assert total_en_sistema(sim) == 0


def test_destinos_siempre_validos_y_distintos_del_origen():
    sim = crear(paradas=4, buses=1, tasa=1, semilla=3)
    for _ in range(50):
        sim._generar_llegadas()
    for i in range(4):
        fila = sim.paradas.posicion(i).fila
        while not fila.esta_vacia():
            p = fila.desencolar()
            assert p.origen == i and p.destino != i and 0 <= p.destino < 4


def test_ids_de_pasajero_unicos():
    sim = crear(tasa=1, buses=1)
    for _ in range(5):
        sim._generar_llegadas()
    ids = []
    for i in range(sim.paradas.longitud()):
        fila = sim.paradas.posicion(i).fila
        while not fila.esta_vacia():
            ids.append(fila.desencolar().id)
    assert len(ids) == len(set(ids)) == 20


def test_probabilidad_de_prioritarios_en_los_extremos():
    for prob, esperado in [(1, PRIORIDAD_ALTA), (0, PRIORIDAD_NORMAL)]:
        sim = crear(tasa=1, prob=prob, buses=1)
        sim._generar_llegadas()
        assert sim.paradas.posicion(0).fila.frente().prioridad == esperado


def test_misma_semilla_misma_simulacion():
    a, b = crear(semilla=42), crear(semilla=42)
    for _ in range(30):
        a.avanzar_tick()
        b.avanzar_tick()
    assert a.estado() == b.estado() and a.reporte() == b.reporte()


# ---------------------------- tick ----------------------------
def test_cada_tick_avanza_el_reloj_y_los_buses_una_parada():
    sim = crear(paradas=4, buses=2, tasa=0)
    sim.avanzar_tick()
    assert sim.minuto == 1
    assert ids_de_parada_de_buses(sim) == [1, 3]
    for _ in range(3):
        sim.avanzar_tick()
    assert ids_de_parada_de_buses(sim) == [0, 2]          # dio la vuelta completa


def test_no_se_pierden_ni_se_inventan_pasajeros():
    sim = crear(paradas=5, buses=2, capacidad=4, tasa=0.6)
    generados = 0
    for _ in range(200):
        sim.avanzar_tick()
        generados = sim.reporte()["pasajeros_generados"]
        assert total_en_sistema(sim) == generados


def test_llegan_pasajeros_a_su_destino():
    sim = crear(paradas=4, buses=2, capacidad=10, tasa=0.3)
    for _ in range(100):
        sim.avanzar_tick()
    assert sum(sim.buses.posicion(i).total_transportados for i in range(2)) > 0


def test_nunca_se_supera_la_capacidad_del_bus():
    sim = crear(paradas=3, buses=1, capacidad=2, tasa=1)
    for _ in range(50):
        sim.avanzar_tick()
        assert sim.buses.posicion(0).cantidad_pasajeros() <= 2


def test_en_pausa_no_pasa_nada():
    sim = crear()
    sim.avanzar_tick()
    sim.pausar()
    antes = sim.estado()
    for _ in range(5):
        sim.avanzar_tick()
    despues = sim.estado()
    assert sim.minuto == 1
    assert despues["paradas"] == antes["paradas"] and despues["buses"] == antes["buses"]
    assert despues["eventos"] == []          # en pausa no ocurre nada que animar


def test_las_series_guardan_una_muestra_por_tick():
    sim = crear()
    for _ in range(7):
        sim.avanzar_tick()
    assert sim.serie_esperando.longitud() == 7 and sim.serie_ocupacion.longitud() == 7


# ---------------------------- acciones y deshacer ----------------------------
def test_agregar_bus_y_deshacer():
    sim = crear(buses=2)
    sim.agregar_bus()
    assert sim.buses.longitud() == 3
    assert sim.deshacer() == "Se quitó el último bus agregado"
    assert sim.buses.longitud() == 2 and sim.historial.esta_vacia()


def test_bus_nuevo_arranca_en_la_parada_mas_llena():
    sim = crear(paradas=4, buses=1, tasa=0)
    for n in range(3):
        sim.paradas.posicion(2).recibir(Pasajero(n, 2, 0, PRIORIDAD_NORMAL, 0))
    bus = sim.agregar_bus()
    assert bus.parada_actual.id == 2 and bus.id == 1


def test_pausar_reanudar_y_deshacer_en_orden_inverso():
    sim = crear()
    sim.pausar()
    sim.reanudar()
    assert not sim.en_pausa
    assert sim.deshacer() == "Se volvió a pausar la simulación" and sim.en_pausa
    assert sim.deshacer() == "Se reanudó la simulación" and not sim.en_pausa


def test_pausar_dos_veces_no_ensucia_el_historial():
    sim = crear()
    sim.pausar()
    sim.pausar()
    assert sim.historial.longitud() == 1


def test_deshacer_sin_acciones_devuelve_none():
    assert crear().deshacer() is None


def test_no_se_deshace_un_bus_con_pasajeros_y_la_accion_se_conserva():
    sim = crear(buses=1)
    bus = sim.agregar_bus()
    bus.subir(Pasajero(1, 0, 1, PRIORIDAD_NORMAL, 0))
    assert "No se puede deshacer" in sim.deshacer()
    assert sim.buses.longitud() == 2 and sim.historial.longitud() == 1
    bus.bajar_en(1)
    assert sim.deshacer() == "Se quitó el último bus agregado"


# ---------------------------- estado y reporte ----------------------------
def test_estado_tiene_los_datos_para_la_interfaz():
    sim = crear(paradas=3, buses=2)
    e = sim.estado()
    assert e["minuto"] == 0 and e["en_pausa"] is False
    assert len(e["paradas"]) == 3 and len(e["buses"]) == 2
    assert set(e["buses"][0]) == {"id", "parada", "pasajeros", "capacidad", "ocupacion"}


def test_estado_al_inicio_tiene_historial_vacio():
    e = crear().estado()
    assert e["historial"] == 0 and e["ultima_accion"] is None


def test_estado_informa_el_tope_de_la_pila_sin_sacarlo():
    sim = crear()
    sim.pausar()
    assert sim.estado()["historial"] == 1 and sim.estado()["ultima_accion"] == "pausar"
    sim.reanudar()
    sim.agregar_bus()
    e = sim.estado()
    assert e["historial"] == 3 and e["ultima_accion"] == "agregar_bus"
    assert sim.historial.longitud() == 3          # consultar estado() no cambia la Pila
    sim.deshacer()
    e = sim.estado()
    assert e["historial"] == 2 and e["ultima_accion"] == "reanudar"


def test_estado_conserva_la_accion_que_no_se_pudo_deshacer():
    sim = crear(buses=1)
    bus = sim.agregar_bus()
    bus.subir(Pasajero(1, 0, 1, PRIORIDAD_NORMAL, 0))
    sim.deshacer()
    e = sim.estado()
    assert e["historial"] == 1 and e["ultima_accion"] == "agregar_bus"


def test_reporte_al_inicio_no_divide_entre_cero():
    r = crear().reporte()
    assert r["espera_promedio"] == 0.0 and r["ocupacion_promedio"] == 0.0
    assert r["pasajeros_generados"] == 0 and r["buses"] == 2


def test_reporte_coherente_despues_de_simular():
    sim = crear(paradas=4, buses=2, tasa=0.5)
    for _ in range(100):
        sim.avanzar_tick()
    r = sim.reporte()
    assert r["minuto"] == 100
    assert r["pasajeros_abordados"] <= r["pasajeros_generados"]
    assert r["pasajeros_esperando"] <= r["pasajeros_generados"]
    assert r["espera_promedio"] >= 0 and 0 <= r["ocupacion_promedio"] <= 1


# ---------------------------- eventos y prioritarios (para animar la interfaz) ----------------------------
CAMPOS_EVENTO = {"bus", "parada", "bajaron", "esperando_antes", "prioritarios_antes", "cupos_antes",
                 "subieron", "prioritarios_subieron", "esperando_despues", "a_bordo", "siguiente_parada"}


def prioritarios_reales(parada):
    """Cuenta recorriendo la fila (sin usar el contador) cuántos prioritarios hay."""
    total = 0
    for k in range(parada.fila.cantidad_niveles):
        nodo = parada.fila.niveles.posicion(k).frente   # Cola de cada nivel
        while nodo is not None:
            if nodo.dato.es_prioritario():
                total += 1
            nodo = nodo.siguiente
    return total


def test_hay_un_evento_por_bus_en_cada_tick():
    sim = crear(buses=3)
    assert sim.eventos.longitud() == 0           # antes del primer tick no hay nada
    sim.avanzar_tick()
    assert sim.eventos.longitud() == 3
    assert [e["bus"] for e in sim.eventos.mostrar()] == [0, 1, 2]
    assert all(set(e) == CAMPOS_EVENTO for e in sim.eventos.mostrar())


def test_los_eventos_se_reemplazan_en_cada_tick():
    sim = crear(buses=2)
    sim.avanzar_tick()
    sim.avanzar_tick()
    assert sim.eventos.longitud() == 2           # solo los del último tick, no acumulados


def test_los_eventos_son_coherentes_con_lo_que_paso():
    sim = crear(paradas=5, buses=3, capacidad=4, tasa=0.7, prob=0.3, semilla=11)
    for _ in range(150):
        antes = [sim.buses.posicion(i).parada_actual.id for i in range(sim.buses.longitud())]
        sim.avanzar_tick()
        for e in sim.eventos.mostrar():
            assert e["parada"] == antes[e["bus"]]                       # parada donde abordó
            assert e["siguiente_parada"] == (e["parada"] + 1) % 5       # la ruta es circular
            assert 0 <= e["subieron"] <= e["cupos_antes"]               # nunca más que los cupos
            assert e["subieron"] <= e["esperando_antes"]
            assert e["esperando_despues"] == e["esperando_antes"] - e["subieron"]
            assert 0 <= e["prioritarios_subieron"] <= e["subieron"]
            assert e["a_bordo"] <= 4


def test_los_prioritarios_suben_primero_en_los_eventos():
    sim = crear(paradas=3, buses=1, capacidad=2, tasa=0, semilla=1)
    parada = sim.paradas.posicion(0)
    for n, prio in enumerate([PRIORIDAD_NORMAL, PRIORIDAD_NORMAL, PRIORIDAD_ALTA, PRIORIDAD_ALTA]):
        parada.recibir(Pasajero(n, 0, 1, prio, 0))
    sim.avanzar_tick()
    e = sim.eventos.posicion(0)
    assert e["esperando_antes"] == 4 and e["prioritarios_antes"] == 2
    assert e["subieron"] == 2 and e["prioritarios_subieron"] == 2       # sube la pareja prioritaria
    assert e["esperando_despues"] == 2 and parada.prioritarios_esperando == 0


def test_estado_incluye_prioritarios_y_eventos():
    sim = crear(paradas=3, buses=1, tasa=0)
    sim.paradas.posicion(1).recibir(Pasajero(0, 1, 0, PRIORIDAD_ALTA, 0))
    sim.paradas.posicion(1).recibir(Pasajero(1, 1, 2, PRIORIDAD_NORMAL, 0))
    e = sim.estado()
    assert e["paradas"][1]["esperando"] == 2 and e["paradas"][1]["prioritarios"] == 1
    assert e["eventos"] == []
    sim.avanzar_tick()
    assert len(sim.estado()["eventos"]) == 1


def test_el_contador_de_prioritarios_coincide_con_la_fila_real():
    sim = crear(paradas=4, buses=2, capacidad=3, tasa=0.8, prob=0.4, semilla=9)
    for _ in range(200):
        sim.avanzar_tick()
        for i in range(sim.paradas.longitud()):
            parada = sim.paradas.posicion(i)
            assert parada.prioritarios_esperando == prioritarios_reales(parada)


def test_el_reloj_avanza_un_minuto_por_tick():
    sim = crear()
    for esperado in range(1, 6):
        sim.avanzar_tick()
        assert sim.minuto == esperado