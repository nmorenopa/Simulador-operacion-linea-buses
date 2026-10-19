
class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.sig = None

class Pila:
    def __init__(self):
        self.tope = None

    def esta_vacia(self):
        return self.tope == None

    def apilar(self, dato):
        if self.esta_vacia():
            self.tope = Nodo(dato)
        else:
            aux = Nodo(dato)
            aux.sig = self.tope
            self.tope = aux

    def desapilar(self):
        if self.esta_vacia():
            return None

        dato = self.tope.dato
        aux = self.tope
        self.tope = self.tope.sig
        del aux

        return dato

    def ver_tope(self):
        if self.esta_vacia():
            return None

        return self.tope.dato

    def longitud(self):
        contador = 0
        aux = self.tope

        while aux != None:
            contador += 1
            aux = aux.sig

        return contador

    def mostrar(self):
        aux = self.tope

        while aux != None:
            print(aux.dato, end=" -> ")
            aux = aux.sig

        print("None")