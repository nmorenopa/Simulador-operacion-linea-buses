from estructuras.nodo import Nodo
from estructuras.cola import Cola
from estructuras.pila import Pila
from estructuras.cola_circular import ColaCircular
from estructuras.cola_prioridad import ColaPrioridad


def test_nodo_nuevo_no_apunta_a_nada():
    n = Nodo("A")
    assert n.dato == "A"
    assert n.siguiente is None


def test_las_cuatro_estructuras_usan_el_mismo_nodo():
    cola, pila, circ, prio = Cola(), Pila(), ColaCircular(), ColaPrioridad(2)
    cola.agregar(1)
    pila.apilar(1)
    circ.encolar(1)
    prio.encolar(1, 0)
    assert type(cola.frente) is Nodo
    assert type(pila.tope) is Nodo
    assert type(circ.cabeza) is Nodo
    assert type(prio.niveles.posicion(0).frente) is Nodo
