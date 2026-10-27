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


def test_la_capacidad_crece_por_el_numero_aureo_al_llenarse():
    # Al llenarse, la nueva capacidad es int(capacidad * 1.618) + 1:
    # 1 -> 2 -> 4 -> 7 -> 12
    a = ArregloDinamico()
    capacidades = []
    for i in range(8):
        a.agregaralfinal(i)
        capacidades.append(a.capacidad)
    assert capacidades == [1, 2, 4, 4, 7, 7, 7, 12]
    assert a.mostrar() == [0, 1, 2, 3, 4, 5, 6, 7]


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


def test_insertar_manda_el_desplazado_al_final():
    # insertar es O(1): no corre elementos, el que estaba en k se va al final.
    a = armar(1, 3)
    a.insertar(1, 2)                 # el 3 se va al final
    assert a.mostrar() == [1, 2, 3]
    a.insertar(0, 0)                 # el 1 se va al final
    assert a.mostrar() == [0, 2, 3, 1]
    a.insertar(a.longitud(), 4)      # k == n: queda al final, nadie se mueve
    assert a.mostrar() == [0, 2, 3, 1, 4]


def test_borrar_posicion_trae_el_ultimo_y_borrar_al_final():
    # borrarposicion es O(1): el último elemento ocupa el hueco que queda en k.
    a = armar(1, 2, 3, 4)
    assert a.borrarposicion(1) == 2
    assert a.mostrar() == [1, 4, 3]
    assert a.borraralfinal() == 3
    assert a.mostrar() == [1, 4]


def test_borrar_posicion_del_ultimo_y_del_unico():
    a = armar(1, 2, 3)
    assert a.borrarposicion(2) == 3          # borrar el último no mueve a nadie
    assert a.mostrar() == [1, 2]
    b = armar("x")
    assert b.borrarposicion(0) == "x"
    assert b.vacio()


def test_borrar_al_final_en_vacio_lanza_error():
    with pytest.raises(IndexError):
        ArregloDinamico().borraralfinal()


def test_buscar_contiene_contar():
    a = armar(5, 7, 5)
    assert a.buscar(7) == 1 and a.buscar(9) == -1
    assert a.contiene(5) and not a.contiene(9)
    assert a.contar(5) == 2
