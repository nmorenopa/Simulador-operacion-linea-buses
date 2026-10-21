class Parada:
    def __init__(self, nombre, busesxestacion):
        self.nombre = nombre
        self.pasajeros = []


    def entrapasajero(self, destino):
        self.destino = destino
        self.pasajeros.append(self.destino)

    def salepasajero(self, salida):
        self.salida = salida
        self.pasajeros.pop(self.salida)


parada1 = Parada("Universidad Nacional")


