
class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.sig = None


class Cola:
    def __init__(self):
        self.frente = None
        self.final = None

    def esta_vacia(self):
        return self.frente == None

    def agregar(self, dato):
        aux = Nodo(dato)

        if self.esta_vacia():
            self.frente = aux
            self.final = aux
        else:
            self.final.sig = aux
            self.final = aux

    def borrar(self):
        if self.esta_vacia():
            return None

        dato = self.frente.dato
        aux = self.frente

        self.frente = self.frente.sig

        if self.frente is None:
            self.final = None

        del aux
        return dato

    def ver_frente(self):
        if self.esta_vacia():
            return None

        return self.frente.dato

    def longitud(self):
        contador = 0
        aux = self.frente

        while aux is not None:
            contador += 1
            aux = aux.sig

        return contador

    def mostrar(self):
        aux = self.frente

        while aux is not None:
            print(aux.dato, end=" -> ")
            aux = aux.sig

        print("None")