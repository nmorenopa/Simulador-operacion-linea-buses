from estructuras.nodo import Nodo   # Nodo central, compartido por todas las estructuras
from typing import Any


class ColaCircular:
    """
    Cola FIFO implementada con una lista enlazada circular.

    Invariante: si la cola no está vacía, ultimo.siguiente es cabeza.
    Por eso basta guardar los dos extremos y las operaciones son O(1).
    """

    def __init__(self)-> None:
        """Crea una cola vacía. O(1)."""
        self.cabeza = None    # Primer nodo
        self.ultimo = None    # Último nodo; su siguiente apunta a cabeza
        self._tamano = 0      # Contador interno, evita recorrer para medir

    def esta_vacia(self)-> bool:
        """Devuelve True si no hay elementos. O(1)."""
        return self._tamano == 0

    def tamano(self)-> int:
        """Devuelve la cantidad de elementos. O(1)."""
        return self._tamano

    def frente(self)-> Any:
        """Devuelve el primer dato sin sacarlo, o None si está vacía. O(1)."""
        if self.esta_vacia():
            return None
        return self.cabeza.dato

    def siguiente(self)-> Any | None:
        """
        Rota la cola: la cabeza pasa a ser el último y la cabeza avanza al nodo
        siguiente. Devuelve el dato de la nueva cabeza, o None si la cola está
        vacía. No crea ni borra nodos, solo mueve dos punteros. O(1).
        """
        if self.esta_vacia():
            return None
        
        self.ultimo = self.cabeza
        self.cabeza = self.cabeza.siguiente
        
        return self.cabeza.dato

    def encolar(self, dato: Any)->None:
        """Agrega un dato al final de la cola. O(1)."""
        nuevo_nodo = Nodo(dato)

        if self.esta_vacia():
            # Único nodo: es cabeza y último a la vez
            self.cabeza = nuevo_nodo
            self.ultimo = nuevo_nodo
        else:
            # El último actual apunta al nuevo, y el nuevo pasa a ser el último
            self.ultimo.siguiente = nuevo_nodo
            self.ultimo = nuevo_nodo

        # En ambos casos el nuevo último cierra el círculo hacia la cabeza
        nuevo_nodo.siguiente = self.cabeza
        self._tamano += 1

    def desencolar(self)-> Any | None:
        """
        Saca y devuelve el primer dato (FIFO).
        Si la cola está vacía devuelve None. O(1).
        """
        if self.esta_vacia():
            return None

        dato_retorno = self.cabeza.dato   # Guardar ANTES de mover punteros

        if self._tamano == 1:
            # Se saca el único nodo: la cola queda vacía
            self.cabeza = None
            self.ultimo = None
        else:
            # Avanza la cabeza y reconecta el último para mantener el círculo
            self.cabeza = self.cabeza.siguiente
            self.ultimo.siguiente = self.cabeza

        self._tamano -= 1
        return dato_retorno