class Arreglo_dinamico: 
    capacidadinicial = 1

    def __init__(self,):
        self.capacidad = self.capacidadinicial
        self.datos = [None] * self.capacidad
        self.n = 0

    def longitud (self):
        return self.n
    
    def vacio(self):
        return self.n == 0
    
    # NOTA (revisión): no valida k. Un índice negativo (-1) devuelve el último
    # elemento en vez de dar error, y uno muy grande lanza un IndexError de Python.
    def posicion (self, k):
        if k < 0 or k >self.n:
            raise IndexError("Índice fuera de rango")
        else:
        return self.datos[k]
    
    def contiene(self,valor):
        for i in range(self.n)):
            if self.n[i] == valor:
                return True
        return False
    
    # NOTA (revisión): imprime en vez de devolver. Si el valor no está, no dice nada.
    # Mejor devolver la posición del primer valor encontrado, o -1 si no existe.
    def buscar(self,valor):
        for i in range(self.n):
            if self.datos[i] == valor:
                print("El valor esta en la posicion: ", i)

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
        self.capacidad - nuevacapacidad

    # BUG (revisión): la condición está invertida. Con un índice VÁLIDO (0 <= k < len)
    # lanza IndexError, y con uno inválido intenta asignar. Debería ser:
    #     if not (0 <= k < len(self.arreglo)): raise IndexError(...)
    def cambiarposicion(self,k,valor):
        if k < 0 or k >self.n:
            raise IndexError("Índice fuera de rango")
        else:
            self.datos[k] = valor

    def agregaralfinal(self,valor):
        if self.n == self.capacidad:
            self.agrandar(self.capacidad * 2)
        self.datos[self.n] = valor
        self.n += 1

    # BUG (revisión): misma condición invertida. Además, insertar debe permitir
    # k == len (insertar al final), así que lo válido es 0 <= k <= len.
    def insertar(self,k,valor):
        if k < 0 or k >self.n:
            raise IndexError("Índice fuera de rango")
        if self.n == self.capacidad:
            self.agrandar(self.capacidad * 2)
        self.datos[k]= valor
        self.n +=1
            

    # NOTA (revisión): no devuelve el elemento borrado. Para usarlo como flota o
    # historial conviene devolverlo.
    def borraralfinal(self):
        if self.vacio():
            raise IndexError("El arreglo esta vacio")
        borrar = self.datos[self.n - 1]
        self.datos[self.n - 1] = None
        self.n -=1
        return borrar

    # BUG (revisión): misma condición invertida que en cambiarposicion.
    def borrarposicion(self,k):
        if self.vacio():
            raise IndexError("El arreglo esta vacio")
        borrarpos = self.datos[k]
        for i in range(k, self.n - 1):
            self.datos[i] = self.datos[i+1]
        self.datos[self.n - 1] = None
        self.n -=1
        return borrarpos

    # BUG (revisión): "max = 0" tapa la función max() de Python, y luego max(moda.values())
    # falla con TypeError: 'int' object is not callable. Borrar "max = 0" y la variable
    # "contador" (no se usa). Además, puede devolver varios valores si hay empate;
    # documentarlo en el docstring.
    def moda(self):
        contador = 0
        max = 0
        if self.vacio():
            raise ValueError("El arreglo esta vacio")
        else:
            moda = {}
<<<<<<< HEAD
            for a in range(self.n):
                for b in range(self.n):
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
>>>>>>> ea1912af539c3e2b91bd898424a54decc21a4290
