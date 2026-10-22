from estructuras.nodo import Nodo
from typing import Any


class Cola:
    """
    Cola FIFO (el primero que llega es el primero que sale), con lista enlazada.

    Se guardan los dos extremos (frente y final) y un contador interno, así
    agregar, borrar y consultar el tamaño son O(1).
    """

    def __init__(self):
        """Crea una cola vacía. O(1)."""
        self.frente = None    # Primer nodo (el próximo en salir)
        self.final = None     # Último nodo (donde se agrega)
        self._tamano = 0      # Contador interno: evita recorrer la lista para medir

    def esta_vacia(self) -> bool:
        """Devuelve True si no hay elementos. O(1)."""
        return self.frente is None

    def agregar(self, dato: Any)-> None:
        """Agrega un dato al final de la cola. O(1)."""
        aux = Nodo(dato)

        if self.esta_vacia():
            self.frente = aux
            self.final = aux
        else:
            self.final.siguiente = aux
            self.final = aux

        self._tamano += 1

    def borrar(self)-> Any:
        """Saca y devuelve el dato del frente, o None si está vacía. O(1)."""
        if self.esta_vacia():
            return None

        dato = self.frente.dato

        self.frente = self.frente.siguiente

        if self.frente is None:
            self.final = None

        self._tamano -= 1
        return dato

    def ver_frente(self)-> Any | None:
        """Devuelve el dato del frente sin sacarlo, o None si está vacía. O(1)."""
        if self.esta_vacia():
            return None

        return self.frente.dato

    def longitud(self)-> int:
        """Devuelve la cantidad de elementos usando el contador interno. O(1)."""
        return self._tamano

    def mostrar(self)-> None:
        """Imprime la cola de frente a final. O(n)."""
        aux = self.frente

        while aux is not None:
            print(aux.dato, end=" -> ")
            aux = aux.siguiente

        print("None")