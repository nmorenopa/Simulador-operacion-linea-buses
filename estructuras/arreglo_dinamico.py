import random
from typing import Any

class ArregloDinamico:
    capacidadinicial = 1
    aureo = 1.618  # Factor crecimiento del arreglo dinamico

    def __init__(self)->None:
        """Crea un arreglo vacío con la capacidad inicial. O(1)."""
        self.capacidad: int = self.capacidadinicial
        self.datos = [None] * self.capacidad
        self.n: int = 0

    def longitud(self)->int:
        """O(1) - Solo retorna una variable."""
        return self.n

    def vacio(self)-> bool:
        """O(1) - Solo compara una variable."""
        return self.n == 0

    def posicion(self, k: int)-> Any:
        """O(1) - Acceso directo a la memoria a través del índice."""
        if k < 0 or k >= self.n:
            raise IndexError("Índice fuera de rango")
        return self.datos[k]

    def contiene(self, valor: Any)-> bool:
        """O(n) - Hay que recorrer todo el arreglo elemento por elemento para saber si existe."""
        for i in range(self.n):
            if self.datos[i] == valor:
                return True
        return False

    def buscar(self, valor: Any)-> int:
        """O(n) - Búsqueda lineal, se revisa uno por uno hasta encontrar la coincidencia."""
        for i in range(self.n):
            if self.datos[i] == valor:
                return i
        return -1

    def mostrar(self)-> list:
        """O(n) - Recorre todos los elementos actuales para copiarlos en la lista a mostrar."""
        mostrar = []
        for i in range(self.n):
            mostrar.append(self.datos[i])
        return mostrar

    def contar(self, valor: Any)-> int:
        """O(n) - Obligatoriamente visita cada elemento para contar las repeticiones."""
        k = 0
        for i in range(self.n):
            if self.datos[i] == valor:
                k += 1
        return k

    def agrandar(self, nuevacapacidad: int)-> None:
        """O(n) al momento de crecer, ya que debe copiar los elementos al nuevo espacio de memoria."""
        arreglonuevo = [None] * nuevacapacidad
        for i in range(self.n):
            arreglonuevo[i] = self.datos[i]
        self.datos = arreglonuevo
        self.capacidad = nuevacapacidad

    def cambiarposicion(self, k: int, valor: Any)-> None:
        """O(1) - Modifica un valor accediendo directamente a su índice."""
        if k < 0 or k >= self.n:
            raise IndexError("Índice fuera de rango")
        self.datos[k] = valor

    def agregaralfinal(self, valor: Any)-> None:
        """O(1) amortizado - Generalmente es O(1), salvo cuando se llena y debe usar agrandar()."""
        if self.n == self.capacidad:
            # Multiplicamos por 1.618 (número áureo) para controlar el crecimiento
            self.agrandar(int(self.capacidad * self.aureo) + 1)
        self.datos[self.n] = valor
        self.n += 1

    def insertar(self, k: int, valor: Any)-> None:
        """
        O(1) CONSTANTE: En vez de correr los elementos hacia la derecha (lo cual sería O(n)),
        mandamos el elemento actual de la posición 'k' al final del arreglo
        y ponemos el nuevo en 'k'.
        """
        if k < 0 or k > self.n:
            raise IndexError("Índice fuera de rango")
        if self.n == self.capacidad:
            self.agrandar(int(self.capacidad * self.aureo) + 1)
            
        if k == self.n:
            self.datos[self.n] = valor
        else:
            # El que estaba en k se va al final
            self.datos[self.n] = self.datos[k]
            # El nuevo toma su lugar
            self.datos[k] = valor
            
        self.n += 1

    def borraralfinal(self)-> Any:
        """O(1) CONSTANTE: Simplemente bajamos el contador 'N' y limpiamos el dato."""
        if self.vacio():
            raise IndexError("El arreglo esta vacio")
        borrar = self.datos[self.n - 1]
        self.datos[self.n - 1] = None
        self.n -= 1
        return borrar

    def borrarposicion(self, k: int)-> Any:
        """
        O(1) CONSTANTE: En vez de correr los elementos a la izquierda (O(n)),
        traemos el último elemento del arreglo a la posición 'k' y achicamos N.
        """
        if k < 0 or k >= self.n:
            raise IndexError("Fuera de rango")
        
        borrarpos = self.datos[k]
        
        # Copiamos el último elemento a la posición que queremos borrar
        self.datos[k] = self.datos[self.n - 1]
        
        # Limpiamos el último y achicamos
        self.datos[self.n - 1] = None
        self.n -= 1
        return borrarpos

