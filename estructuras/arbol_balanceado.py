
class NodoAVL:
    """
    Representa un nodo de un árbol AVL.

    Atributos:
        clave: valor utilizado para ordenar el árbol.
        valor: información asociada a la clave.
        izquierdo: hijo izquierdo.
        derecho: hijo derecho.
        altura: altura del nodo.
    """

    def __init__(self, clave, valor):
        self.clave = clave
        self.valor = valor
        self.izquierdo = None
        self.derecho = None
        self.altura = 1  


class ArbolAVL:
    """
    Árbol binario de búsqueda autoequilibrado (AVL).
    Las claves deben ser comparables entre sí.
    """

    def __init__(self):
        self.raiz = None
        self.tamano = 0

    # --------------------------------------------------
    # MÉTODOS AUXILIARES
    # --------------------------------------------------

    def _altura(self, nodo):
        """
        Obtiene la altura de un nodo.
        Complejidad: O(1).
        """
        if nodo is None:
            return 0

        return nodo.altura

    def _actualizar_altura(self, nodo):
        """
        Actualiza la altura de un nodo según sus hijos.
        Complejidad: O(1).
        """
        nodo.altura = 1 + max(
            self._altura(nodo.izquierdo),
            self._altura(nodo.derecho)
        )

    def _factor_balance(self, nodo):
        """
        Calcula el factor de balance de un nodo.
        Complejidad: O(1).
        """
        if nodo is None:
            return 0

        return (
            self._altura(nodo.izquierdo)
            - self._altura(nodo.derecho)
        )

    # --------------------------------------------------
    # ROTACIONES
    # --------------------------------------------------

    def _rotacion_derecha(self, y):
        """
        Realiza una rotación simple hacia la derecha.
        Complejidad: O(1).
        """
        x = y.izquierdo
        subarbol = x.derecho

        # Realizar la rotación
        x.derecho = y
        y.izquierdo = subarbol

        # Actualizar primero el nodo que baja
        self._actualizar_altura(y)

        # Después, el nodo que sube
        self._actualizar_altura(x)

        return x

    def _rotacion_izquierda(self, x):
        """
        Realiza una rotación simple hacia la izquierda.
        Complejidad: O(1).
        """
        y = x.derecho
        subarbol = y.izquierdo

        # Realizar la rotación
        y.izquierdo = x
        x.derecho = subarbol

        # Actualizar primero el nodo que baja
        self._actualizar_altura(x)

        # Después, el nodo que sube
        self._actualizar_altura(y)

        return y

    # --------------------------------------------------
    # INSERCIÓN Y BALANCEO
    # --------------------------------------------------

    def _insertar(self, nodo, clave, valor):
        """
        Inserta una clave recursivamente y equilibra el árbol.
        Complejidad: O(log n), por tratarse de un AVL.
        """
        # Caso base: posición disponible
        if nodo is None:
            return NodoAVL(clave, valor)

        # Buscar la posición correspondiente
        if clave < nodo.clave:
            nodo.izquierdo = self._insertar(
                nodo.izquierdo, clave, valor
            )

        elif clave > nodo.clave:
            nodo.derecho = self._insertar(
                nodo.derecho, clave, valor
            )

        else:
            # Si la clave existe, actualizar su valor
            nodo.valor = valor
            return nodo

        # Actualizar altura
        self._actualizar_altura(nodo)

        # Calcular balance
        balance = self._factor_balance(nodo)

        # CASO 1: Izquierda - Izquierda (II)
        if balance > 1 and clave < nodo.izquierdo.clave:
            return self._rotacion_derecha(nodo)

        # CASO 2: Derecha - Derecha (DD)
        if balance < -1 and clave > nodo.derecho.clave:
            return self._rotacion_izquierda(nodo)

        # CASO 3: Izquierda - Derecha (ID)
        if balance > 1 and clave > nodo.izquierdo.clave:
            nodo.izquierdo = self._rotacion_izquierda(
                nodo.izquierdo
            )
            return self._rotacion_derecha(nodo)

        # CASO 4: Derecha - Izquierda (DI)
        if balance < -1 and clave < nodo.derecho.clave:
            nodo.derecho = self._rotacion_derecha(
                nodo.derecho
            )
            return self._rotacion_izquierda(nodo)

        return nodo

    def insertar(self, clave, valor):
        """
        Inserta una clave y su valor asociado.
        Si la clave ya existe, actualiza su valor.
        Complejidad: O(log n).
        """
        existente = self.buscar(clave)

        if existente is None:
            self.tamano += 1

        self.raiz = self._insertar(self.raiz, clave, valor)

    # --------------------------------------------------
    # BÚSQUEDA
    # --------------------------------------------------

    def _buscar(self, nodo, clave):
        """
        Busca una clave desde un nodo determinado.
        Complejidad: O(log n) en un AVL.
        """
        if nodo is None:
            return None

        if clave == nodo.clave:
            return nodo.valor

        if clave < nodo.clave:
            return self._buscar(nodo.izquierdo, clave)

        return self._buscar(nodo.derecho, clave)

    def buscar(self, clave):
        """
        Busca una clave y devuelve su valor asociado.
        Devuelve None si no existe.
        Complejidad: O(log n).
        """
        return self._buscar(self.raiz, clave)


    # --------------------------------------------------
    # RECORRIDO EN ORDEN
    # --------------------------------------------------

    def _en_orden(self, nodo, resultado):
        """
        Recorre el árbol en orden ascendente.
        Complejidad: O(n).
        """
        if nodo is None:
            return

        self._en_orden(nodo.izquierdo, resultado)
        resultado.append((nodo.clave, nodo.valor))
        self._en_orden(nodo.derecho, resultado)

    def en_orden(self):
        """
        Devuelve todos los elementos ordenados por clave.
        Complejidad: O(n).
        """
        resultado = []
        self._en_orden(self.raiz, resultado)

        return resultado if resultado else None

    # --------------------------------------------------
    # VERIFICACIÓN DEL BALANCE
    # --------------------------------------------------

    def _verificar_balance(self, nodo):
        """
        Comprueba que todos los nodos estén balanceados
        y que sus alturas sean correctas.
        Complejidad: O(n).
        """
        if nodo is None:
            return True, 0

        balance_izq, altura_izq = self._verificar_balance(
            nodo.izquierdo
        )

        balance_der, altura_der = self._verificar_balance(
            nodo.derecho
        )

        altura_real = 1 + max(altura_izq, altura_der)

        esta_balanceado = (
            balance_izq
            and balance_der
            and abs(altura_izq - altura_der) <= 1
            and nodo.altura == altura_real
        )

        return esta_balanceado, altura_real

    def verificar_balance(self):
        """
        Comprueba si todo el árbol cumple las condiciones AVL.
        Complejidad: O(n).
        """
        return self._verificar_balance(self.raiz)[0]

    # --------------------------------------------------
    # INFORMACIÓN GENERAL
    # --------------------------------------------------

    def altura(self):
        """
        Devuelve la altura total del árbol.
        Complejidad: O(1).
        """
        return self._altura(self.raiz)

    def __len__(self):
        """
        Devuelve la cantidad de elementos almacenados.
        Complejidad: O(1).
        """
        return self.tamano

    def esta_vacio(self):
        """
        Comprueba si el árbol está vacío.
        Complejidad: O(1).
        """
        return self.raiz is None
