
from enum import Enum

from estructuras.cola_circular import ColaCircular


class TipoBus(Enum):
    ALIMENTADOR = "Alimentador"
    SITP = "SITP"
    TRANSMILENIO = "TransMilenio"


class EstadoBus(Enum):
    DETENIDO = "Detenido"
    AVANZANDO = "Avanzando"


class Bus:
    def __init__(
        self,
        tipo_bus: TipoBus,
        ruta: ColaCircular,
        sillas_rojas: int,
        sillas_azules: int,
        capacidad_maxima: int,
        adaptado_discapacitados: bool
    ):
        self.tipo_bus: TipoBus = tipo_bus
        self.ruta: ColaCircular = ruta

        self.sillas_rojas: int = sillas_rojas
        self.sillas_azules: int = sillas_azules
        self.capacidad_maxima: int = capacidad_maxima
        self.cantidad_pasajeros: int = 0

        self.estado: EstadoBus = EstadoBus.DETENIDO
        self.adaptado_discapacitados: bool = adaptado_discapacitados

        self.puertas_entrada_abiertas: bool = False
        self.puertas_salida_abiertas: bool = False

    def detenerse(self):
        pass

    def avanzar(self):
        pass

    def abrir_puertas(self):
        pass

    def cerrar_puertas(self):
        pass

    def desplegar_rampa_accesibilidad(self):
        pass

    def cambiar_estado(self, nuevo_estado: EstadoBus):
        pass
