from estructuras.cola import Cola
from estructuras.cola_prioridad import ColaPrioridad

class Parada:

    def __init__ (self, id, nombre, tasa_llegada):
        self. id = id 
        self.nombre = nombre
        self.tasa_llegada = tasa_llegada
        self.fila = Cola()

        self.total_entran = 0
        self.total_subidos = 0

    def entra_pasajero(self,pasajero):
        self.fila.agregar(pasajero)
        self.totalentran +=1

    def espera_pasajero(self, bus, minuto):
        return self.fila.longitud()

    def subidos_al_bus(self, bus, minuto):
        cola_prioridad = ColaPrioridad()
        for i in range (self.fila.longitud()):
            prioridad2 = self.fila.borrar()
            cola_prioridad.encolar(prioridad2, prioridad2.prioridad)
        subieron = 0
        while bus.cupos.libres() > 0 and cola_prioridad.tamano() > 0:
            p = cola_prioridad.desencolar()
            p.minuto_abordaje = minuto
            bus.subir(p)
            subieron +=1
        for i in range(cola_prioridad.tamano()):
            self.fila.agregar(cola_prioridad.desencolar())
        self.total_subidos += subieron
        return subieron
    
        