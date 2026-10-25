from estructuras.cola_prioridad import ColaPrioridad
from simulador.pasajero import Pasajero, NIVELES_PRIORIDAD
from simulador.bus import Bus


class Parada:
    """
    Parada de la línea: guarda la fila de pasajeros que esperan y organiza
    quién sube cuando llega un bus.

    La fila es una ColaPrioridad: cada pasajero queda organizado por prioridad
    en el momento en que LLEGA a la parada. Así, al abordar, los prioritarios
    suben primero y, entre iguales, se respeta el orden de llegada (FIFO).

    La Parada no importa Bus: solo usa bus.cupos_libres() y bus.subir().
    La Parada tampoco crea pasajeros; eso lo hace el Simulador.

    Atributos:
        id: identificador de la parada (su posición en la ruta).
        nombre: nombre para mostrar.
        tasa_llegada: probabilidad (entre 0 y 1) de que llegue un pasajero cada minuto.
        fila: ColaPrioridad con los pasajeros que esperan, ordenados por prioridad.
        total_llegados: pasajeros que han llegado a esta parada.
        total_abordados: pasajeros que han subido a un bus aquí.
        suma_espera: suma de los minutos de espera de quienes ya abordaron
        (sirve para calcular la espera promedio).
        prioritarios_esperando: cuántos de los que esperan en la fila son prioritarios
        (la interfaz lo usa para dibujar la fila sin recorrerla).
    """

    def __init__(self, id: int, nombre: str, tasa_llegada: float):
        """
        Crea una parada sin pasajeros. O(1).
        Lanza ValueError si la tasa de llegada no está entre 0 y 1.
        """
        if not 0 <= tasa_llegada <= 1:
            raise ValueError("La tasa de llegada debe estar entre 0 y 1")

        self.id = id
        self.nombre = nombre
        self.tasa_llegada = tasa_llegada
        self.fila = ColaPrioridad(NIVELES_PRIORIDAD)

        self.total_llegados = 0
        self.total_abordados = 0
        self.suma_espera = 0
        self.prioritarios_esperando = 0

    def recibir(self, pasajero: Pasajero):
        """Pone al pasajero en la fila según su prioridad (al final de su nivel) y suma a los contadores de llegados y prioritarios. O(1)."""
        self.fila.encolar(pasajero, pasajero.prioridad)

        if pasajero.es_prioritario():
            self.prioritarios_esperando += 1

        self.total_llegados += 1

    def esperando(self):
        """Devuelve cuántos pasajeros hay en la fila. O(1)."""
        return self.fila.tamano()

    def abordar(self, bus: Bus, minuto: int):
        """
        Sube pasajeros al bus mientras tenga cupo: primero los prioritarios y,
        entre iguales, los que llegaron antes. Los que no caben siguen en la fila.

        Como la fila ya está ordenada por prioridad desde que cada pasajero llegó,
        basta con desencolar mientras haya cupo (se anota su minuto de abordaje
        y su espera).

        Devuelve cuántos pasajeros subieron. O(m), con m = pasajeros que suben:
        cada desencolar es O(k) y k (niveles de prioridad) es fijo.
        """
        subieron = 0
        while bus.cupos_libres() > 0 and not self.fila.esta_vacia():
            pasajero = self.fila.desencolar()
            pasajero.minuto_abordaje = minuto
            bus.subir(pasajero)
            self.suma_espera += pasajero.tiempo_espera()
            if pasajero.es_prioritario():
                self.prioritarios_esperando -= 1
            subieron += 1

        self.total_abordados += subieron
        return subieron