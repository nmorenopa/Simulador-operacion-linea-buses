class Arreglo_dinamico: 

    def __init__(self):
        self.arreglo = []

    def longitud (self):
        return len(self.arreglo)
    
    def vacio(self):
        return len(self.arreglo) == 0
    
    def posicion (self, k):
        return self.arreglo[k]
    
    def contiene(self,valor):
        for i in range(len(self.arreglo)):
            if self.arreglo[i] == valor:
                return True
        return False
    
    def buscar(self,valor):
        for i in range(len(self.arreglo)):
            if self.arreglo[i] == valor:
                print("El valor esta en la posicion: ", i)

    def mostrar (self):
        return self.arreglo
    
    def contar(self,valor):
        k = 0
        for i in range(len(self.arreglo)):
            if self.arreglo[i] == valor:
                k += 1
        return k


    def cambiarposicion(self,k,valor):
        if 0 <= k < len(self.arreglo):
            raise IndexError("Índice fuera de rango")
        else:
            self.arreglo[k] = valor

    def agregaralfinal(self,valor):
        self.arreglo.append(valor)

    def insertar(self,k,valor):
        if (0 <= k < len(self.arreglo)):
            raise IndexError("Índice fuera de rango")
        else:
            self.arreglo.insert(k,valor)

    def borraralfinal(self):
        if self.vacio():
            raise IndexError("El arreglo esta vacio")
        else:
            self.arreglo.pop()

    def borrarposicion(self,k):
        if 0 <= k < len(self.arreglo):
            raise IndexError("Índice fuera de rango")
        else:
            self.arreglo.pop(k)

    def moda(self):
        contador = 0
        max = 0
        if self.vacio():
            raise ValueError("El arreglo esta vacio")
        else:
            moda = {}
<<<<<<< HEAD
            for a in range(len(self.arreglo)):
                for b in range(len(self.arreglo)):
                    if self.arreglo[a] == self.arreglo[b]:
                        contador += 1
                if contador > max:
                    max = contador
                    moda = self.arreglo[a]
        return moda
=======
            for i in range(len(self.arreglo)):
                if self.arreglo[i] in moda:
                    moda[self.arreglo[i]] += 1
                else:
                    moda[self.arreglo[i]] = 1
            maximo = max(moda.values())
            return [k for k, v in moda.items() if v == maximo]


>>>>>>> 93c6c16c2e4c4fa297be246d1e50a59e971b4687
