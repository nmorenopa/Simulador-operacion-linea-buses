from typing import Any

class Nodo:
    """
    Nodo de una lista enlazada simple. Es el único nodo del proyecto:
    lo usan Cola, Pila, ColaCircular y ColaPrioridad (a través de las Colas de sus niveles).
    """

    def __init__(self, dato: Any)-> None:
        """Crea un nodo suelto, sin enlazar. O(1)."""
        self.dato = dato
        self.siguiente = None