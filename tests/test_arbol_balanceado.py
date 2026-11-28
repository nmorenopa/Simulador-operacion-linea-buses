"""
Pruebas del ArbolAVL de estructuras/arbol_balanceado.py.

Recordatorio:
  - Es un árbol binario de búsqueda (ABB): a la izquierda de un nodo van las claves
    menores y a la derecha las mayores.
  - Es AVL: en cada nodo, la altura de sus dos subárboles difiere a lo más en 1.
    Si una inserción rompe eso, el árbol se arregla con rotaciones.
  - En el proyecto la clave será la distancia (en metros) desde Portal Américas
    y el valor, la estación.

Para correrlas, desde la carpeta raíz del proyecto:  pytest tests/test_arbol_balanceado.py
"""
import math
from random import Random

import pytest

from estructuras.arbol_balanceado import ArbolAVL, NodoAVL


# ---------------------------------------------------------------
# Ayudas
# ---------------------------------------------------------------
def arbol_con(claves):
    """Crea un árbol e inserta las claves en ese orden (el valor es la clave en texto)."""
    arbol = ArbolAVL()
    for clave in claves:
        arbol.insertar(clave, str(clave))
    return arbol


def es_abb(nodo, minimo=None, maximo=None):
    """True si todo el subárbol respeta la regla menor-izquierda / mayor-derecha."""
    if nodo is None:
        return True
    if minimo is not None and not nodo.clave > minimo:
        return False
    if maximo is not None and not nodo.clave < maximo:
        return False
    return (es_abb(nodo.izquierdo, minimo, nodo.clave)
            and es_abb(nodo.derecho, nodo.clave, maximo))


def contar_nodos(nodo):
    """Cuenta los nodos recorriendo el árbol (para comparar con tamano())."""
    if nodo is None:
        return 0
    return 1 + contar_nodos(nodo.izquierdo) + contar_nodos(nodo.derecho)


def claves_en_orden(arbol):
    """Solo las claves del recorrido en orden."""
    return [clave for clave, _ in arbol.en_orden()]


def es_avl_valido(arbol):
    """Reúne las tres condiciones: ABB, balance/alturas y tamaño correcto."""
    return (es_abb(arbol.raiz)
            and arbol.verificar_balance()
            and contar_nodos(arbol.raiz) == arbol.tamano())


# ---------------------------------------------------------------
# NodoAVL
# ---------------------------------------------------------------
def test_nodo_nuevo_es_una_hoja_de_altura_1():
    nodo = NodoAVL(1500, "Banderas")
    assert nodo.clave == 1500
    assert nodo.valor == "Banderas"
    assert nodo.izquierdo is None
    assert nodo.derecho is None
    assert nodo.altura == 1


# ---------------------------------------------------------------
# Árbol vacío
# ---------------------------------------------------------------
def test_arbol_nuevo_esta_vacio():
    arbol = ArbolAVL()
    assert arbol.esta_vacio()
    assert arbol.tamano() == 0
    assert arbol.raiz is None
    assert arbol.altura() == 0
    assert arbol.verificar_balance()


def test_buscar_en_vacio_devuelve_none():
    assert ArbolAVL().buscar(10) is None


def test_en_orden_de_vacio_es_lista_vacia():
    # Así 'for clave, valor in arbol.en_orden()' funciona aunque no haya nada
    assert ArbolAVL().en_orden() == []


def test_contiene_en_vacio_es_false():
    assert not ArbolAVL().contiene(10)


# ---------------------------------------------------------------
# Insertar y buscar
# ---------------------------------------------------------------
def test_insertar_uno():
    arbol = ArbolAVL()
    arbol.insertar(0, "Portal Américas")
    assert not arbol.esta_vacio()
    assert arbol.tamano() == 1
    assert arbol.altura() == 1
    assert arbol.raiz.clave == 0
    assert arbol.buscar(0) == "Portal Américas"


def test_buscar_encuentra_cada_clave_insertada():
    claves = [50, 20, 70, 10, 30, 60, 80]
    arbol = arbol_con(claves)
    for clave in claves:
        assert arbol.buscar(clave) == str(clave)


@pytest.mark.parametrize("clave", [-1, 0, 15, 25, 55, 75, 99])
def test_buscar_clave_que_no_existe_devuelve_none(clave):
    arbol = arbol_con([50, 20, 70, 10, 30, 60, 80])
    assert arbol.buscar(clave) is None


def test_insertar_clave_repetida_actualiza_el_valor():
    arbol = ArbolAVL()
    arbol.insertar(1200, "Estación vieja")
    arbol.insertar(1200, "Estación nueva")
    assert arbol.buscar(1200) == "Estación nueva"
    assert arbol.tamano() == 1                   # No se duplica


def test_insertar_repetida_no_cambia_la_forma_del_arbol():
    arbol = arbol_con([4, 2, 6, 1, 3, 5, 7])
    antes = (arbol.raiz.clave, arbol.altura(), claves_en_orden(arbol))
    arbol.insertar(1, "otro valor")
    arbol.insertar(7, "otro valor")
    despues = (arbol.raiz.clave, arbol.altura(), claves_en_orden(arbol))
    assert antes == despues
    assert arbol.tamano() == 7


def test_tamano_cuenta_solo_claves_distintas():
    arbol = arbol_con([5, 3, 5, 8, 3, 3, 1])
    assert arbol.tamano() == 4
    assert contar_nodos(arbol.raiz) == 4


def test_tamano_correcto_aunque_el_valor_sea_none():
    # Antes fallaba: insertar() usaba buscar(), que devuelve None tanto si la
    # clave no existe como si su valor es None, y el tamaño subía de más.
    arbol = ArbolAVL()
    arbol.insertar(5, None)
    arbol.insertar(5, None)
    assert arbol.tamano() == 1


def test_contiene_distingue_no_existe_de_valor_none():
    arbol = ArbolAVL()
    arbol.insertar(5, None)
    assert arbol.buscar(5) is None            # buscar() no basta para saberlo...
    assert arbol.contiene(5)                  # ...contiene() sí
    assert not arbol.contiene(6)


def test_contiene_cada_clave_insertada():
    arbol = arbol_con([50, 20, 70, 10, 30])
    for clave in [50, 20, 70, 10, 30]:
        assert arbol.contiene(clave)
    for clave in [0, 15, 60, 99]:
        assert not arbol.contiene(clave)


def test_acepta_claves_decimales():
    """Las distancias pueden venir con decimales (metros con fracción)."""
    arbol = ArbolAVL()
    for km in [3.5, 0.0, 12.25, 7.75]:
        arbol.insertar(km, f"km {km}")
    assert claves_en_orden(arbol) == [0.0, 3.5, 7.75, 12.25]
    assert arbol.buscar(7.75) == "km 7.75"


def test_acepta_claves_de_texto():
    """Por si el índice se arma por nombre de estación."""
    arbol = ArbolAVL()
    for nombre in ["Ricaurte", "Banderas", "Portal Norte", "Calle 100", "Av. Jiménez"]:
        arbol.insertar(nombre, len(nombre))
    assert claves_en_orden(arbol) == ["Av. Jiménez", "Banderas", "Calle 100",
                                      "Portal Norte", "Ricaurte"]
    assert arbol.buscar("Calle 100") == 9


def test_guarda_cualquier_objeto_como_valor():
    estacion = {"nombre": "Estación de ejemplo", "vagones": 3}
    arbol = ArbolAVL()
    arbol.insertar(2500, estacion)
    assert arbol.buscar(2500) is estacion   # El mismo objeto, no una copia


# ---------------------------------------------------------------
# Recorrido en orden
# ---------------------------------------------------------------
def test_en_orden_devuelve_parejas_ordenadas_por_clave():
    arbol = arbol_con([40, 10, 30, 20, 50])
    assert arbol.en_orden() == [(10, "10"), (20, "20"), (30, "30"),
                                (40, "40"), (50, "50")]


def test_en_orden_refleja_el_valor_actualizado():
    arbol = arbol_con([2, 1, 3])
    arbol.insertar(2, "nuevo")
    assert arbol.en_orden() == [(1, "1"), (2, "nuevo"), (3, "3")]


# ---------------------------------------------------------------
# Los cuatro casos de rotación
# Con 3 claves, el árbol debe quedar con la del medio en la raíz.
# ---------------------------------------------------------------
@pytest.mark.parametrize("caso, orden", [
    ("II: rotación simple a la derecha", [3, 2, 1]),
    ("DD: rotación simple a la izquierda", [1, 2, 3]),
    ("ID: doble, izquierda y luego derecha", [3, 1, 2]),
    ("DI: doble, derecha y luego izquierda", [1, 3, 2]),
])
def test_rotaciones_dejan_la_clave_del_medio_en_la_raiz(caso, orden):
    arbol = arbol_con(orden)
    assert arbol.raiz.clave == 2, caso
    assert arbol.raiz.izquierdo.clave == 1
    assert arbol.raiz.derecho.clave == 3
    # Alturas actualizadas después de rotar
    assert arbol.raiz.altura == 2
    assert arbol.raiz.izquierdo.altura == 1
    assert arbol.raiz.derecho.altura == 1
    assert es_avl_valido(arbol)


def test_rotacion_conserva_el_subarbol_que_cambia_de_padre():
    """
    Caso II con más nodos: al rotar a la derecha alrededor de 30, el hijo derecho
    de 20 (la clave 25) debe pasar a ser el hijo izquierdo de 30.
          30                 20
         /  \\              /  \\
       20    40   --->    10    30
      /  \\                /     / \\
    10    25             5    25  40
    /
   5
    """
    arbol = arbol_con([30, 20, 40, 10, 25, 5])
    assert arbol.raiz.clave == 20
    assert arbol.raiz.izquierdo.clave == 10
    assert arbol.raiz.izquierdo.izquierdo.clave == 5
    assert arbol.raiz.derecho.clave == 30
    assert arbol.raiz.derecho.izquierdo.clave == 25
    assert arbol.raiz.derecho.derecho.clave == 40
    assert es_avl_valido(arbol)


def test_rotacion_doble_con_subarboles():
    """
    Caso DI con más nodos: insertar 35 desbalancea 20 por la derecha y el camino
    va derecha (40) -> izquierda (30). Tras la rotación doble, 30 queda en la raíz.
    """
    arbol = arbol_con([20, 10, 40, 30, 50, 35])
    assert arbol.raiz.clave == 30
    assert arbol.raiz.izquierdo.clave == 20
    assert arbol.raiz.derecho.clave == 40
    assert claves_en_orden(arbol) == [10, 20, 30, 35, 40, 50]
    assert es_avl_valido(arbol)


def test_rotacion_izquierda_directa_actualiza_alturas():
    """
    Se llama a la rotación a mano (sin insertar) sobre un árbol armado a mano.
    Al solo insertar, un error en la altura del nodo que sube puede quedar
    escondido; aquí no, y servirá cuando el árbol tenga eliminar.
        1                    3
         \\                 /
          3      --->      1
         /                  \\
        2                    2
    """
    uno, tres, dos = NodoAVL(1, "a"), NodoAVL(3, "c"), NodoAVL(2, "b")
    uno.derecho, tres.izquierdo = tres, dos
    tres.altura, uno.altura = 2, 3
    nueva_raiz = ArbolAVL()._rotacion_izquierda(uno)
    assert nueva_raiz is tres
    assert tres.izquierdo is uno
    assert uno.derecho is dos                 # El subárbol cambia de padre
    assert uno.altura == 2
    assert tres.altura == 3


def test_rotacion_derecha_directa_actualiza_alturas():
    """Espejo de la anterior."""
    tres, uno, dos = NodoAVL(3, "c"), NodoAVL(1, "a"), NodoAVL(2, "b")
    tres.izquierdo, uno.derecho = uno, dos
    uno.altura, tres.altura = 2, 3
    nueva_raiz = ArbolAVL()._rotacion_derecha(tres)
    assert nueva_raiz is uno
    assert uno.derecho is tres
    assert tres.izquierdo is dos
    assert tres.altura == 2
    assert uno.altura == 3


# ---------------------------------------------------------------
# Balance y altura
# ---------------------------------------------------------------
def test_claves_crecientes_no_degeneran_en_lista():
    """
    En un ABB sin balanceo, insertar 1, 2, 3, ... forma una "lista" de altura n.
    En un AVL, 2^k - 1 claves seguidas forman un árbol perfecto de altura k.
    """
    arbol = arbol_con(range(1, 1024))         # 1023 = 2^10 - 1 claves
    assert arbol.tamano() == 1023
    assert arbol.altura() == 10
    assert es_avl_valido(arbol)


def test_claves_decrecientes_no_degeneran_en_lista():
    arbol = arbol_con(range(1023, 0, -1))
    assert arbol.altura() == 10
    assert es_avl_valido(arbol)


@pytest.mark.parametrize("n", [1, 2, 3, 7, 30, 100, 1000])
def test_altura_dentro_del_limite_de_un_avl(n):
    """Teorema del AVL: altura < 1.44 * log2(n + 2). Por eso buscar es O(log n)."""
    azar = Random(n)
    claves = list(range(n))
    azar.shuffle(claves)
    arbol = arbol_con(claves)
    assert arbol.altura() < 1.44 * math.log2(n + 2)


def test_cada_nodo_guarda_su_altura_correcta():
    def revisar(nodo):
        if nodo is None:
            return 0
        real = 1 + max(revisar(nodo.izquierdo), revisar(nodo.derecho))
        assert nodo.altura == real
        return real

    revisar(arbol_con([8, 3, 10, 1, 6, 14, 4, 7, 13, 2, 5]).raiz)


def test_balance_se_mantiene_despues_de_cada_insercion():
    arbol = ArbolAVL()
    for clave in [50, 40, 30, 20, 10, 5, 60, 70, 65, 66, 1, 2, 3]:
        arbol.insertar(clave, clave)
        assert es_avl_valido(arbol), f"Se rompió al insertar {clave}"


# ---------------------------------------------------------------
# verificar_balance debe detectar árboles mal formados
# (se arman a mano, sin pasar por insertar)
# ---------------------------------------------------------------
def test_verificar_balance_detecta_un_arbol_desbalanceado():
    # 1 -> 2 -> 3 todos a la derecha: el nodo 1 tiene balance -2
    a, b, c = NodoAVL(1, "a"), NodoAVL(2, "b"), NodoAVL(3, "c")
    a.derecho, b.derecho = b, c
    b.altura, a.altura = 2, 3
    arbol = ArbolAVL()
    arbol.raiz = a
    assert not arbol.verificar_balance()


def test_verificar_balance_detecta_una_altura_mal_guardada():
    a, b = NodoAVL(2, "a"), NodoAVL(1, "b")
    a.izquierdo = b
    a.altura = 5                              # Debería ser 2
    arbol = ArbolAVL()
    arbol.raiz = a
    assert not arbol.verificar_balance()


# ---------------------------------------------------------------
# rango(desde, hasta): claves entre dos valores, ambos incluidos
# ---------------------------------------------------------------
def test_rango_en_vacio_es_lista_vacia():
    assert ArbolAVL().rango(0, 100) == []


def test_rango_devuelve_parejas_ordenadas():
    arbol = arbol_con([50, 20, 70, 10, 30, 60, 80])
    assert arbol.rango(25, 65) == [(30, "30"), (50, "50"), (60, "60")]


def test_rango_incluye_los_dos_extremos():
    arbol = arbol_con([10, 20, 30, 40])
    assert [c for c, _ in arbol.rango(20, 40)] == [20, 30, 40]


def test_rango_de_un_solo_punto():
    arbol = arbol_con([10, 20, 30])
    assert arbol.rango(20, 20) == [(20, "20")]
    assert arbol.rango(25, 25) == []


def test_rango_que_cubre_todo_es_igual_a_en_orden():
    arbol = arbol_con([5, 1, 9, 3, 7])
    assert arbol.rango(-100, 100) == arbol.en_orden()


@pytest.mark.parametrize("desde, hasta", [(-10, -1), (100, 200), (21, 29)])
def test_rango_sin_claves_adentro_es_vacio(desde, hasta):
    arbol = arbol_con([10, 20, 30, 40, 50])
    assert arbol.rango(desde, hasta) == []


def test_rango_al_reves_es_vacio():
    arbol = arbol_con([10, 20, 30])
    assert arbol.rango(30, 10) == []


def test_rango_no_cambia_el_arbol():
    arbol = arbol_con(range(20))
    antes = arbol.en_orden()
    arbol.rango(5, 12)
    assert arbol.en_orden() == antes
    assert arbol.tamano() == 20


# ---------------------------------------------------------------
# piso(clave): la mayor clave que sea menor o igual a la pedida
# ---------------------------------------------------------------
def test_piso_en_vacio_es_none():
    assert ArbolAVL().piso(10) is None


@pytest.mark.parametrize("pedida, esperada", [
    (10, 10),      # Existe: el piso es ella misma
    (15, 10),      # Entre 10 y 20: el piso es 10
    (29.9, 20),
    (50, 50),      # La mayor de todas
    (1000, 50),    # Más allá de la última: la última
])
def test_piso_devuelve_la_mayor_clave_menor_o_igual(pedida, esperada):
    arbol = arbol_con([30, 10, 50, 20, 40])
    assert arbol.piso(pedida) == (esperada, str(esperada))


def test_piso_antes_de_la_primera_clave_es_none():
    arbol = arbol_con([30, 10, 50])
    assert arbol.piso(9) is None


# ---------------------------------------------------------------
# techo(clave): la menor clave que sea mayor o igual a la pedida
# ---------------------------------------------------------------
def test_techo_en_vacio_es_none():
    assert ArbolAVL().techo(10) is None


@pytest.mark.parametrize("pedida, esperada", [
    (10, 10),      # Existe: el techo es ella misma
    (15, 20),      # Entre 10 y 20: el techo es 20
    (20.1, 30),
    (-100, 10),    # Antes de la primera: la primera
    (50, 50),      # La mayor de todas
])
def test_techo_devuelve_la_menor_clave_mayor_o_igual(pedida, esperada):
    arbol = arbol_con([30, 10, 50, 20, 40])
    assert arbol.techo(pedida) == (esperada, str(esperada))


def test_techo_despues_de_la_ultima_clave_es_none():
    arbol = arbol_con([30, 10, 50])
    assert arbol.techo(51) is None


# ---------------------------------------------------------------
# minimo() y maximo()
# ---------------------------------------------------------------
def test_minimo_y_maximo_en_vacio_son_none():
    arbol = ArbolAVL()
    assert arbol.minimo() is None
    assert arbol.maximo() is None


def test_minimo_y_maximo_con_una_sola_clave_son_la_misma():
    arbol = arbol_con([7])
    assert arbol.minimo() == (7, "7")
    assert arbol.maximo() == (7, "7")


def test_minimo_y_maximo_devuelven_los_extremos():
    arbol = arbol_con([30, 10, 50, 20, 40, 5, 60])
    assert arbol.minimo() == (5, "5")
    assert arbol.maximo() == (60, "60")


def test_minimo_y_maximo_no_cambian_el_arbol():
    arbol = arbol_con([30, 10, 50, 20, 40])
    antes = arbol.en_orden()
    arbol.minimo()
    arbol.maximo()
    assert arbol.en_orden() == antes
    assert arbol.tamano() == 5


def test_maximo_con_claves_compuestas_da_la_peor_espera():
    """
    Uso decidido del AVL: clave (tiempo_espera, id_pasajero). Entre dos con la
    misma espera, gana el id mayor (comparación de tuplas posición por posición).
    """
    arbol = ArbolAVL()
    for espera, id_pasajero in [(3, 0), (9, 1), (2, 2), (9, 3), (5, 4)]:
        arbol.insertar((espera, id_pasajero), f"P{id_pasajero}")
    assert arbol.maximo() == ((9, 3), "P3")
    assert arbol.minimo() == ((2, 2), "P2")


# ---------------------------------------------------------------
# Pruebas al azar contra un diccionario de referencia
# ---------------------------------------------------------------
@pytest.mark.parametrize("semilla", range(20))
def test_al_azar_igual_que_un_diccionario(semilla):
    azar = Random(semilla)
    arbol = ArbolAVL()
    referencia = {}
    for _ in range(azar.randint(0, 150)):
        clave = azar.randint(0, 80)           # Rango chico: habrá claves repetidas
        valor = azar.random()
        arbol.insertar(clave, valor)
        referencia[clave] = valor
        assert es_avl_valido(arbol)
    assert arbol.tamano() == len(referencia)
    assert arbol.en_orden() == sorted(referencia.items())
    for clave in range(-5, 90):
        assert arbol.buscar(clave) == referencia.get(clave)
        assert arbol.contiene(clave) == (clave in referencia)
        # piso: la mayor clave de la referencia que sea <= clave
        menores = [k for k in referencia if k <= clave]
        esperado = (max(menores), referencia[max(menores)]) if menores else None
        assert arbol.piso(clave) == esperado
        # techo: la menor clave de la referencia que sea >= clave
        mayores = [k for k in referencia if k >= clave]
        esperado = (min(mayores), referencia[min(mayores)]) if mayores else None
        assert arbol.techo(clave) == esperado
    if referencia:
        assert arbol.minimo() == (min(referencia), referencia[min(referencia)])
        assert arbol.maximo() == (max(referencia), referencia[max(referencia)])
    else:
        assert arbol.minimo() is None and arbol.maximo() is None
    for _ in range(30):
        desde, hasta = azar.randint(-5, 90), azar.randint(-5, 90)
        esperado = sorted((k, v) for k, v in referencia.items() if desde <= k <= hasta)
        assert arbol.rango(desde, hasta) == esperado


# ---------------------------------------------------------------
# Uso del proyecto: índice de estaciones por distancia desde Portal Américas
# (distancias de ejemplo, NO son las reales de la troncal)
# ---------------------------------------------------------------
ESTACIONES_EJEMPLO = [
    (0, "Portal Américas"),
    (1800, "Estación B"),
    (950, "Estación A"),
    (4100, "Estación D"),
    (2700, "Estación C"),
    (26500, "Portal Norte"),
]


def test_indice_de_estaciones_queda_ordenado_por_distancia():
    arbol = ArbolAVL()
    for metros, nombre in ESTACIONES_EJEMPLO:
        arbol.insertar(metros, nombre)
    nombres = [nombre for _, nombre in arbol.en_orden()]
    assert nombres == ["Portal Américas", "Estación A", "Estación B",
                       "Estación C", "Estación D", "Portal Norte"]
    assert arbol.buscar(2700) == "Estación C"
    assert arbol.buscar(2701) is None
    assert es_avl_valido(arbol)


def test_indice_estaciones_entre_dos_kilometros():
    arbol = ArbolAVL()
    for metros, nombre in ESTACIONES_EJEMPLO:
        arbol.insertar(metros, nombre)
    # Entre el km 1 y el km 3
    entre = [nombre for _, nombre in arbol.rango(1000, 3000)]
    assert entre == ["Estación B", "Estación C"]


def test_indice_ultima_estacion_antes_de_un_kilometro():
    arbol = ArbolAVL()
    for metros, nombre in ESTACIONES_EJEMPLO:
        arbol.insertar(metros, nombre)
    assert arbol.piso(3500) == (2700, "Estación C")   # Un bus en el metro 3500
    assert arbol.piso(4100) == (4100, "Estación D")   # Justo en la estación
    assert arbol.piso(0) == (0, "Portal Américas")
