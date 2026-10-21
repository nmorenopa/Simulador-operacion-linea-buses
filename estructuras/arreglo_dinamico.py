class Arreglo_dinamico: 
    capacidadinicial = 1

    def __init__(self,):
        self.capacidad: int = self.capacidadinicial
        self.datos = [None] * self.capacidad
        self.n: int = 0

    def longitud (self):
        return self.n
    
    def vacio(self):
        return self.n == 0
    
    def posicion (self, k):
        if k < 0 or k >=self.n:
            raise IndexError("Índice fuera de rango")
        return self.datos[k]
    
    def contiene(self,valor):
        for i in range(self.n):
            if self.datos[i] == valor:
                return True
        return False
    
    def buscar(self,valor):
        for i in range(self.n):
            if self.datos[i] == valor:
                print("El valor esta en la posicion: ", i)
                return i
        return -1

    def mostrar (self):
        mostrar =[]
        for i in range(self.n):
            mostrar.append(self.datos[i])
        return mostrar
    
    def contar(self,valor):
        k = 0
        for i in range(self.n):
            if self.datos[i] == valor:
                k += 1
        return k

    def agrandar(self, nuevacapacidad):
        arreglonuevo = [None] * nuevacapacidad
        for i in range(self.n):
            arreglonuevo[i] = self.datos[i]
        self.datos = arreglonuevo
        self.capacidad = nuevacapacidad

    def cambiarposicion(self,k,valor):
        if k < 0 or k >=self.n:
            raise IndexError("Índice fuera de rango")
        self.datos[k] = valor

    def agregaralfinal(self,valor):
        if self.n == self.capacidad:
            self.agrandar(self.capacidad * 2)
        self.datos[self.n] = valor
        self.n += 1

    def insertar(self,k,valor):
        if k < 0 or k >self.n:
            raise IndexError("Índice fuera de rango")
        if self.n == self.capacidad:
            self.agrandar(self.capacidad * 2)
        for i in range(self.n, k, -1):
            self.datos[i]= self.datos[i-1]
        self.datos[k]= valor
        self.n +=1
            

    def borraralfinal(self):
        if self.vacio():
            raise IndexError("El arreglo esta vacio")
        borrar = self.datos[self.n - 1]
        self.datos[self.n - 1] = None
        self.n -=1
        return borrar

    def borrarposicion(self,k):
        if k<0 or k>=self.n:
            raise IndexError("Fuera de rango")
        borrarpos = self.datos[k]
        for i in range(k, self.n - 1):
            self.datos[i] = self.datos[i+1]
        self.datos[self.n - 1] = None
        self.n -=1
        return borrarpos

    def moda(self):
        mayor = 0
        if self.vacio():
            raise ValueError("El arreglo esta vacio")
        else:
            moda = None
            for a in range(self.n):
                contador = 0
                for b in range(self.n):
                    if self.datos[a] == self.datos[b]:
                        contador += 1
                if contador > mayor:
                    mayor = contador
                    moda = self.datos[a]
        return moda
