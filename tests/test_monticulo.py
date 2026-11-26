"""
Pruebas del Monticulo (montículo, en inglés "heap") de estructuras/monticulo.py.

Recordatorio:
  - montículo de mínimos: la raíz es siempre el MENOR elemento (sale primero el más pequeño).
  - montículo de máximos: la raíz es siempre el MAYOR elemento (sale primero el más grande).
  - El arreglo guarda un árbol binario "casi completo": el padre de la posición i
    está en (i - 1) // 2 y sus hijos en 2i + 1 y 2i + 2.

Para correrlas, desde la carpeta raíz del proyecto:  pytest tests/test_monticulo.py
"""
import math
from random import Random

import pytest

from estructuras.monticulo import Monticulo


# ---------------------------------------------------------------
# Ayudas
# ---------------------------------------------------------------
def vaciar(monticulo):
    """Extrae todo y devuelve una lista con los elementos en el orden en que salen."""
    salida = []
    while not monticulo.vacio():
        salida.append(monticulo.extraer_raiz())
    return salida


def cumple_propiedad(lista, es_min):
    """
    Revisa la "propiedad del montículo" directamente sobre el arreglo:
    cada padre debe ir antes (o empatar) con cada uno de sus hijos.
    """
    for i in range(1, len(lista)):
        padre = lista[(i - 1) // 2]
        hijo = lista[i]
        if es_min and padre > hijo:
            return False
        if not es_min and padre < hijo:
            return False
    return True


class Contador:
    """
    Envuelve un número y cuenta cuántas comparaciones (< y >) se hacen.
    Sirve para comprobar en la práctica que insertar y extraer son O(log n).
    """
    comparaciones = 0

    def __init__(self, valor):
        self.valor = valor

    def __lt__(self, otro):
        Contador.comparaciones += 1
        return self.valor < otro.valor

    def __gt__(self, otro):
        Contador.comparaciones += 1
        return self.valor > otro.valor


class BusFalso:
    """Objeto que Python NO sabe comparar (no define < ni >), como un Bus real."""

    def __init__(self, id_bus):
        self.id_bus = id_bus


# ---------------------------------------------------------------
# Constructor y tipo
# ---------------------------------------------------------------
@pytest.mark.parametrize("tipo", ["minimos", "maximos"])
def test_monticulo_nuevo_esta_vacio(tipo):
    m = Monticulo(tipo)
    assert m.vacio()
    assert m.longitud() == 0
    assert m.mostrar() == []


@pytest.mark.parametrize("tipo", ["min-heap", "max-heap", "minimo", "MINIMOS", "mínimos", "", None, 0])
def test_tipo_no_valido_lanza_error(tipo):
    with pytest.raises(ValueError):
        Monticulo(tipo)


def test_de_minimos_se_reconoce_como_tal():
    m = Monticulo("minimos")
    assert m.tipo == "minimos"
    assert m.es_de_minimos()
    assert not m.es_de_maximos()


def test_de_maximos_se_reconoce_como_tal():
    m = Monticulo("maximos")
    assert m.tipo == "maximos"
    assert m.es_de_maximos()
    assert not m.es_de_minimos()


# ---------------------------------------------------------------
# Montículo vacío: errores esperados
# ---------------------------------------------------------------
@pytest.mark.parametrize("tipo", ["minimos", "maximos"])
def test_ver_raiz_en_vacio_lanza_error(tipo):
    with pytest.raises(IndexError):
        Monticulo(tipo).ver_raiz()


@pytest.mark.parametrize("tipo", ["minimos", "maximos"])
def test_extraer_en_vacio_lanza_error(tipo):
    with pytest.raises(IndexError):
        Monticulo(tipo).extraer_raiz()


def test_extraer_despues_de_vaciar_lanza_error():
    m = Monticulo("minimos")
    m.insertar(1)
    m.extraer_raiz()
    with pytest.raises(IndexError):
        m.extraer_raiz()


# ---------------------------------------------------------------
# Un solo elemento
# ---------------------------------------------------------------
@pytest.mark.parametrize("tipo", ["minimos", "maximos"])
def test_un_elemento_es_la_raiz(tipo):
    m = Monticulo(tipo)
    m.insertar(42)
    assert m.ver_raiz() == 42
    assert m.longitud() == 1
    assert not m.vacio()


@pytest.mark.parametrize("tipo", ["minimos", "maximos"])
def test_extraer_el_unico_elemento_lo_deja_vacio(tipo):
    m = Monticulo(tipo)
    m.insertar(42)
    assert m.extraer_raiz() == 42
    assert m.vacio()
    assert m.longitud() == 0


# ---------------------------------------------------------------
# Orden de salida
# ---------------------------------------------------------------
def test_de_minimos_saca_de_menor_a_mayor():
    m = Monticulo("minimos")
    for x in [5, 3, 8, 1, 9, 2, 7]:
        m.insertar(x)
    assert vaciar(m) == [1, 2, 3, 5, 7, 8, 9]


def test_de_maximos_saca_de_mayor_a_menor():
    m = Monticulo("maximos")
    for x in [5, 3, 8, 1, 9, 2, 7]:
        m.insertar(x)
    assert vaciar(m) == [9, 8, 7, 5, 3, 2, 1]


def test_de_minimos_con_datos_que_llegan_ordenados_al_reves():
    # Peor caso para insertar en un montículo de mínimos: cada nuevo dato sube hasta la raíz.
    m = Monticulo("minimos")
    for x in range(20, 0, -1):
        m.insertar(x)
    assert vaciar(m) == list(range(1, 21))


def test_de_maximos_con_datos_que_llegan_ordenados():
    # Peor caso para insertar en un montículo de máximos.
    m = Monticulo("maximos")
    for x in range(1, 21):
        m.insertar(x)
    assert vaciar(m) == list(range(20, 0, -1))


@pytest.mark.parametrize("tipo, al_reves", [("minimos", False), ("maximos", True)])
def test_acepta_repetidos(tipo, al_reves):
    m = Monticulo(tipo)
    datos = [4, 1, 4, 4, 1, 7, 7, 0, 4]
    for x in datos:
        m.insertar(x)
    assert vaciar(m) == sorted(datos, reverse=al_reves)


@pytest.mark.parametrize("tipo", ["minimos", "maximos"])
def test_todos_iguales(tipo):
    m = Monticulo(tipo)
    for _ in range(6):
        m.insertar(3)
    assert vaciar(m) == [3] * 6


def test_acepta_negativos_y_decimales():
    m = Monticulo("minimos")
    for x in [0.5, -3, 2, -3.5, 0]:
        m.insertar(x)
    assert vaciar(m) == [-3.5, -3, 0, 0.5, 2]


def test_acepta_textos_en_orden_alfabetico():
    m = Monticulo("minimos")
    for nombre in ["Ricaurte", "Banderas", "Portal Norte", "Calle 100"]:
        m.insertar(nombre)
    assert vaciar(m) == ["Banderas", "Calle 100", "Portal Norte", "Ricaurte"]


# ---------------------------------------------------------------
# ver_raiz, longitud y mostrar
# ---------------------------------------------------------------
def test_ver_raiz_no_saca_el_elemento():
    m = Monticulo("minimos")
    for x in [3, 1, 2]:
        m.insertar(x)
    assert m.ver_raiz() == 1
    assert m.ver_raiz() == 1      # Mirar dos veces no cambia nada
    assert m.longitud() == 3


def test_ver_raiz_se_actualiza_al_insertar_uno_mejor():
    m = Monticulo("minimos")
    m.insertar(10)
    assert m.ver_raiz() == 10
    m.insertar(20)                 # Peor que la raíz: la raíz no cambia
    assert m.ver_raiz() == 10
    m.insertar(5)                  # Mejor que la raíz: pasa a ser la raíz
    assert m.ver_raiz() == 5


def test_longitud_sube_y_baja():
    m = Monticulo("maximos")
    for k, x in enumerate([4, 8, 1, 6], start=1):
        m.insertar(x)
        assert m.longitud() == k
    for k in range(3, -1, -1):
        m.extraer_raiz()
        assert m.longitud() == k


def test_mostrar_devuelve_el_arreglo_con_la_raiz_primero():
    m = Monticulo("minimos")
    for x in [5, 3, 8, 1]:
        m.insertar(x)
    lista = m.mostrar()
    assert len(lista) == 4
    assert lista[0] == 1                     # La raíz está en la posición 0
    assert sorted(lista) == [1, 3, 5, 8]     # Están todos, aunque no ordenados
    assert cumple_propiedad(lista, es_min=True)


def test_mostrar_es_una_copia():
    m = Monticulo("minimos")
    for x in [2, 1]:
        m.insertar(x)
    copia = m.mostrar()
    copia.append(-100)                       # Cambiar la copia...
    copia[0] = 999
    assert m.mostrar() == [1, 2]             # ...no cambia el montículo
    assert m.longitud() == 2


def test_dos_monticulos_son_independientes():
    a = Monticulo("minimos")
    b = Monticulo("minimos")
    a.insertar(1)
    assert b.vacio()
    assert a.elementos is not b.elementos


# ---------------------------------------------------------------
# Propiedad del montículo después de cada operación
# ---------------------------------------------------------------
@pytest.mark.parametrize("tipo", ["minimos", "maximos"])
def test_la_propiedad_se_cumple_tras_cada_operacion(tipo):
    es_min = tipo == "minimos"
    m = Monticulo(tipo)
    azar = Random(7)
    for _ in range(200):
        m.insertar(azar.randint(0, 50))
        assert cumple_propiedad(m.mostrar(), es_min)
    while not m.vacio():
        m.extraer_raiz()
        assert cumple_propiedad(m.mostrar(), es_min)


# ---------------------------------------------------------------
# Pruebas al azar contra una referencia sencilla
# (sorted() solo se usa aquí, en las pruebas, para comparar resultados)
# ---------------------------------------------------------------
@pytest.mark.parametrize("semilla", range(25))
@pytest.mark.parametrize("tipo, al_reves", [("minimos", False), ("maximos", True)])
def test_al_azar_igual_que_ordenar(semilla, tipo, al_reves):
    azar = Random(semilla)
    datos = [azar.randint(-100, 100) for _ in range(azar.randint(0, 80))]
    m = Monticulo(tipo)
    for x in datos:
        m.insertar(x)
    assert vaciar(m) == sorted(datos, reverse=al_reves)


@pytest.mark.parametrize("semilla", range(15))
def test_al_azar_insertando_y_extrayendo_intercalado(semilla):
    """Mezcla inserciones y extracciones; la raíz siempre debe ser el mínimo actual."""
    azar = Random(semilla)
    m = Monticulo("minimos")
    referencia = []                          # Lista normal con los mismos datos
    for _ in range(300):
        if referencia and azar.random() < 0.4:
            esperado = min(referencia)
            referencia.remove(esperado)
            assert m.extraer_raiz() == esperado
        else:
            x = azar.randint(0, 30)
            m.insertar(x)
            referencia.append(x)
        assert m.longitud() == len(referencia)
        if referencia:
            assert m.ver_raiz() == min(referencia)


def test_muchos_elementos():
    m = Monticulo("maximos")
    azar = Random(2026)
    datos = [azar.randint(0, 10_000) for _ in range(5_000)]
    for x in datos:
        m.insertar(x)
    assert m.longitud() == 5_000
    assert vaciar(m) == sorted(datos, reverse=True)


# ---------------------------------------------------------------
# Complejidad: insertar y extraer hacen O(log n) comparaciones
# ---------------------------------------------------------------
def test_insertar_hace_a_lo_sumo_log_n_comparaciones():
    """
    Al insertar, el dato sube a lo más la altura del árbol: floor(log2 n) niveles,
    con una comparación por nivel. Peor caso en montículo de mínimos: datos de mayor a menor.
    """
    m = Monticulo("minimos")
    n = 1024
    peor = 0
    for x in range(n, 0, -1):
        Contador.comparaciones = 0
        m.insertar(Contador(x))
        peor = max(peor, Contador.comparaciones)
    assert peor <= math.floor(math.log2(n))


def test_extraer_hace_a_lo_sumo_2_log_n_comparaciones():
    """
    Al extraer, el dato baja nivel por nivel; en cada nivel compara los dos hijos
    entre sí y el mejor con el dato: 2 comparaciones por nivel.
    """
    m = Monticulo("minimos")
    azar = Random(1)
    n = 1024
    for _ in range(n):
        m.insertar(Contador(azar.randint(0, 10_000)))
    peor = 0
    while not m.vacio():
        Contador.comparaciones = 0
        m.extraer_raiz()
        peor = max(peor, Contador.comparaciones)
    assert peor <= 2 * math.floor(math.log2(n))


# ---------------------------------------------------------------
# Límite: los elementos deben poder compararse entre sí
# ---------------------------------------------------------------
def test_elementos_que_no_se_pueden_comparar_lanzan_error():
    m = Monticulo("minimos")
    m.insertar(1)
    with pytest.raises(TypeError):
        m.insertar("uno")                    # Python no sabe si "uno" < 1


# ---------------------------------------------------------------
# Uso 1 del proyecto: despachos programados (montículo de mínimos)
# Cada evento es (minuto, contador, id_bus).
# ---------------------------------------------------------------
def test_despachos_sale_primero_el_minuto_mas_proximo():
    despachos = Monticulo("minimos")
    despachos.insertar((12, 0, "B1"))
    despachos.insertar((5, 1, "B2"))
    despachos.insertar((9, 2, "B3"))
    assert [evento[2] for evento in vaciar(despachos)] == ["B2", "B3", "B1"]


def test_despachos_mismo_minuto_sale_en_orden_de_llegada():
    """
    El montículo no es "estable" por sí solo: con dos eventos del mismo minuto no
    garantiza cuál sale primero. El contador de llegada desempata.
    """
    despachos = Monticulo("minimos")
    contador = 0
    for id_bus in ["B7", "B2", "B9", "B1", "B5", "B3"]:
        despachos.insertar((10, contador, id_bus))
        contador += 1
    despachos.insertar((4, contador, "B8"))
    salida = [evento[2] for evento in vaciar(despachos)]
    assert salida == ["B8", "B7", "B2", "B9", "B1", "B5", "B3"]


def test_despachos_con_el_mismo_orden_de_entrada_sale_siempre_lo_mismo():
    """Reproducible: misma semilla -> mismos eventos -> misma salida."""
    def correr():
        azar = Random(42)
        despachos = Monticulo("minimos")
        for contador in range(50):
            despachos.insertar((azar.randint(0, 10), contador, f"B{contador}"))
        return vaciar(despachos)

    assert correr() == correr()


def test_el_contador_evita_comparar_los_buses():
    """
    Si dos eventos empatan en el minuto, Python compara el siguiente campo de la
    tupla. Con el contador (que nunca se repite) jamás llega a comparar el Bus.
    """
    despachos = Monticulo("minimos")
    b1, b2, b3 = BusFalso("B1"), BusFalso("B2"), BusFalso("B3")
    despachos.insertar((10, 0, b1))
    despachos.insertar((10, 1, b2))
    despachos.insertar((10, 2, b3))
    assert [evento[2] for evento in vaciar(despachos)] == [b1, b2, b3]


def test_sin_contador_dos_buses_del_mismo_minuto_lanzan_error():
    """Muestra POR QUÉ hace falta el contador."""
    despachos = Monticulo("minimos")
    despachos.insertar((10, BusFalso("B1")))
    with pytest.raises(TypeError):
        despachos.insertar((10, BusFalso("B2")))


# ---------------------------------------------------------------
# Uso 2 del proyecto: ranking de andenes saturados (montículo de máximos)
# Cada elemento es (pasajeros_esperando, id_anden).
# ---------------------------------------------------------------
def test_ranking_sale_primero_el_anden_mas_lleno():
    ranking = Monticulo("maximos")
    for esperando, anden in [(3, "A1"), (15, "A2"), (0, "A3"), (8, "A4"), (12, "A5")]:
        ranking.insertar((esperando, anden))
    top_3 = [ranking.extraer_raiz() for _ in range(3)]
    assert top_3 == [(15, "A2"), (12, "A5"), (8, "A4")]
    assert ranking.longitud() == 2           # Quedan los dos menos llenos


def test_ranking_empate_lo_decide_el_segundo_campo():
    """En un montículo de máximos, ante un empate en pasajeros sale primero el id MAYOR."""
    ranking = Monticulo("maximos")
    for anden in [1, 3, 2]:
        ranking.insertar((10, anden))
    assert vaciar(ranking) == [(10, 3), (10, 2), (10, 1)]
