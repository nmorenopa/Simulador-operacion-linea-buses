from estructuras.pila import Pila


def test_pila_nueva_esta_vacia():
    p = Pila()
    assert p.esta_vacia()
    assert p.longitud() == 0
    assert p.ver_tope() is None
    assert p.desapilar() is None


def test_orden_lifo_y_contador():
    p = Pila()
    for x in ["A", "B", "C"]:
        p.apilar(x)
    assert p.longitud() == 3
    assert p.ver_tope() == "C"
    assert [p.desapilar(), p.desapilar(), p.desapilar()] == ["C", "B", "A"]
    assert p.longitud() == 0 and p.esta_vacia()


def test_desapilar_vacia_no_cambia_contador():
    p = Pila()
    p.desapilar()
    assert p.longitud() == 0


def test_vaciar_y_reutilizar():
    p = Pila()
    p.apilar("A")
    p.desapilar()
    p.apilar("B")
    assert p.ver_tope() == "B" and p.longitud() == 1