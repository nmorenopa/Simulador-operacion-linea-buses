
from enum import Enum
from estructuras.arreglo_dinamico import Arreglo_dinamico
from estructuras.cola_circular import ColaCircular




class EstadoBus(Enum):
    DETENIDO = "Detenido"
    AVANZANDO = "Avanzando"


class Bus:
    def __init__(
        self,
        ruta: ColaCircular,
        sillas_rojas: int = 0,
        capacidad_maxima: int,
        adaptado_discapacitados: bool
    ):
        if self.sillas_rojas > capacidad_maxima:
            raise ValueError("Esta lleno")
        self.ruta: ColaCircular = ruta

        self.sillas_rojas: int = sillas_rojas
        self.capacidad_maxima: int = capacidad_maxima
        self.cantidad_pasajeros: int = 0

        self.estado: EstadoBus = EstadoBus.DETENIDO

        self.puertas_entrada_abiertas: bool = False
        self.puertas_salida_abiertas: bool = False

        self.pasajeros = Arreglo_dinamico()
        self.parada_actual = self.ruta.frente()
        self.totaltransportados: int = 0

        self.puertas_entrada_cerradas: bool = False
        self.puertas_salida_cerradas: bool = False

    def cantidad_pasajeros(self):
        self.pasajeros.longitud()
    def cupos_disponibles(self):
        self.cupos_disponibles = self.capacidad_maxima - self.pasajeros.longitud()


    def sube_al_bus(self,pasajero):
        if self.cupos_disponibles <= 0:
            raise ValueError("El bus esta lleno")
        self.pasajeros.agregaralfinal(pasajero)

    def bajar_parada(self,parada,minuto):
        se_fueron = 0
        for i in range(self.pasajeros.longitud() - 1, -1, -1):
            if self.pasajeros.posicion(i).destino == id_parada:
                self.pasajeros.borrarposicion(i)
                bajaron +=1
        self.totaltransportados += se_fueron
        return se_fueron
        
    def detenerbus(self):
        self.cambiar_estado(EstadoBus.DETENIDO)

    def avanzar(self):
        if self.puertas_salida_abiertas or self.puertas_entrada_abiertas:
            raise ValueError("Puertas abiertas")
        self.ruta.siguiente()
        self.parada_actual = self.self.ruta.frente()
        self.cambiar_estado(EstadoBus.AVANZANDO) 

    def abrir_puertas(self):
        if EstadoBus.AVANZANDO: 
            raise ValueError("Se esta moviendo")
        self.puertas_entrada_abiertas = True
        self.puertas_salida_abiertas = True

    def cerrar_puertas(self):
        self.puertas_entrada_cerradas = True
        self.puertas_salida_cerradas = True

    def cambiar_estado(self, nuevo_estado: EstadoBus):
        self.estado = nuevo_estado


