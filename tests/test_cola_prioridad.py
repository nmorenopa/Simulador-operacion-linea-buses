"""
Pruebas de ColaPrioridad (arreglo de colas).

Convención: MENOR número = MAYOR prioridad. El nivel 0 sale primero.
Dentro de un mismo nivel se respeta el orden de llegada (FIFO).

Para correrlas, desde la carpeta raíz del proyecto:  pytest tests/test_cola_prioridad.py
"""
import pytest
from random import Random

from estructuras.cola import Cola
from estructuras.cola_prioridad import ColaPrioridad


# ---------------------------------------------------------------
# Ayuda: vacía la cola y devuelve los datos en el orden en que salen
# ---------------------------------------------------------------
def vaciar(cola):
    """Desencola todo y devuelve una lista con los datos, en orden de salida."""
    salida = []
    while not cola.esta_vacia():
        salida.append(cola.desencolar())
    return salida


# ---------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------
def test_cola_nueva_esta_vacia():
    cola = ColaPrioridad(2)
    assert cola.esta_vacia()
    assert cola.tamano() == 0
    assert cola.frente() is None
    assert cola.desencolar() is None


@pytest.mark.parametrize("niveles", [0, -1, -5])
def test_constructor_con_menos_de_un_nivel_lanza_error(niveles):
    with pytest.raises(ValueError):
        ColaPrioridad(niveles)


def test_constructor_crea_un_nivel_por_cada_prioridad():
    cola = ColaPrioridad(4)
    assert cola.cantidad_niveles == 4
    assert cola.niveles.longitud() == 4
    for k in range(4):
        # Cada nivel es una Cola vacía e independiente de las demás
        assert isinstance(cola.niveles.posicion(k), Cola)
        assert cola.niveles.posicion(k).esta_vacia()
    assert cola.niveles.posicion(0) is not cola.niveles.posicion(1)


def test_con_un_solo_nivel_funciona_como_cola_normal():
    cola = ColaPrioridad(1)
    for dato in ["A", "B", "C"]:
        cola.encolar(dato, 0)
    assert vaciar(cola) == ["A", "B", "C"]


# ---------------------------------------------------------------
# Orden de salida
# ---------------------------------------------------------------
def test_sale_por_prioridad_aunque_llegue_despues():
    cola = ColaPrioridad(2)
    cola.encolar("normal", 1)          # Llega primero, pero nivel 1 = menos prioridad
    cola.encolar("prioritario", 0)     # Llega después, pero nivel 0 = más prioridad
    assert cola.desencolar() == "prioritario"
    assert cola.desencolar() == "normal"


def test_misma_prioridad_respeta_orden_de_llegada():
    cola = ColaPrioridad(2)
    for nombre in ["N1", "N2", "N3"]:
        cola.encolar(nombre, 1)
    assert vaciar(cola) == ["N1", "N2", "N3"]


def test_mezcla_prioridades():
    cola = ColaPrioridad(2)
    cola.encolar("P1", 0)
    cola.encolar("N1", 1)
    cola.encolar("N2", 1)
    cola.encolar("P2", 0)
    assert vaciar(cola) == ["P1", "P2", "N1", "N2"]


def test_varios_niveles():
    cola = ColaPrioridad(4)
    for nombre, prio in [("c", 1), ("a", 3), ("d", 0), ("b", 2)]:
        cola.encolar(nombre, prio)
    assert vaciar(cola) == ["d", "c", "b", "a"]      # Del nivel 0 al nivel 3


def test_desencolar_salta_los_niveles_vacios():
    cola = ColaPrioridad(4)
    cola.encolar("solo", 3)            # Los niveles 0, 1 y 2 están vacíos
    assert cola.desencolar() == "solo"
    assert cola.esta_vacia()


def test_intercalar_encolar_y_desencolar_mantiene_el_orden():
    cola = ColaPrioridad(2)
    cola.encolar("N1", 1)
    assert cola.desencolar() == "N1"
    cola.encolar("N2", 1)
    cola.encolar("P1", 0)
    cola.encolar("N3", 1)
    assert cola.desencolar() == "P1"   # El prioritario se adelanta a los normales
    cola.encolar("P2", 0)
    assert vaciar(cola) == ["P2", "N2", "N3"]


# ---------------------------------------------------------------
# frente()
# ---------------------------------------------------------------
def test_frente_no_saca_el_dato():
    cola = ColaPrioridad(2)
    cola.encolar("A", 1)
    assert cola.frente() == "A"
    assert cola.frente() == "A"
    assert cola.tamano() == 1


def test_frente_encuentra_el_dato_aunque_el_nivel_0_este_vacio():
    cola = ColaPrioridad(2)
    cola.encolar("normal", 1)          # Nivel 0 vacío
    assert cola.frente() == "normal"


def test_frente_cambia_cuando_llega_alguien_con_mas_prioridad():
    cola = ColaPrioridad(3)
    cola.encolar("B", 2)
    assert cola.frente() == "B"
    cola.encolar("A", 0)
    assert cola.frente() == "A"
    cola.encolar("C", 1)
    assert cola.frente() == "A"        # A sigue siendo el de mayor prioridad


def test_frente_coincide_con_lo_que_sale_en_desencolar():
    cola = ColaPrioridad(3)
    for dato, prio in [("x", 2), ("y", 1), ("z", 2), ("w", 1)]:
        cola.encolar(dato, prio)
    while not cola.esta_vacia():
        esperado = cola.frente()
        assert cola.desencolar() == esperado


# ---------------------------------------------------------------
# tamano() y esta_vacia()
# ---------------------------------------------------------------
def test_tamano_sube_al_encolar_y_baja_al_desencolar():
    cola = ColaPrioridad(3)
    cola.encolar("A", 2)
    cola.encolar("B", 0)
    cola.encolar("C", 2)
    assert cola.tamano() == 3
    assert not cola.esta_vacia()

    cola.desencolar()
    assert cola.tamano() == 2
    cola.desencolar()
    assert cola.tamano() == 1
    cola.desencolar()
    assert cola.tamano() == 0
    assert cola.esta_vacia()


def test_desencolar_en_cola_vacia_no_deja_el_tamano_negativo():
    cola = ColaPrioridad(2)
    assert cola.desencolar() is None
    assert cola.desencolar() is None
    assert cola.tamano() == 0


def test_tamano_coincide_con_la_suma_de_los_niveles():
    cola = ColaPrioridad(3)
    for dato, prio in [("a", 0), ("b", 1), ("c", 1), ("d", 2), ("e", 2), ("f", 2)]:
        cola.encolar(dato, prio)
    cola.desencolar()
    cola.desencolar()
    suma = 0
    for k in range(cola.cantidad_niveles):
        suma += cola.niveles.posicion(k).longitud()
    assert cola.tamano() == suma == 4


def test_vaciar_y_reutilizar():
    cola = ColaPrioridad(2)
    cola.encolar("A", 1)
    cola.desencolar()
    assert cola.esta_vacia()
    cola.encolar("B", 0)
    assert cola.frente() == "B"
    assert cola.tamano() == 1


# ---------------------------------------------------------------
# Validación de la prioridad
# ---------------------------------------------------------------
@pytest.mark.parametrize("prioridad", [-1, 2, 3, 100])
def test_prioridad_fuera_de_rango_lanza_error(prioridad):
    cola = ColaPrioridad(2)            # Prioridades válidas: 0 y 1
    with pytest.raises(ValueError):
        cola.encolar("X", prioridad)


def test_un_encolar_fallido_no_deja_rastro():
    cola = ColaPrioridad(2)
    with pytest.raises(ValueError):
        cola.encolar("X", 2)
    assert cola.esta_vacia()           # El contador no subió
    assert cola.tamano() == 0
    assert cola.frente() is None


def test_los_limites_del_rango_son_validos():
    cola = ColaPrioridad(5)
    cola.encolar("primero", 0)         # El nivel más bajo
    cola.encolar("ultimo", 4)          # El nivel más alto (k - 1)
    assert vaciar(cola) == ["primero", "ultimo"]


# ---------------------------------------------------------------
# Comparación contra una referencia (usa sorted de Python SOLO para validar)
# ---------------------------------------------------------------
@pytest.mark.parametrize("semilla", [1, 2, 3, 4, 5])
def test_contra_referencia_ordenada_con_datos_al_azar(semilla):
    """
    sorted() es estable: ordena por prioridad y deja en su orden de llegada
    a los que empatan. Es justo lo que debe hacer nuestra cola.
    """
    azar = Random(semilla)
    cola = ColaPrioridad(3)
    llegadas = []                      # (numero_de_llegada, prioridad)
    for numero in range(200):
        prioridad = azar.randrange(3)
        llegadas.append((numero, prioridad))
        cola.encolar(numero, prioridad)

    esperado = [numero for numero, prioridad in sorted(llegadas, key=lambda par: par[1])]
    assert vaciar(cola) == esperado