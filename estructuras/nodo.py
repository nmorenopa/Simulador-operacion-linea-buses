class Nodo:
    """
    Nodo de una lista enlazada simple. Es el único nodo del proyecto:
    lo usan Cola, Pila, ColaCircular y ColaPrioridad.
    """

    def __init__(self, dato):
        """Crea un nodo suelto, sin enlazar. O(1)."""
        self.dato = dato
        self.siguiente = None