from estructuras.nodo import Nodo   # Nodo central, compartido por todas las estructuras
from typing import Any

class NodoColaPrioridad(Nodo):
    """Nodo de la cola con prioridad: un Nodo con un campo extra (la prioridad)."""

    def __init__(self, dato: Any, prioridad: int):
        super().__init__(dato)        # El padre inicializa dato y siguiente
        self.prioridad = prioridad    # Entero: mayor número = mayor prioridad


class ColaPrioridad:
    """
    Cola con prioridad implementada con una lista enlazada ordenada.

    Convención: MAYOR número = MAYOR prioridad (1 pasa antes que 0).
    La lista siempre está ordenada, así que el de mayor prioridad es la
    cabeza. Entre elementos con la misma prioridad se respeta el orden de
    llegada (FIFO).
    """

    def __init__(self)-> None:
        """Crea una cola vacía. O(1)."""
        self.cabeza = None    # Elemento de mayor prioridad (el próximo en salir)
        self._tamano = 0

    def esta_vacia(self)->bool:
        """Devuelve True si no hay elementos. O(1)."""
        return self._tamano == 0

    def tamano(self)-> int:
        """Devuelve la cantidad de elementos. O(1)."""
        return self._tamano

    def frente(self)-> Any:
        """Devuelve el próximo dato en salir sin sacarlo, o None si está vacía. O(1)."""
        if self.esta_vacia():
            return None
        return self.cabeza.dato

    def encolar(self, dato, prioridad)-> None:
        """
        Inserta el dato en su posición según su prioridad. O(n) en el peor caso.
        A igual prioridad, queda detrás de los que ya estaban.
        """
        nuevo = NodoColaPrioridad(dato, prioridad)

        # Caso 1: lista vacía, o el nuevo tiene ESTRICTAMENTE más prioridad que la cabeza
        if self.esta_vacia() or prioridad > self.cabeza.prioridad:
            nuevo.siguiente = self.cabeza
            self.cabeza = nuevo
        else:
            # Caso 2: va en medio o al final. Se avanza mientras el siguiente
            # tenga prioridad MAYOR O IGUAL (con ">=" el nuevo queda detrás de
            # sus iguales y se conserva el orden de llegada)
            actual = self.cabeza
            while actual.siguiente is not None and actual.siguiente.prioridad >= prioridad:
                actual = actual.siguiente
            nuevo.siguiente = actual.siguiente   # El nuevo apunta a lo que seguía
            actual.siguiente = nuevo             # Y el anterior apunta al nuevo

        self._tamano += 1
        # La prioridad se valida en pasajero.py (PRIORIDAD_ALTA=1, PRIORIDAD_NORMAL=0);
        # aquí la estructura acepta cualquier número comparable.

    def desencolar(self)-> Any:
        """Saca y devuelve el dato de mayor prioridad, o None si está vacía. O(1)."""
        if self.esta_vacia():
            return None

        dato = self.cabeza.dato              # Guardar antes de mover la cabeza
        self.cabeza = self.cabeza.siguiente  # Si era el único, queda en None
        self._tamano -= 1
        return dato