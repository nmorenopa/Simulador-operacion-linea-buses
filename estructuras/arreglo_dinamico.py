from typing import Any

class ArregloDinamico:
    """
    Arreglo dinámico: guarda sus elementos en un arreglo de tamaño fijo y,
    cuando se llena, lo reemplaza por otro del doble de capacidad.

    Atributos:
        capacidad: cuántos elementos caben sin crecer.
        datos: el arreglo interno de tamaño fijo (con None en los huecos libres).
        n: cuántos elementos tiene realmente (los índices válidos van de 0 a n-1).

    Agregar al final es O(1) amortizado: casi siempre es una sola asignación y
    solo cuando se llena hay que copiar todo (O(n)), algo que ocurre cada vez
    menos seguido porque la capacidad se duplica.
    """

    capacidadinicial = 1

    def __init__(self)->None:
        """Crea un arreglo vacío con la capacidad inicial. O(1)."""
        self.capacidad: int = self.capacidadinicial
        self.datos = [None] * self.capacidad
        self.n: int = 0

    def longitud(self)->int:
        """Devuelve cuántos elementos hay. O(1)."""
        return self.n

    def vacio(self)-> bool:
        """Devuelve True si no hay elementos. O(1)."""
        return self.n == 0

    def posicion(self, k: int)-> Any:
        """
        Devuelve el elemento en la posición k.
        Lanza IndexError si k no está entre 0 y n-1. O(1).
        """
        if k < 0 or k >= self.n:
            raise IndexError("Índice fuera de rango")
        return self.datos[k]

    def contiene(self, valor: Any)-> bool:
        """Devuelve True si el valor está en el arreglo. O(n)."""
        for i in range(self.n):
            if self.datos[i] == valor:
                return True
        return False

    def buscar(self, valor: Any)-> int:
        """Devuelve la posición de la primera aparición del valor, o -1 si no está. O(n)."""
        for i in range(self.n):
            if self.datos[i] == valor:
                return i
        return -1

    def mostrar(self)-> list:
        """
        Devuelve una lista de Python con los elementos, solo para mostrarlos
        en la interfaz o en las pruebas (no se usa dentro de las estructuras). O(n).
        """
        mostrar = []
        for i in range(self.n):
            mostrar.append(self.datos[i])
        return mostrar

    def contar(self, valor: Any)-> int:
        """Devuelve cuántas veces aparece el valor. O(n)."""
        k = 0
        for i in range(self.n):
            if self.datos[i] == valor:
                k += 1
        return k

    def agrandar(self, nuevacapacidad: int)-> None:
        """
        Uso interno: crea un arreglo nuevo con la capacidad dada y copia
        los n elementos uno por uno. O(n).
        """
        arreglonuevo = [None] * nuevacapacidad
        for i in range(self.n):
            arreglonuevo[i] = self.datos[i]
        self.datos = arreglonuevo
        self.capacidad = nuevacapacidad

    def cambiarposicion(self, k: int, valor: Any)-> None:
        """
        Reemplaza el elemento de la posición k por el valor dado.
        Lanza IndexError si k no está entre 0 y n-1. O(1).
        """
        if k < 0 or k >= self.n:
            raise IndexError("Índice fuera de rango")
        self.datos[k] = valor

    def agregaralfinal(self, valor: Any)-> None:
        """
        Agrega el valor después del último elemento. Si el arreglo está lleno,
        primero duplica su capacidad. O(1) amortizado (O(n) en el momento de crecer).
        """
        if self.n == self.capacidad:
            self.agrandar(self.capacidad * 2)
        self.datos[self.n] = valor
        self.n += 1

    def insertar(self, k: int, valor: Any)-> None:
        """
        Inserta el valor en la posición k, corriendo una posición a la derecha
        los elementos desde k. Se permite k == n (insertar al final).
        Lanza IndexError si k no está entre 0 y n. O(n).
        """
        if k < 0 or k > self.n:
            raise IndexError("Índice fuera de rango")
        if self.n == self.capacidad:
            self.agrandar(self.capacidad * 2)
        for i in range(self.n, k, -1):
            self.datos[i] = self.datos[i - 1]
        self.datos[k] = valor
        self.n += 1

    def borraralfinal(self)-> Any:
        """
        Quita y devuelve el último elemento.
        Lanza IndexError si el arreglo está vacío. O(1).
        """
        if self.vacio():
            raise IndexError("El arreglo esta vacio")
        borrar = self.datos[self.n - 1]
        self.datos[self.n - 1] = None
        self.n -= 1
        return borrar

    def borrarposicion(self, k: int)-> Any:
        """
        Quita y devuelve el elemento de la posición k, corriendo una posición a
        la izquierda los que estaban después.
        Lanza IndexError si k no está entre 0 y n-1. O(n).
        """
        if k < 0 or k >= self.n:
            raise IndexError("Fuera de rango")
        borrarpos = self.datos[k]
        for i in range(k, self.n - 1):
            self.datos[i] = self.datos[i + 1]
        self.datos[self.n - 1] = None
        self.n -= 1
        return borrarpos

    def moda(self)-> Any | None:
        """
        Devuelve el valor que más se repite. Si hay empate, devuelve el que
        aparece primero. Lanza ValueError si el arreglo está vacío. O(n²).
        """
        mayor = 0
        if self.vacio():
            raise ValueError("El arreglo esta vacio")
        else:
            moda = None
            for a in range(self.n):
                contador = 0
                for b in range(self.n):
                    if self.datos[a] == self.datos[b]:
                        contador += 1
                if contador > mayor:
                    mayor = contador
                    moda = self.datos[a]
        return moda