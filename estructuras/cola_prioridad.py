from estructuras.cola import Cola
from estructuras.arreglo_dinamico import ArregloDinamico
from typing import Any


class ColaPrioridad:
    """
    Cola con prioridad implementada como un arreglo de colas.
    
    En donde a menor indice dentor del arreglo estos tienen mas prioridad.
    CONVENCION: MENOR número = MAYOR prioridad
    """
    def __init__(self, cantidad_niveles: int)-> None:
        """
        Crea un arreglo con k (cantidad_niveles) pocisiones y a cada uno le asigna una cola vacia. O(k)
        """
        
        if cantidad_niveles < 1:
            raise ValueError("La cantidad minima de niveles requerida es de 1")
        
        self.cantidad_niveles = cantidad_niveles
        self.niveles = ArregloDinamico()
        
        for _ in range(cantidad_niveles):
            self.niveles.agregaralfinal(Cola())
        
        self._tamano = 0
    
    def tamano(self)-> int:
        """Devuelve la cantidad de elementos O(1)"""
        return self._tamano
    
    def esta_vacia(self)-> bool:
        """Devuelve un booleano que indica si la cola esta vacia O(1)"""
        return self.tamano() == 0
    
    def frente(self)-> Any | None:
        """Devuelve el dato del primer elemento de la cola no vacia dentro de los k niveles O(k)"""
        if self.esta_vacia():
            return None
        
        primer_nivel_con_datos = self._primer_nivel_con_datos()
        return primer_nivel_con_datos.ver_frente()
    
    def encolar(self, dato: Any, prioridad: int) -> None:
        """Agrega el dato a la cola segun su prioridad(nivel) O(1)"""
        if not(0 <= prioridad <= self.cantidad_niveles - 1):
            raise ValueError(f"La prioridad debe estar entre 0 y {self.cantidad_niveles - 1}")
        
        self.niveles.posicion(prioridad).agregar(dato)
        self._tamano += 1
    
    def desencolar(self) -> Any | None:
        """Saca y devuelve el dato de mayor prioridad, o None si está vacía. Dependiendo la cantidad k de niveles del arreglo O(k)."""
        if self.esta_vacia():
            return None
        
        primer_nivel_con_datos = self._primer_nivel_con_datos()
        self._tamano -= 1
        return primer_nivel_con_datos.borrar()
    
    # Métodos privados (uso interno)
    def _primer_nivel_con_datos(self)-> Cola | None:
        """Devuelve la primera cola no vacia en un nivel no vacio"""
        for k in range(self.cantidad_niveles):
            if self.niveles.posicion(k).esta_vacia():
                continue
            
            return self.niveles.posicion(k)
        
        return None