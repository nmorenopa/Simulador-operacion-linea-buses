from typing import Any, Literal

from estructuras.arreglo_dinamico import ArregloDinamico


class Monticulo:
    """
    Montículo (heap) sobre un ArregloDinamico.
    Puede ser de mínimos o de máximos:
      - De mínimos: cada padre es menor o igual a sus hijos; la raíz es el MENOR.
      - De máximos: cada padre es mayor o igual a sus hijos; la raíz es el MAYOR.
    Posición i: padre en (i-1)//2, hijos en 2i+1 y 2i+2.

    Contrato (precondición del TDA): los elementos deben poder compararse
    entre sí con "<" (números, textos, tuplas de esos, o cualquier clase que
    defina __lt__). El montículo no sabe qué guarda: solo los compara.

    Empates: se permiten. Como la regla es "menor o igual" (o "mayor o igual"),
    dos elementos iguales pueden convivir sin problema. Pero el montículo NO es
    estable: entre empatados, no garantiza que salga primero el que llegó antes.

    Claves compuestas (tuplas): Python las compara posición por posición, y solo
    mira el siguiente componente si hay empate en el anterior. Por eso cada
    componente al que se pueda llegar debe ser comparable. Si la tupla lleva un
    objeto que no se compara (por ejemplo, un Bus), se pone antes un contador
    que nunca se repita:
        (minuto, contador, bus)
    Así Python nunca llega a comparar los buses (evita un TypeError) y, de paso,
    entre empatados sale primero el que llegó antes.

    Orden mixto: para "mayor primero" en un componente y "menor primero" en otro,
    se niega el que va al revés. Ej.: (-ocupacion, id) en uno de mínimos da la
    mayor ocupación primero y, si empatan, el menor id.
    """

    def __init__(self, tipo: Literal["minimos", "maximos"]) -> None:
        """Crea un montículo vacío del tipo indicado ("minimos" o "maximos"). O(1)."""
        if tipo not in ("minimos", "maximos"):
            raise ValueError('Tipo de montículo no válido: use "minimos" o "maximos"')
        self.tipo = tipo
        self._es_min = tipo == "minimos"
        self.elementos = ArregloDinamico()

    def es_de_minimos(self) -> bool:
        """True si es de mínimos: padre menor o igual a sus hijos (p <= h). O(1)."""
        return self._es_min

    def es_de_maximos(self) -> bool:
        """True si es de máximos: padre mayor o igual a sus hijos (p >= h). O(1)."""
        return not self._es_min

    def tamano(self) -> int:
        """Cantidad de elementos. O(1)."""
        return self.elementos.tamano()

    def esta_vacio(self) -> bool:
        """True si no tiene elementos. O(1)."""
        return self.elementos.esta_vacio()

    def ver_raiz(self) -> Any:
        """Devuelve la raíz sin sacarla (mínimo o máximo según el tipo). O(1)."""
        if self.esta_vacio():
            raise IndexError("El montículo no tiene elementos")
        return self.elementos.posicion(0)

    def insertar(self, elemento: Any) -> None:
        """Inserta un elemento y restaura la propiedad del montículo. O(log n)."""
        self.elementos.agregaralfinal(elemento)
        self._subir(self.elementos.tamano() - 1)

    def extraer_raiz(self) -> Any:
        """
        Elimina y devuelve la raíz. O(log n).
          - de mínimos: devuelve el mínimo
          - de máximos: devuelve el máximo
        """
        if self.esta_vacio():
            raise IndexError("El montículo no tiene elementos")
        raiz = self.elementos.posicion(0)
        # El último elemento tapa el hueco de la raíz y luego se hunde a su lugar
        ultimo = self.elementos.borraralfinal()
        if not self.esta_vacio():
            self.elementos.cambiarposicion(0, ultimo)
            self._hundir(0)
        return raiz

    def mostrar(self) -> list:
        """Copia de los elementos en orden de arreglo (no ordenado). O(n)."""
        return self.elementos.mostrar()

    # ---------- Métodos privados ----------

    def _antes(self, a: Any, b: Any) -> bool:
        """True si 'a' debe quedar por encima de 'b'. O(1)."""
        return a < b if self._es_min else a > b

    def _subir(self, i: int) -> None:
        """
        Sube el elemento de la posición i hasta su lugar. O(log n).
        Técnica del "hueco": en vez de intercambiar en cada nivel, se guarda el
        dato aparte, se bajan los padres uno a uno y el dato se escribe una sola
        vez, al final, en el lugar que le corresponde.
        """
        dato = self.elementos.posicion(i)
        while i > 0:
            i_padre = self._padre(i)
            padre = self.elementos.posicion(i_padre)
            if not self._antes(dato, padre):
                break
            self.elementos.cambiarposicion(i, padre)  # el padre baja
            i = i_padre
        self.elementos.cambiarposicion(i, dato)

    def _hundir(self, i: int) -> None:
        """
        Baja el elemento de la posición i hasta su lugar. O(log n).
        En cada nivel elige el "mejor" de los dos hijos (el menor en uno de
        mínimos, el mayor en uno de máximos) y, si va antes que el dato, lo sube.
        También usa la técnica del "hueco" (ver _subir).
        """
        n = self.elementos.tamano()
        dato = self.elementos.posicion(i)
        while True:
            izq = self._hijo_izquierdo(i)
            if izq >= n:
                break                                 # Sin hijos: es una hoja
            hijo = izq
            valor = self.elementos.posicion(izq)
            der = self._hijo_derecho(i)
            if der < n:                               # ¿Existe el hijo derecho?
                valor_der = self.elementos.posicion(der)
                if self._antes(valor_der, valor):
                    hijo, valor = der, valor_der
            if not self._antes(valor, dato):
                break
            self.elementos.cambiarposicion(i, valor)  # el hijo sube
            i = hijo
        self.elementos.cambiarposicion(i, dato)

    def _padre(self, i: int) -> int:
        """Posición del padre del nodo i. O(1)."""
        return (i - 1) // 2

    def _hijo_izquierdo(self, i: int) -> int:
        """Posición del hijo izquierdo del nodo i. O(1)."""
        return 2 * i + 1

    def _hijo_derecho(self, i: int) -> int:
        """Posición del hijo derecho del nodo i. O(1)."""
        return 2 * i + 2
