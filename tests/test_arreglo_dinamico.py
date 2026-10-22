import pytest
from estructuras.arreglo_dinamico import ArregloDinamico


def armar(*valores):
    a = ArregloDinamico()
    for v in valores:
        a.agregaralfinal(v)
    return a


def test_arreglo_nuevo_esta_vacio():
    a = ArregloDinamico()
    assert a.vacio() and a.longitud() == 0


def test_la_capacidad_se_duplica_al_llenarse():
    a = ArregloDinamico()
    capacidades = []
    for i in range(5):
        a.agregaralfinal(i)
        capacidades.append(a.capacidad)
    assert capacidades == [1, 2, 4, 4, 8]
    assert a.mostrar() == [0, 1, 2, 3, 4]


def test_posicion_y_cambiarposicion():
    a = armar("a", "b", "c")
    assert a.posicion(1) == "b"
    a.cambiarposicion(1, "X")
    assert a.mostrar() == ["a", "X", "c"]


def test_indices_invalidos_lanzan_error():
    a = armar(1, 2)
    for f in (lambda: a.posicion(2), lambda: a.posicion(-1),
              lambda: a.cambiarposicion(2, 0), lambda: a.borrarposicion(2),
              lambda: a.insertar(3, 0)):
        with pytest.raises(IndexError):
            f()


def test_insertar_en_medio_inicio_y_final():
    a = armar(1, 3)
    a.insertar(1, 2)
    a.insertar(0, 0)
    a.insertar(a.longitud(), 4)
    assert a.mostrar() == [0, 1, 2, 3, 4]


def test_borrar_posicion_y_al_final():
    a = armar(1, 2, 3, 4)
    assert a.borrarposicion(1) == 2
    assert a.borraralfinal() == 4
    assert a.mostrar() == [1, 3]


def test_borrar_al_final_en_vacio_lanza_error():
    with pytest.raises(IndexError):
        ArregloDinamico().borraralfinal()


def test_buscar_contiene_contar():
    a = armar(5, 7, 5)
    assert a.buscar(7) == 1 and a.buscar(9) == -1
    assert a.contiene(5) and not a.contiene(9)
    assert a.contar(5) == 2


def test_moda():
    assert armar(1, 2, 2, 3).moda() == 2
    with pytest.raises(ValueError):
        ArregloDinamico().moda()