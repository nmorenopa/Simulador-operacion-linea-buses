class Arreglo_dinamico: 

    def __init__(self):
        self.arreglo = []

    def longitud (self):
        return len(self.arreglo)
    
    def vacio(self):
        return len(self.arreglo) == 0
    
    # NOTA (revisión): no valida k. Un índice negativo (-1) devuelve el último
    # elemento en vez de dar error, y uno muy grande lanza un IndexError de Python.
    def posicion (self, k):
        return self.arreglo[k]
    
    def contiene(self,valor):
        for i in range(len(self.arreglo)):
            if self.arreglo[i] == valor:
                return True
        return False
    
    # NOTA (revisión): imprime en vez de devolver. Si el valor no está, no dice nada.
    # Mejor devolver la posición del primer valor encontrado, o -1 si no existe.
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


    # BUG (revisión): la condición está invertida. Con un índice VÁLIDO (0 <= k < len)
    # lanza IndexError, y con uno inválido intenta asignar. Debería ser:
    #     if not (0 <= k < len(self.arreglo)): raise IndexError(...)
    def cambiarposicion(self,k,valor):
        if 0 <= k < len(self.arreglo):
            raise IndexError("Índice fuera de rango")
        else:
            self.arreglo[k] = valor

    def agregaralfinal(self,valor):
        self.arreglo.append(valor)

    # BUG (revisión): misma condición invertida. Además, insertar debe permitir
    # k == len (insertar al final), así que lo válido es 0 <= k <= len.
    def insertar(self,k,valor):
        if (0 <= k < len(self.arreglo)):
            raise IndexError("Índice fuera de rango")
        else:
            self.arreglo.insert(k,valor)

    # NOTA (revisión): no devuelve el elemento borrado. Para usarlo como flota o
    # historial conviene devolverlo.
    def borraralfinal(self):
        if self.vacio():
            raise IndexError("El arreglo esta vacio")
        else:
            self.arreglo.pop()

    # BUG (revisión): misma condición invertida que en cambiarposicion.
    def borrarposicion(self,k):
        if 0 <= k < len(self.arreglo):
            raise IndexError("Índice fuera de rango")
        else:
            self.arreglo.pop(k)

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
            for i in range(len(self.arreglo)):
                if self.arreglo[i] in moda:
                    moda[self.arreglo[i]] += 1
                else:
                    moda[self.arreglo[i]] = 1
            maximo = max(moda.values())
            return [k for k, v in moda.items() if v == maximo]