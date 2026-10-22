from estructuras.nodo import Nodo
from typing import Any

class Pila:
    """
    Pila LIFO (el último en entrar es el primero en salir), con lista enlazada.

    Solo se guarda el tope y un contador interno, así apilar, desapilar y
    consultar el tamaño son O(1).
    """

    def __init__(self)-> None:
        """Crea una pila vacía. O(1)."""
        self.tope = None      # Último nodo apilado (el próximo en salir)
        self._tamano = 0      # Contador interno: evita recorrer la lista para medir

    def esta_vacia(self)-> bool:
        """Devuelve True si no hay elementos. O(1)."""
        return self.tope is None

    def apilar(self, dato: Any)-> None:
        """Pone un dato encima de la pila. O(1)."""
        aux = Nodo(dato)
        aux.siguiente = self.tope   # Si la pila estaba vacía, vale None
        self.tope = aux

        self._tamano += 1

    def desapilar(self)->Any | None:
        """Quita y devuelve el dato del tope, o None si está vacía. O(1)."""
        if self.esta_vacia():
            return None

        dato = self.tope.dato
        self.tope = self.tope.siguiente

        self._tamano -= 1
        return dato

    def ver_tope(self)-> Any | None:
        """Devuelve el dato del tope sin sacarlo, o None si está vacía. O(1)."""
        if self.esta_vacia():
            return None

        return self.tope.dato

    def longitud(self)-> int:
        """Devuelve la cantidad de elementos usando el contador interno. O(1)."""
        return self._tamano

    def mostrar(self)->None:
        """Imprime la pila del tope hacia el fondo. O(n)."""
        aux = self.tope

        while aux is not None:
            print(aux.dato, end=" -> ")
            aux = aux.siguiente

        print("None")