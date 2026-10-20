from estructuras.cola_prioridad import ColaPrioridad


def test_cola_nueva_esta_vacia():
    cola = ColaPrioridad()
    assert cola.esta_vacia()
    assert cola.tamano() == 0
    assert cola.frente() is None
    assert cola.desencolar() is None


def test_sale_por_prioridad_aunque_llegue_despues():
    cola = ColaPrioridad()
    cola.encolar("normal", 1)
    cola.encolar("prioritario", 0)
    assert cola.desencolar() == "prioritario"
    assert cola.desencolar() == "normal"


def test_misma_prioridad_respeta_orden_de_llegada():
    cola = ColaPrioridad()
    for nombre in ["N1", "N2", "N3"]:
        cola.encolar(nombre, 1)
    assert [cola.desencolar() for _ in range(3)] == ["N1", "N2", "N3"]


def test_mezcla_prioridades():
    cola = ColaPrioridad()
    cola.encolar("P1", 0)
    cola.encolar("N1", 1)
    cola.encolar("N2", 1)
    cola.encolar("P2", 0)
    assert [cola.desencolar() for _ in range(4)] == ["P1", "P2", "N1", "N2"]


def test_varios_niveles():
    cola = ColaPrioridad()
    for nombre, prio in [("c", 2), ("a", 0), ("d", 3), ("b", 1)]:
        cola.encolar(nombre, prio)
    assert [cola.desencolar() for _ in range(4)] == ["a", "b", "c", "d"]


def test_vaciar_y_reutilizar():
    cola = ColaPrioridad()
    cola.encolar("A", 1)
    cola.desencolar()
    assert cola.esta_vacia()
    cola.encolar("B", 0)
    assert cola.frente() == "B"
    assert cola.tamano() == 1