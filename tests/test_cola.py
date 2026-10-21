from estructuras.cola import Cola


def test_cola_nueva_esta_vacia():
    c = Cola()
    assert c.esta_vacia()
    assert c.longitud() == 0
    assert c.ver_frente() is None
    assert c.borrar() is None


def test_orden_fifo_y_contador():
    c = Cola()
    for x in ["A", "B", "C"]:
        c.agregar(x)
    assert c.longitud() == 3
    assert c.ver_frente() == "A"
    assert [c.borrar(), c.borrar(), c.borrar()] == ["A", "B", "C"]
    assert c.longitud() == 0 and c.esta_vacia()


def test_vaciar_y_reutilizar():
    c = Cola()
    c.agregar("A")
    c.borrar()
    assert c.frente is None and c.final is None
    c.agregar("B")
    assert c.ver_frente() == "B" and c.longitud() == 1


def test_borrar_vacia_no_cambia_contador():
    c = Cola()
    c.borrar()
    assert c.longitud() == 0