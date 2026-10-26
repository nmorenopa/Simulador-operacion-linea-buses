from typing import Any

class ArregloDinamico:
    """
    Arreglo dinámico: guarda sus elementos en un arreglo de tamaño fijo y,
    cuando se llena, lo reemplaza por otro de mayor capacidad (razón áurea).
    Si queda muy vacío, lo reemplaza por uno más pequeño.

    Atributos:
        capacidad: cuántos elementos caben sin crecer.
        datos: el arreglo interno de tamaño fijo (con None en los huecos libres).
        n: cuántos elementos tiene realmente (los índices válidos van de 0 a n-1).
        frecuencias: diccionario valor -> cuántas veces aparece.
"""

    capacidadinicial = 1
    aureo = 1.618

    def __init__(self)->None:
        """Crea un arreglo vacío con la capacidad inicial. O(1)."""
        self.capacidad: int = self.capacidadinicial
        self.datos = [None] * self.capacidad
        self.n: int = 0

        self.posiciones = {}
        self.frecuencias = {}
        self.moda_inicial = {}
        self.frecuencia_maxima = 0


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
        """Devuelve True si el valor está en el arreglo. O(1)."""
        return valor in self.frecuencias

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
        """Devuelve cuántas veces aparece el valor. O(1)."""
        return self.frecuencias.get(valor, 0)

    def _restar(self, valor: Any)-> None:
        """Uso interno: descuenta una aparición del valor. O(1)."""
        self.frecuencias[valor] -= 1
        if self.frecuencias[valor] == 0:
            del self.frecuencias[valor]

    def agrandar(self, nuevacapacidad: int)-> None:
        """
        Uso interno: crea un arreglo nuevo con la capacidad dada y copia
        los n elementos uno por uno. Sirve para crecer y para encoger. O(n).
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
        self._restar(self.datos[k])
        self.datos[k] = valor
        self.frecuencias[valor] = self.frecuencias.get(valor, 0) + 1

    def agregaralfinal(self, valor: Any)-> None:
        """
        Agrega el valor después del último elemento. Si el arreglo está lleno,
        multiplica su capacidad por la razón áurea (siempre crece al menos 1).
        O(1) amortizado (O(n) en el momento de crecer).
        """
        if self.n == self.capacidad:
            nueva = int(self.capacidad * self.aureo)
            if nueva <= self.capacidad:
                nueva = self.capacidad + 1
            self.agrandar(nueva)
        self.datos[self.n] = valor
        self.n += 1
        self.frecuencias[valor] = self.frecuencias.get(valor, 0) + 1

    def insertar(self, k: int, valor: Any)-> None:
        """
        Inserta el valor en la posición k, corriendo una posición a la derecha
        los elementos desde k. Se permite k == n (insertar al final).
        Lanza IndexError si k no está entre 0 y n. O(n).
        """
        if k < 0 or k > self.n:
            raise IndexError("Índice fuera de rango")
        if self.n == self.capacidad:
            nueva = int(self.capacidad * self.aureo)
            if nueva <= self.capacidad:
                nueva = self.capacidad + 1
            self.agrandar(nueva)
        for i in range(self.n, k, -1):
            self.datos[i] = self.datos[i - 1]
        self.datos[k] = valor
        self.n += 1
        self.frecuencias[valor] = self.frecuencias.get(valor, 0) + 1

    def borraralfinal(self)-> Any:
        """
        Quita y devuelve el último elemento. Si la ocupación baja de
        capacidad / aureo², reduce la capacidad a n * aureo.
        Lanza IndexError si el arreglo está vacío. O(1) amortizado.
        """
        if self.vacio():
            raise IndexError("El arreglo esta vacio")
        if self.n * self.aureo * self.aureo < self.capacidad:
            self.agrandar(int(self.n * self.aureo))
        borrar = self.datos[self.n - 1]
        self.datos[self.n - 1] = None
        self.n -= 1
        self._restar(borrar)
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
        self._restar(borrarpos)
        return borrarpos

    def moda(self)-> Any | None:
        """
        Devuelve el valor que más se repite. Si hay empate, devuelve el que
        aparece primero. Lanza ValueError si el arreglo está vacío. O(n).
        """
        if self.vacio():
            raise ValueError("El arreglo esta vacio")
        mayor = 0
        moda = None
        for i in range(self.n):
            f = self.frecuencias[self.datos[i]]
            if f > mayor:
                mayor = f
                moda = self.datos[i]
        return moda