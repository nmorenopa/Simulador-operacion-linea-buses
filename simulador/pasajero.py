# MENOR número = MAYOR prioridad, así el prioritario sale primero de la cola.
PRIORIDAD_ALTA = 0      # Adultos mayores, movilidad reducida, etc.
PRIORIDAD_NORMAL = 1
NIVELES_PRIORIDAD = 2

class Pasajero:
    """
    Persona que espera en una parada y viaja en un bus.

    Es casi solo datos: no sabe de colas ni de buses. Quien lo sube a un bus
    (la Parada) es quien le asigna el minuto de abordaje.
    """

    def __init__(self, id: int, origen: int, destino: int, prioridad: int, minuto_llegada: int)-> None:
        """
        Crea un pasajero que todavía no ha abordado. O(1).

        Parámetros:
            id: identificador del pasajero.
            origen: id de la parada donde espera.
            destino: id de la parada donde se baja (distinto del origen).
            prioridad: PRIORIDAD_ALTA o PRIORIDAD_NORMAL.
            minuto_llegada: minuto de la simulación en que llegó a la fila.

        Lanza ValueError si el origen es igual al destino o si la prioridad
        no es una de las dos constantes.
        """
        if origen == destino:
            raise ValueError("El origen y el destino deben ser distintos")
        if prioridad not in (PRIORIDAD_ALTA, PRIORIDAD_NORMAL):
            raise ValueError("Prioridad inválida: use PRIORIDAD_ALTA o PRIORIDAD_NORMAL")

        self.id = id
        self.origen = origen
        self.destino = destino
        self.prioridad = prioridad
        self.minuto_llegada = minuto_llegada
        self.minuto_abordaje = None    # None hasta que sube a un bus

    def es_prioritario(self)-> bool:
        """Devuelve True si tiene prioridad alta. O(1)."""
        return self.prioridad == PRIORIDAD_ALTA

    def tiempo_espera(self)-> int | None:
        """
        Minutos que esperó en la fila (minuto_abordaje - minuto_llegada).
        Devuelve None si todavía no ha abordado. O(1).
        """
        if self.minuto_abordaje is None:
            return None

        return self.minuto_abordaje - self.minuto_llegada

    def __repr__(self)-> str:
        """Texto corto para depurar y para mostrar en pantalla. O(1)."""
        tipo = "prioritario" if self.es_prioritario() else "normal"
        return f"Pasajero(id={self.id}, {self.origen}->{self.destino}, {tipo}, llegó={self.minuto_llegada})"