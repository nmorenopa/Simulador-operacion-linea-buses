from estructuras.cola import Cola
from estructuras.cola_prioridad import ColaPrioridad
from simulador.pasajero import Pasajero
from simulador.bus import Bus


class Parada:
    """
    Parada de la línea: guarda la fila de pasajeros que esperan y organiza
    quién sube cuando llega un bus.

    La fila es una Cola (FIFO). Al abordar, los pasajeros pasan por una
    ColaPrioridad para que los prioritarios suban primero y, entre iguales,
    se respete el orden de llegada.

    La Parada no importa Bus: solo usa bus.cupos_libres() y bus.subir().
    La Parada tampoco crea pasajeros; eso lo hace el Simulador.

    Atributos:
        id: identificador de la parada (su posición en la ruta).
        nombre: nombre para mostrar.
        tasa_llegada: probabilidad (entre 0 y 1) de que llegue un pasajero cada minuto.
        fila: Cola con los pasajeros que esperan.
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
        self.fila = Cola()

        self.total_llegados = 0
        self.total_abordados = 0
        self.suma_espera = 0
        self.prioritarios_esperando = 0

    def recibir(self, pasajero: Pasajero):
        """Pone al pasajero al final de la fila y suma a los contadores de llegados y prioritarios. O(1)."""
        self.fila.agregar(pasajero)

        if pasajero.es_prioritario():
            self.prioritarios_esperando += 1

        self.total_llegados += 1

    def esperando(self):
        """Devuelve cuántos pasajeros hay en la fila. O(1)."""
        return self.fila.longitud()

    def abordar(self, bus: Bus, minuto: int):
        """
        Sube pasajeros al bus mientras tenga cupo: primero los prioritarios y,
        entre iguales, los que llegaron antes. Los que no caben vuelven a la fila.

        Pasos: se vacía la fila en una ColaPrioridad, se suben los que caben
        (se anota su minuto de abordaje y su espera) y se devuelve el resto a la fila.

        Devuelve cuántos pasajeros subieron. O(n²) en el peor caso, porque
        encolar en la ColaPrioridad es O(n) y se hace n veces.
        """
        en_orden = ColaPrioridad()
        while not self.fila.esta_vacia():
            pasajero = self.fila.borrar()
            en_orden.encolar(pasajero, pasajero.prioridad)

        subieron = 0
        while bus.cupos_libres() > 0 and not en_orden.esta_vacia():
            pasajero = en_orden.desencolar()
            pasajero.minuto_abordaje = minuto
            bus.subir(pasajero)
            self.suma_espera += pasajero.tiempo_espera()
            if pasajero.es_prioritario():
                self.prioritarios_esperando -= 1
            subieron += 1

        # Los que no cupieron vuelven a la fila (ya salen ordenados por prioridad)
        while not en_orden.esta_vacia():
            self.fila.agregar(en_orden.desencolar())

        self.total_abordados += subieron
        return subieron