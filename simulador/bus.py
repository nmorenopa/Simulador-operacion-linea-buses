from estructuras.arreglo_dinamico import ArregloDinamico
from estructuras.cola_circular import ColaCircular
from simulador.pasajero import Pasajero


class Bus:
    """
    Bus que recorre una ruta circular, y sube y baja pasajeros.

    Cada bus tiene SU PROPIA ColaCircular, con las mismas paradas (las mismas
    referencias a objetos Parada) que los demás. El frente de esa cola es la
    parada donde está el bus, y avanzar es rotar la cola.

    Atributos:
        id: identificador del bus.
        ruta: ColaCircular de paradas propia de este bus.
        capacidad_maxima: cuántos pasajeros caben a bordo.
        pasajeros: ArregloDinamico con los pasajeros que van a bordo.
        parada_actual: la Parada donde está el bus.
        total_transportados: pasajeros que ya llegaron a su destino y bajaron.
    """

    def __init__(self, id: int, ruta: ColaCircular, capacidad_maxima: int)-> None:
        """
        Crea un bus vacío, ubicado en el frente de su ruta. O(1).

        Si se quiere separar los buses en la línea, hay que rotar la ruta
        (ruta.siguiente()) ANTES de crear el bus, porque la parada inicial
        se toma del frente en este momento.

        Lanza ValueError si la capacidad no es positiva o si la ruta está vacía.
        """
        if capacidad_maxima <= 0:
            raise ValueError("La capacidad debe ser mayor que 0")
        if ruta.esta_vacia():
            raise ValueError("La ruta no puede estar vacía")

        self.id = id
        self.ruta: ColaCircular = ruta
        self.capacidad_maxima: int = capacidad_maxima
        self.pasajeros = ArregloDinamico()
        self.parada_actual = self.ruta.frente()
        self.total_transportados: int = 0

    def cantidad_pasajeros(self)->int:
        """Devuelve cuántos pasajeros van a bordo. O(1)."""
        return self.pasajeros.longitud()

    def cupos_libres(self)-> int:
        """Devuelve cuántos pasajeros más caben. O(1)."""
        return self.capacidad_maxima - self.pasajeros.longitud()

    def ocupacion(self)-> float:
        """Devuelve la ocupación como fracción entre 0 y 1 (pasajeros / capacidad). O(1)."""
        return self.pasajeros.longitud() / self.capacidad_maxima

    def subir(self, pasajero: Pasajero)-> None:
        """
        Sube un pasajero al bus. Lanza ValueError si el bus está lleno
        (quien llama debe revisar cupos_libres() antes). O(1) amortizado.
        """
        if self.cupos_libres() <= 0:
            raise ValueError("El bus esta lleno")
        self.pasajeros.agregaralfinal(pasajero)

    def bajar_en(self, id_parada: int)-> int:
        """
        Baja a todos los pasajeros cuyo destino es la parada dada y suma
        cuántos bajaron a total_transportados. Devuelve cuántos bajaron.

        Se recorre de atrás hacia adelante para que borrar un elemento no
        corra los índices de los que faltan por revisar.
        O(n²) en el peor caso: cada borrado desplaza elementos.
        """
        bajaron = 0
        for i in range(self.pasajeros.longitud() - 1, -1, -1):
            if self.pasajeros.posicion(i).destino == id_parada:
                self.pasajeros.borrarposicion(i)
                bajaron += 1
        self.total_transportados += bajaron
        return bajaron

    def avanzar(self)-> None:
        """
        Mueve el bus a la siguiente parada de su ruta (rota la cola circular
        y actualiza parada_actual). O(1).
        """
        self.parada_actual = self.ruta.siguiente()