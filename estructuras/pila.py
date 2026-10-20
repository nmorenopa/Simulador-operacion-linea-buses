from estructuras.nodo import Nodo


class Pila:
    """
    Pila LIFO (el último en entrar es el primero en salir), con lista enlazada.

    Solo se guarda el tope y un contador interno, así apilar, desapilar y
    consultar el tamaño son O(1).
    """

    def __init__(self):
        """Crea una pila vacía. O(1)."""
        self.tope = None      # Último nodo apilado (el próximo en salir)
        self._tamano = 0      # Contador interno: evita recorrer la lista para medir

    def esta_vacia(self):
        """Devuelve True si no hay elementos. O(1)."""
        return self.tope == None
        # NOTA (revisión): en Python se compara con None usando "is None", no "== None".

    def apilar(self, dato):
        """Pone un dato encima de la pila. O(1)."""
        if self.esta_vacia():
            self.tope = Nodo(dato)
        else:
            aux = Nodo(dato)
            aux.siguiente = self.tope
            self.tope = aux
        # NOTA (revisión): los dos casos se pueden unir: crear el nodo, hacer
        # nodo.siguiente = self.tope (vale None si está vacía) y mover el tope.

        self._tamano += 1

    def desapilar(self):
        """Quita y devuelve el dato del tope, o None si está vacía. O(1)."""
        if self.esta_vacia():
            return None

        dato = self.tope.dato
        aux = self.tope
        self.tope = self.tope.siguiente
        del aux
        # NOTA (revisión): "del aux" no hace falta; Python libera la memoria solo.

        self._tamano -= 1
        return dato

    def ver_tope(self):
        """Devuelve el dato del tope sin sacarlo, o None si está vacía. O(1)."""
        if self.esta_vacia():
            return None

        return self.tope.dato

    def longitud(self):
        """Devuelve la cantidad de elementos usando el contador interno. O(1)."""
        return self._tamano
        # NOTA (revisión): se acordó el nombre tamano(), y apilar/desapilar/tope
        # para esta estructura. Al renombrar, avisar a quien use Pila.

    def mostrar(self):
        """Imprime la pila del tope hacia el fondo. O(n)."""
        aux = self.tope

        while aux != None:
            print(aux.dato, end=" -> ")
            aux = aux.siguiente

        print("None")
        # NOTA (revisión): imprimir mezcla lógica con interfaz. Para Streamlit
        # sería más útil un método que devuelva una lista de datos.