from estructuras.cola_circular import NodoCola
# TODO: mover NodoCola a un archivo común (ver con Santiago)


class NodoColaPrioridad(NodoCola):
    """Nodo de la cola con prioridad: un NodoCola con un campo extra."""

    def __init__(self, dato, prioridad):
        super().__init__(dato)        # El padre inicializa dato y siguiente
        self.prioridad = prioridad    # Entero: menor número = mayor prioridad


class ColaPrioridad:
    """
    Cola con prioridad implementada con una lista enlazada ordenada.

    Convención: MENOR número = MAYOR prioridad (0 pasa antes que 1).
    La lista siempre está ordenada, así que el de mayor prioridad es la
    cabeza. Entre elementos con la misma prioridad se respeta el orden de
    llegada (FIFO).
    """

    def __init__(self):
        """Crea una cola vacía. O(1)."""
        self.cabeza = None    # Elemento de mayor prioridad (el próximo en salir)
        self._tamano = 0

    def esta_vacia(self):
        """Devuelve True si no hay elementos. O(1)."""
        return self._tamano == 0

    def tamano(self):
        """Devuelve la cantidad de elementos. O(1)."""
        return self._tamano

    def frente(self):
        """Devuelve el próximo dato en salir sin sacarlo, o None si está vacía. O(1)."""
        if self.esta_vacia():
            return None
        return self.cabeza.dato

    def encolar(self, dato, prioridad):
        """
        Inserta el dato en su posición según su prioridad. O(n) en el peor caso.
        A igual prioridad, queda detrás de los que ya estaban.
        """
        nuevo = NodoColaPrioridad(dato, prioridad)

        # Caso 1: lista vacía, o el nuevo es ESTRICTAMENTE mejor que la cabeza
        if self.esta_vacia() or prioridad < self.cabeza.prioridad:
            nuevo.siguiente = self.cabeza
            self.cabeza = nuevo
        else:
            # Caso 2: va en medio o al final. Se avanza mientras el siguiente
            actual = self.cabeza
            while actual.siguiente is not None and actual.siguiente.prioridad <= prioridad:
                actual = actual.siguiente
            nuevo.siguiente = actual.siguiente   # El nuevo apunta a lo que seguía
            actual.siguiente = nuevo             # Y el anterior apunta al nuevo

        self._tamano += 1

    def desencolar(self):
        """Saca y devuelve el dato de mayor prioridad, o None si está vacía. O(1)."""
        if self.esta_vacia():
            return None

        dato = self.cabeza.dato              # Guardar antes de mover la cabeza
        self.cabeza = self.cabeza.siguiente  # Si era el único, queda en None
        self._tamano -= 1
        return dato