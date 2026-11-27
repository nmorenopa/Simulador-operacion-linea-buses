from estructuras.arreglo_dinamico import ArregloDinamico


class ArbolSegmentos:
    """
    Árbol de segmentos genérico: consulta un rango y actualiza una posición
    en O(log n). No sabe nada del dominio: solo posiciones, valores y una
    operación para combinar.

    combinar: función (a, b) asociativa que une dos tramos contiguos
              (izquierdo primero). Ej.: suma, máximo.
    neutro:   valor que no altera a otro al combinar. Ej.: 0 para la suma.

    Convenciones:
        - Posiciones desde 0 hasta tamano() - 1.
        - Rangos cerrados: [desde, hasta] incluye ambos extremos.
        - Árbol vacío: consultar devuelve None.
        - Posición fuera de límites: IndexError. Rango invertido: ValueError.

    Representación: ArregloDinamico de 4n posiciones. La raíz está en 0 y
    los hijos de i están en 2i+1 y 2i+2.
    """

    def __init__(self, datos, combinar, neutro) -> None:
        """Construye el árbol desde una secuencia de valores. O(n)."""
        self._combinar = combinar
        self._neutro = neutro
        self._n = len(datos)
        self._arbol = ArregloDinamico()

        if self._n > 0:
            for _ in range(4 * self._n):
                self._arbol.agregaralfinal(neutro)
            self._construir(0, 0, self._n - 1, datos)

    # --------------------------------------------------
    # MÉTODOS PRIVADOS
    # --------------------------------------------------

    def _construir(self, nodo: int, izq: int, der: int, datos) -> None:
        """Llena el tramo [izq, der]: hojas copian el dato, el resto combina hijos. O(n)."""
        if izq == der:
            self._arbol.cambiarposicion(nodo, datos[izq])
            return

        medio = (izq + der) // 2
        hijo_izq = 2 * nodo + 1
        hijo_der = 2 * nodo + 2

        self._construir(hijo_izq, izq, medio, datos)
        self._construir(hijo_der, medio + 1, der, datos)
        self._recalcular(nodo, hijo_izq, hijo_der)

    def _recalcular(self, nodo: int, hijo_izq: int, hijo_der: int) -> None:
        """Combina el resumen de los dos hijos en el nodo. O(1)."""
        self._arbol.cambiarposicion(
            nodo,
            self._combinar(
                self._arbol.posicion(hijo_izq),
                self._arbol.posicion(hijo_der)
            )
        )

    def _actualizar(self, nodo: int, izq: int, der: int, posicion: int, valor) -> None:
        """Baja a la hoja, la cambia y recalcula al volver. O(log n)."""
        if izq == der:
            self._arbol.cambiarposicion(nodo, valor)
            return

        medio = (izq + der) // 2
        hijo_izq = 2 * nodo + 1
        hijo_der = 2 * nodo + 2

        if posicion <= medio:
            self._actualizar(hijo_izq, izq, medio, posicion, valor)
        else:
            self._actualizar(hijo_der, medio + 1, der, posicion, valor)

        self._recalcular(nodo, hijo_izq, hijo_der)

    def _consultar(self, nodo: int, izq: int, der: int, desde: int, hasta: int):
        """
        Usa el resumen del tramo si está dentro del rango; si no, baja a los
        hijos que lo toquen (izquierda primero). O(log n).
        """
        if desde <= izq and der <= hasta:
            return self._arbol.posicion(nodo)

        medio = (izq + der) // 2
        resultado = self._neutro

        if desde <= medio:
            resultado = self._combinar(
                resultado,
                self._consultar(2 * nodo + 1, izq, medio, desde, hasta)
            )

        if hasta > medio:
            resultado = self._combinar(
                resultado,
                self._consultar(2 * nodo + 2, medio + 1, der, desde, hasta)
            )

        return resultado

    def _validar_posicion(self, posicion: int) -> None:
        """Lanza IndexError si la posición no está en [0, n-1]. O(1)."""
        if posicion < 0 or posicion >= self._n:
            raise IndexError("Posición fuera de límites")

    # --------------------------------------------------
    # OPERACIONES PÚBLICAS
    # --------------------------------------------------

    def actualizar(self, posicion: int, valor) -> None:
        """Cambia el valor de una posición. IndexError si no existe. O(log n)."""
        self._validar_posicion(posicion)
        self._actualizar(0, 0, self._n - 1, posicion, valor)

    def consultar(self, desde: int, hasta: int):
        """
        Combina las posiciones desde..hasta (ambas incluidas).
        None si está vacío; ValueError si el rango está invertido;
        IndexError si algún extremo está fuera de límites. O(log n).
        """
        if self.esta_vacio():
            return None

        if desde > hasta:
            raise ValueError("Rango invertido: 'desde' no puede ser mayor que 'hasta'")

        self._validar_posicion(desde)
        self._validar_posicion(hasta)

        return self._consultar(0, 0, self._n - 1, desde, hasta)

    def consultar_todo(self):
        """Combina todas las posiciones (la raíz), o None si está vacío. O(1)."""
        if self.esta_vacio():
            return None

        return self._arbol.posicion(0)

    def tamano(self) -> int:
        """Cantidad de posiciones. O(1)."""
        return self._n

    def esta_vacio(self) -> bool:
        """True si no tiene posiciones. O(1)."""
        return self._n == 0