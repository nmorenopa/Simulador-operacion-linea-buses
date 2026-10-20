from estructuras.cola_circular import ColaCircular


def test_cola_nueva_esta_vacia():
    cola = ColaCircular()
    assert cola.esta_vacia()
    assert cola.tamano() == 0
    assert cola.frente() is None


def test_un_solo_nodo_se_apunta_a_si_mismo():
    cola = ColaCircular()
    cola.encolar("A")
    assert cola.cabeza is cola.ultimo
    assert cola.ultimo.siguiente is cola.cabeza


def test_orden_fifo():
    cola = ColaCircular()
    for parada in ["A", "B", "C"]:
        cola.encolar(parada)
    assert cola.frente() == "A"
    assert cola.desencolar() == "A"
    assert cola.desencolar() == "B"
    assert cola.desencolar() == "C"


def test_circularidad_se_mantiene_al_encolar_y_desencolar():
    cola = ColaCircular()
    for parada in ["A", "B", "C"]:
        cola.encolar(parada)
        assert cola.ultimo.siguiente is cola.cabeza
    cola.desencolar()
    assert cola.ultimo.siguiente is cola.cabeza


def test_desencolar_hasta_vaciar_y_reutilizar():
    cola = ColaCircular()
    cola.encolar("A")
    cola.encolar("B")
    cola.desencolar()
    cola.desencolar()
    assert cola.esta_vacia()
    assert cola.cabeza is None and cola.ultimo is None
    cola.encolar("C")
    assert cola.frente() == "C"
    assert cola.tamano() == 1


def test_desencolar_vacia_devuelve_none():
    cola = ColaCircular()
    assert cola.desencolar() is None
    assert cola.tamano() == 0