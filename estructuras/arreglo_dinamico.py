class Arreglo_dinamico: 
    def __init__(self):
        self.nuevo = []
    def longitud (self):
        return len(self.nuevo)
    def vacio(self):
        return len(self.nuevo) == 0
    def posicion (self, k):
        return self.nuevo[k]
    def contiene(self,valor):
        return valor in self.nuevo
    def buscar(self,valor):
        for i in range(len(self.nuevo)):
            if self.nuevo[i] == valor:
                print("El valor esta en la posicion: ", i)
    def mostrar (self):
        return self.nuevo
    def contar(self,valor):
        k = 0
        for i in range(len(self.nuevo)):
            if self.nuevo[i] == valor:
                k += 1
        return k
    def cambiarposicion(self,k,valor):
        if 
        self..nuevo[k] = valor
