from typing import Any
from estructuras.arreglo_dinamico import ArregloDinamico


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

    def __init__(self, clave: Any, valor: Any) -> None:
        """Crea una hoja: sin hijos y con altura 1. O(1)."""
        self.clave = clave
        self.valor = valor
        self.izquierdo: NodoAVL | None = None
        self.derecho: NodoAVL | None = None
        self.altura = 1


class ArbolAVL:
    """
    Árbol binario de búsqueda autoequilibrado (AVL).
    Las claves deben ser comparables entre sí.

    En cada nodo, la altura de sus dos subárboles difiere a lo más en 1; por
    eso la altura total es O(log n) y buscar o insertar también lo son.
    """

    def __init__(self) -> None:
        """Crea un árbol vacío. O(1)."""
        self.raiz: NodoAVL | None = None
        self._tamano = 0      # Contador interno: evita recorrer el árbol para medir

    # --------------------------------------------------
    # MÉTODOS AUXILIARES
    # --------------------------------------------------

    def _altura(self, nodo: NodoAVL | None) -> int:
        """
        Obtiene la altura de un nodo (0 si el nodo no existe).
        Complejidad: O(1).
        """
        if nodo is None:
            return 0

        return nodo.altura

    def _actualizar_altura(self, nodo: NodoAVL) -> None:
        """
        Actualiza la altura de un nodo según sus hijos.
        Complejidad: O(1).
        """
        nodo.altura = 1 + max(
            self._altura(nodo.izquierdo),
            self._altura(nodo.derecho)
        )

    def _factor_balance(self, nodo: NodoAVL | None) -> int:
        """
        Calcula el factor de balance de un nodo: altura izquierda - altura derecha.
        Mayor que 1: cargado a la izquierda. Menor que -1: cargado a la derecha.
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

    def _rotacion_derecha(self, y: NodoAVL) -> NodoAVL:
        """
        Realiza una rotación simple hacia la derecha y devuelve la nueva raíz
        del subárbol.
                y              x
               / \\           / \\
              x   C   --->   A   y
             / \\               / \\
            A   B              B   C
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

    def _rotacion_izquierda(self, x: NodoAVL) -> NodoAVL:
        """
        Realiza una rotación simple hacia la izquierda (espejo de la derecha)
        y devuelve la nueva raíz del subárbol.
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

    def _insertar(self, nodo: NodoAVL | None, clave: Any, valor: Any) -> NodoAVL:
        """
        Inserta una clave recursivamente y equilibra el árbol.
        Devuelve la raíz (quizá nueva, tras rotar) del subárbol.
        Complejidad: O(log n), por tratarse de un AVL.
        """
        # Caso base: posición disponible. Solo aquí nace un nodo nuevo, así que
        # es el único lugar donde crece el tamaño.
        if nodo is None:
            self._tamano += 1
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
            # Si la clave existe, actualizar su valor (el árbol no cambia de forma)
            nodo.valor = valor
            return nodo

        # Actualizar altura
        self._actualizar_altura(nodo)

        # Calcular balance
        balance = self._factor_balance(nodo)

        # Para saber cuál de los 4 casos es, se mira hacia qué lado del hijo
        # bajó la clave recién insertada.

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

    def insertar(self, clave: Any, valor: Any) -> None:
        """
        Inserta una clave y su valor asociado.
        Si la clave ya existe, actualiza su valor (el tamaño no cambia).
        Complejidad: O(log n).
        """
        self.raiz = self._insertar(self.raiz, clave, valor)

    # --------------------------------------------------
    # BÚSQUEDA
    # --------------------------------------------------

    def _buscar_nodo(self, clave: Any) -> NodoAVL | None:
        """
        Baja desde la raíz eligiendo izquierda o derecha y devuelve el NODO con
        esa clave, o None si no está. Devolver el nodo (y no el valor) permite
        distinguir "no existe" de "existe y su valor es None".
        Complejidad: O(log n) en un AVL.
        """
        nodo = self.raiz
        while nodo is not None:
            if clave == nodo.clave:
                return nodo
            if clave < nodo.clave:
                nodo = nodo.izquierdo
            else:
                nodo = nodo.derecho
        return None

    def buscar(self, clave: Any) -> Any:
        """
        Busca una clave y devuelve su valor asociado.
        Devuelve None si no existe (si el valor guardado puede ser None,
        usar contiene() para saber si la clave está).
        Complejidad: O(log n).
        """
        nodo = self._buscar_nodo(clave)
        return None if nodo is None else nodo.valor

    def contiene(self, clave: Any) -> bool:
        """
        True si la clave está en el árbol.
        Complejidad: O(log n).
        """
        return self._buscar_nodo(clave) is not None

    # --------------------------------------------------
    # CONSULTAS POR ORDEN
    # --------------------------------------------------

    def _rango(self, nodo: NodoAVL | None, desde: Any, hasta: Any, resultado: ArregloDinamico) -> None:
        """
        Recorrido en orden que se salta las ramas que no pueden tener claves
        dentro de [desde, hasta]: si la clave del nodo ya es menor o igual a
        'desde', a su izquierda todo es más pequeño y no hace falta bajar.
        Complejidad: O(log n + k), donde k es la cantidad de claves halladas.
        """
        if nodo is None:
            return

        if desde < nodo.clave:
            self._rango(nodo.izquierdo, desde, hasta, resultado)

        if desde <= nodo.clave <= hasta:
            resultado.agregaralfinal((nodo.clave, nodo.valor))

        if nodo.clave < hasta:
            self._rango(nodo.derecho, desde, hasta, resultado)

    def rango(self, desde: Any, hasta: Any) -> ArregloDinamico:
        """
        Devuelve un ArregloDinamico con las parejas (clave, valor) con
        desde <= clave <= hasta (incluye los dos extremos), ordenadas por clave.
        Si desde > hasta, devuelve un ArregloDinamico vacío.
        Ejemplo: estaciones entre el metro 2000 y el 5000.
        Complejidad: O(log n + k), donde k es la cantidad de claves halladas
        (cada agregaralfinal es O(1) amortizado).
        """
        resultado = ArregloDinamico()
        self._rango(self.raiz, desde, hasta, resultado)
        return resultado

    def piso(self, clave: Any) -> tuple | None:
        """
        "Piso" de una clave: la pareja (clave, valor) con la MAYOR clave que sea
        menor o igual a la pedida, o None si todas son mayores.
        Ejemplo: la última estación en o antes del metro 3500.
        Idea: si el nodo sirve (clave <= pedida), se guarda como candidato y se
        busca uno mejor (más grande) a la derecha; si no sirve, se va a la izquierda.
        Complejidad: O(log n).
        """
        mejor = None
        nodo = self.raiz
        while nodo is not None:
            if nodo.clave <= clave:
                mejor = nodo
                nodo = nodo.derecho
            else:
                nodo = nodo.izquierdo
        return None if mejor is None else (mejor.clave, mejor.valor)

    def techo(self, clave: Any) -> tuple | None:
        """
        "Techo" de una clave: la pareja (clave, valor) con la MENOR clave que sea
        mayor o igual a la pedida, o None si todas son menores.
        Es el espejo de piso(): si el nodo sirve (clave >= pedida), se guarda
        como candidato y se busca uno mejor (más pequeño) a la izquierda; si no
        sirve, se va a la derecha.
        Ejemplo: el primer pasajero que esperó 15 minutos o más.
        Complejidad: O(log n).
        """
        mejor = None
        nodo = self.raiz
        while nodo is not None:
            if nodo.clave >= clave:
                mejor = nodo
                nodo = nodo.izquierdo
            else:
                nodo = nodo.derecho
        return None if mejor is None else (mejor.clave, mejor.valor)

    def minimo(self) -> tuple | None:
        """
        La pareja (clave, valor) con la MENOR clave, o None si el árbol está vacío.
        Idea: en un ABB lo más pequeño siempre está a la izquierda, así que se
        baja por la izquierda hasta que no haya más.
        Complejidad: O(log n), porque la altura de un AVL es O(log n).
        """
        if self.raiz is None:
            return None
        nodo = self.raiz
        while nodo.izquierdo is not None:
            nodo = nodo.izquierdo
        return (nodo.clave, nodo.valor)

    def maximo(self) -> tuple | None:
        """
        La pareja (clave, valor) con la MAYOR clave, o None si el árbol está vacío.
        Idea: espejo de minimo(): se baja por la derecha hasta que no haya más.
        Ejemplo: el pasajero con la peor espera.
        Complejidad: O(log n), porque la altura de un AVL es O(log n).
        """
        if self.raiz is None:
            return None
        nodo = self.raiz
        while nodo.derecho is not None:
            nodo = nodo.derecho
        return (nodo.clave, nodo.valor)

    # --------------------------------------------------
    # RECORRIDO EN ORDEN
    # --------------------------------------------------

    def _en_orden(self, nodo: NodoAVL | None, resultado: ArregloDinamico) -> None:
        """
        Recorre el árbol en orden ascendente (izquierda, nodo, derecha)
        y va agregando cada pareja al final de 'resultado'.
        Complejidad: O(n).
        """
        if nodo is None:
            return

        self._en_orden(nodo.izquierdo, resultado)
        resultado.agregaralfinal((nodo.clave, nodo.valor))
        self._en_orden(nodo.derecho, resultado)

    def en_orden(self) -> ArregloDinamico:
        """
        Devuelve un ArregloDinamico con todas las parejas (clave, valor)
        ordenadas por clave. Si el árbol está vacío, devuelve un ArregloDinamico vacío.
        Complejidad: O(n) (cada agregaralfinal es O(1) amortizado).
        """
        resultado = ArregloDinamico()
        self._en_orden(self.raiz, resultado)

        return resultado

    # --------------------------------------------------
    # VERIFICACIÓN DEL BALANCE
    # --------------------------------------------------

    def _verificar_balance(self, nodo: NodoAVL | None) -> tuple:
        """
        Comprueba que todos los nodos estén balanceados
        y que sus alturas sean correctas.
        Devuelve (está_balanceado, altura_real).
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

    def verificar_balance(self) -> bool:
        """
        Comprueba si todo el árbol cumple las condiciones AVL.
        Complejidad: O(n).
        """
        return self._verificar_balance(self.raiz)[0]

    # --------------------------------------------------
    # INFORMACIÓN GENERAL
    # --------------------------------------------------

    def altura(self) -> int:
        """
        Devuelve la altura total del árbol.
        Complejidad: O(1).
        """
        return self._altura(self.raiz)

    def tamano(self) -> int:
        """
        Devuelve la cantidad de elementos almacenados.
        Complejidad: O(1).
        """
        return self._tamano

    def esta_vacio(self) -> bool:
        """
        Comprueba si el árbol está vacío.
        Complejidad: O(1).
        """
        return self.raiz is None
