# Librería de generador de números aleatorios
from random import Random

# Estructuras utilizadas (importación absoluta desde la raíz)
from estructuras.pila import Pila
from estructuras.arreglo_dinamico import ArregloDinamico
from estructuras.cola_circular import ColaCircular
from estructuras.arbol_balanceado import ArbolAVL

# Entidades del dominio
from simulador.bus import Bus
from simulador.parada import Parada
from simulador.pasajero import Pasajero, PRIORIDAD_ALTA, PRIORIDAD_NORMAL


#Acciones del operador
ACCION_AGREGAR_BUS = "agregar_bus"
ACCION_PAUSAR = "pausar"
ACCION_REANUDAR = "reanudar"

# Tope para los límites del rango del AVL: infinito es mayor que cualquier
# espera o id, así (TOPE, TOPE) queda después de toda clave (espera, id).
TOPE = float("inf")


class Simulador:
    """
    Director del reloj y de todas las acciones de una simulación.

    No dibuja ni imprime nada: la interfaz lo usa llamando a avanzar_tick(),
    a las acciones del operador y a estado() / reporte(), de modo que toda su
    lógica se puede probar sin ventana.

    Atributos:
        minuto: reloj de la simulación.
        paradas: ArregloDinamico de Parada (el id de cada una es su posición).
        buses: ArregloDinamico de Bus.
        historial: Pila de acciones del operador, para deshacer.
        serie_esperando: ArregloDinamico, un valor por tick: pasajeros esperando en total.
        serie_ocupacion: ArregloDinamico, un valor por tick: ocupación promedio de la flota (0 a 1).
        eventos: ArregloDinamico con lo ocurrido en el último tick (un diccionario por bus),
            para que la interfaz pueda animar el abordaje.
        en_pausa: True si la simulación está detenida.
        capacidad_bus: capacidad de cada bus (también la de los que se agreguen).
        probabilidad_prioritario: probabilidad (0 a 1) de que un pasajero nuevo sea prioritario.
        intentos_llegada: cuántas veces por minuto se sortea, en cada parada, si llega
            un pasajero (cada sorteo con probabilidad tasa_llegada). Con 1 llega como
            máximo un pasajero por parada y minuto; con K, como máximo K.
        segundos_por_tick: cuántos segundos simulados dura un tick. Hoy vale 60
            (1 tick = 1 minuto); cambiará cuando existan los tiempos reales de los tramos.
        esperas: ArbolAVL, índice de los pasajeros que ya abordaron. Clave
            (tiempo_espera en ticks, id_pasajero) -> referencia al Pasajero.
        _aleatorio: generador Random (con semilla, para poder repetir una simulación).
        _proximo_id: id que recibirá el próximo pasajero.
    """
    
    #Constructor
    def __init__(
      self,
      numero_paradas: int,
      numero_buses: int,
      capacidad_bus: int,
      tasa_llegada: float,
      probabilidad_prioritario: float,
      semilla = None,
      intentos_llegada: int = 1,
      segundos_por_tick: int = 60
    ):
        """
        Crea una simulación lista para arrancar en el minuto 0. O(P + B*P),
        con P paradas y B buses (cada bus arma su propia ruta de P paradas).

        intentos_llegada es opcional y va al final para no cambiar las llamadas
        que ya existen; con el valor por defecto (1) la simulación es igual que antes.
        Lo mismo con segundos_por_tick (por defecto 60, es decir, 1 tick = 1 minuto).

        Lanza ValueError si algún parámetro no tiene sentido.
        """
        # Validaciones
        if numero_buses < 1:
            raise ValueError("La simulación requiere de mínimo un bus")
        if numero_paradas < 2:
            raise ValueError("La simulación requiere de mínimo 2 paradas")
        if capacidad_bus < 1:
            raise ValueError("La capacidad del bus debe ser mayor a cero")
        if not(0 <= tasa_llegada <= 1):
            raise ValueError("La tasa de llegada debe ser un valor entre 0 y 1")
        if not(0 <= probabilidad_prioritario <=1):
            raise ValueError("La probabilidad de prioritario debe ser un valor entre 0 y 1")
        if not isinstance(intentos_llegada, int) or intentos_llegada < 1:
            raise ValueError("Los intentos de llegada deben ser un entero mayor o igual a 1")
        if not isinstance(segundos_por_tick, int) or not(segundos_por_tick > 0):
            raise ValueError("Los segundos por tick deben ser un entero mayor que 0")

        #Asignacion de valores iniciales de los atributos
        self.minuto = 0
        self.paradas = ArregloDinamico()
        self.buses = ArregloDinamico()
        self.historial = Pila()
        self.serie_esperando = ArregloDinamico()
        self.serie_ocupacion = ArregloDinamico()
        self.eventos = ArregloDinamico()
        self.en_pausa = False
        self.capacidad_bus = capacidad_bus
        self.probabilidad_prioritario = probabilidad_prioritario
        self.intentos_llegada = intentos_llegada
        self._aleatorio = Random(semilla)
        self._proximo_id = 0
        self.segundos_por_tick = segundos_por_tick
        self.esperas = ArbolAVL()
        
        #Se crean las paradas
        for i in range(numero_paradas):
            self.paradas.agregaralfinal(Parada(i, f"Parada {i+1}",tasa_llegada))
        
        #Se crean los buses repartidos a distancias parejas entre el conjunto de paradas
        for k in range(numero_buses):
            rotaciones = (k * numero_paradas) // numero_buses
            self.buses.agregaralfinal(self._crear_bus(k, rotaciones))
    
    #Motor de la simulación
    def avanzar_tick(self):
        """
        Simula un minuto. Si la simulación está en pausa, no hace nada.

        Orden de cada minuto: llegan pasajeros; en cada bus, primero bajan
        (así se libera cupo), después suben, y luego el bus avanza; por último
        se guardan las estadísticas y corre el reloj.

        Deja en self.eventos lo ocurrido en cada bus durante este minuto
        (en qué parada estaba, cuántos bajaron y cuántos subieron), para que la
        interfaz pueda animarlo.
        """
        # Los eventos son solo del tick actual: se vacían aunque esté en pausa
        self.eventos = ArregloDinamico()

        if self.en_pausa:
            return None

        self._generar_llegadas()

        for i in range(self.buses.tamano()):
            bus = self.buses.posicion(i)
            parada = bus.parada_actual

            bajaron = bus.bajar_en(parada.id)

            # Se toman las medidas justo antes de abordar, para poder animar
            # cómo se llena el bus
            esperando_antes = parada.esperando()
            prioritarios_antes = parada.prioritarios_esperando
            cupos_antes = bus.cupos_libres()

            abordaron = parada.abordar(bus, self.minuto)

            # Índice de esperas (AVL): cada pasajero que acaba de subir entra
            # con su clave (espera, id). Se guarda la referencia al Pasajero,
            # no una copia. O(m log n): m = los que subieron, n = los del árbol.
            for j in range(abordaron.tamano()):
                pasajero = abordaron.posicion(j)
                self.esperas.insertar(self._clave_espera(pasajero), pasajero)

            bus.avanzar()

            self.eventos.agregaralfinal({
                "bus": bus.id,
                "parada": parada.id,
                "bajaron": bajaron,
                "esperando_antes": esperando_antes,
                "prioritarios_antes": prioritarios_antes,
                "cupos_antes": cupos_antes,
                "subieron": abordaron.tamano(),
                "prioritarios_subieron": prioritarios_antes - parada.prioritarios_esperando,
                "esperando_despues": parada.esperando(),
                "a_bordo": bus.cantidad_pasajeros(),
                "siguiente_parada": bus.parada_actual.id,
            })

        self._registrar_estadisticas()
        self.minuto += 1

    # --------------------------
    # Métodos del operador
    # --------------------------
    def agregar_bus(self):
        """
        Agrega un bus a la flota. Arranca en la parada con más gente esperando.
        Devuelve el bus creado. O(P + B).
        """
        bus = self._crear_bus(self.buses.tamano(), self._id_parada_mas_llena())
        self.buses.agregaralfinal(bus)
        self.historial.apilar(ACCION_AGREGAR_BUS)
        return bus

    def pausar(self):
        """Detiene la simulación. Si ya estaba en pausa, no hace nada. O(1)."""
        if not self.en_pausa:
            self.en_pausa = True
            self.historial.apilar(ACCION_PAUSAR)

    def reanudar(self):
        """Reanuda la simulación. Si no estaba en pausa, no hace nada. O(1)."""
        if self.en_pausa:
            self.en_pausa = False
            self.historial.apilar(ACCION_REANUDAR)

    def deshacer(self):
        """
        Deshace la última acción del operador (la que está en el tope de la pila).

        Devuelve un texto para mostrar en pantalla, o None si no hay nada que
        deshacer. Un bus agregado solo se puede quitar si no lleva pasajeros a
        bordo; en ese caso la acción se conserva en la pila. O(1).
        """
        if self.historial.esta_vacio():
            return None

        accion = self.historial.ver_tope()

        if accion == ACCION_AGREGAR_BUS:
            ultimo = self.buses.posicion(self.buses.tamano() - 1)
            if ultimo.cantidad_pasajeros() > 0:
                return "No se puede deshacer: el último bus agregado lleva pasajeros a bordo"
            self.buses.borraralfinal()
            mensaje = "Se quitó el último bus agregado"
        elif accion == ACCION_PAUSAR:
            self.en_pausa = False
            mensaje = "Se reanudó la simulación"
        else:  # ACCION_REANUDAR
            self.en_pausa = True
            mensaje = "Se volvió a pausar la simulación"

        self.historial.desapilar()
        return mensaje
    
    def consultar_esperas(self, minimo: int, limite: int)-> dict:
        """
        ¿Quiénes esperaron `minimo` minutos o más, y dónde? Consulta el índice
        de esperas (AVL) de los pasajeros que ya abordaron.

        Parámetros:
            minimo: umbral en MINUTOS (entero >= 0). Se pasa a ticks por dentro.
            limite: cuántos registros individuales devolver como máximo (entero >= 0);
                evita mandar miles de registros a la web. El resumen sí cuenta a todos.

        Devuelve un diccionario con:
            minimo_minutos: el umbral pedido.
            total: cuántos pasajeros cumplen el umbral.
            resumen: una fila por parada, con cuántos prioritarios y normales
                cumplen el umbral y la peor espera allí (en minutos, o None).
            registros: hasta `limite` pasajeros, las PEORES esperas primero.

        Lanza ValueError si minimo o limite no son enteros >= 0 (True/False no cuentan).

        Complejidad: O(log n + k + P), con n = pasajeros en el árbol,
        k = los que cumplen el umbral (el resumen los recorre a todos) y P = paradas.
        """

        # Validación de datos (bool es un subtipo de int en Python: se excluye aparte)
        if isinstance(minimo, bool) or not isinstance(minimo, int) or minimo < 0:
            raise ValueError("El mínimo debe ser un entero mayor o igual que cero")
        if isinstance(limite, bool) or not isinstance(limite, int) or limite < 0:
            raise ValueError("El límite debe ser un entero mayor o igual que cero")

        # 1) El AVL entrega, en orden ASCENDENTE, todos los (clave, pasajero)
        #    con espera >= el umbral en ticks. O(log n + k).
        desde, hasta = self._limites_espera(self._minutos_a_ticks(minimo))
        candidatos = self.esperas.rango(desde, hasta)

        # 2) Acumuladores del resumen, indexados por id de parada
        #    (el id de cada parada es su posición, así que se llega en O(1)). O(P).
        prioritarios = ArregloDinamico()
        normales = ArregloDinamico()
        peor_espera = ArregloDinamico()
        for _ in range(self.paradas.tamano()):
            prioritarios.agregaralfinal(0)
            normales.agregaralfinal(0)
            peor_espera.agregaralfinal(None)

        # 3) Se recorre de atrás hacia adelante: así salen primero las PEORES
        #    esperas. Los primeros `limite` van a registros; todos van al resumen. O(k).
        registros = ArregloDinamico()
        for i in range(candidatos.tamano() - 1, -1, -1):
            clave, pasajero = candidatos.posicion(i)
            espera_ticks = clave[0]
            origen = pasajero.origen

            if pasajero.es_prioritario():
                prioritarios.cambiarposicion(origen, prioritarios.posicion(origen) + 1)
            else:
                normales.cambiarposicion(origen, normales.posicion(origen) + 1)

            # Como vamos de mayor a menor espera, el primero que aparece en
            # cada parada es su peor espera
            if peor_espera.posicion(origen) is None:
                peor_espera.cambiarposicion(origen, self._ticks_a_minutos(espera_ticks))

            if registros.tamano() < limite:
                registros.agregaralfinal({
                    "id": pasajero.id,
                    "origen": origen,
                    "destino": pasajero.destino,
                    "prioritario": pasajero.es_prioritario(),
                    "espera_minutos": self._ticks_a_minutos(espera_ticks),
                })

        # 4) Se arma el resumen. Las listas y diccionarios de Python solo se
        #    usan aquí, para entregar los datos a la interfaz (como en estado()).
        resumen = []
        for id_parada in range(self.paradas.tamano()):
            p = prioritarios.posicion(id_parada)
            n = normales.posicion(id_parada)
            resumen.append({
                "parada": id_parada,
                "nombre": self.paradas.posicion(id_parada).nombre,
                "prioritarios": p,
                "normales": n,
                "total": p + n,
                "peor_espera_minutos": peor_espera.posicion(id_parada),
            })

        return {
            "minimo_minutos": minimo,
            "total": candidatos.tamano(),
            "resumen": resumen,
            "registros": registros.mostrar(),
        }

    
    # --------------------------
    # Métodos para la interfaz
    # --------------------------
    def estado(self):
        """
        Foto del momento actual para dibujar en pantalla: un diccionario con
        el minuto, si está en pausa, los datos de cada parada (con cuántos de los
        que esperan son prioritarios) y de cada bus, y los eventos del último tick.
        También informa la Pila de operaciones: "historial" (cuántas acciones
        hay, con tamano(), O(1)) y "ultima_accion" (la del tope, con
        ver_tope(), O(1); None si la Pila está vacía), sin sacar nada de ella.
        Usa listas y diccionarios de Python solo para entregar datos a la
        interfaz; el estado real vive en nuestras estructuras. O(P + B).
        """
        paradas = []
        for i in range(self.paradas.tamano()):
            parada = self.paradas.posicion(i)
            paradas.append({
                "id": parada.id,
                "nombre": parada.nombre,
                "esperando": parada.esperando(),
                "prioritarios": parada.prioritarios_esperando,
            })

        buses = []
        for i in range(self.buses.tamano()):
            bus = self.buses.posicion(i)
            buses.append({
                "id": bus.id,
                "parada": bus.parada_actual.id,
                "pasajeros": bus.cantidad_pasajeros(),
                "capacidad": bus.capacidad_maxima,
                "ocupacion": bus.ocupacion(),
            })

        return {
            "minuto": self.minuto,
            "en_pausa": self.en_pausa,
            "paradas": paradas,
            "buses": buses,
            "eventos": self.eventos.mostrar(),
            "historial": self.historial.tamano(),
            "ultima_accion": self.historial.ver_tope(),
        }

    def reporte(self):
        """
        Resumen de lo ocurrido hasta ahora. Si nadie ha abordado o no ha pasado
        ningún minuto, los promedios valen 0.0 (así no se divide entre cero). O(P + T),
        con T los ticks simulados.

        Devuelve un diccionario con: minuto, pasajeros_generados,
        pasajeros_abordados, pasajeros_esperando, espera_promedio (en minutos),
        ocupacion_promedio (0 a 1, promedio de todos los ticks) y buses.
        """
        generados = 0
        abordados = 0
        suma_espera = 0
        for i in range(self.paradas.tamano()):
            parada = self.paradas.posicion(i)
            generados += parada.total_llegados
            abordados += parada.total_abordados
            suma_espera += parada.suma_espera

        if abordados > 0:
            espera_promedio = suma_espera / abordados
        else:
            espera_promedio = 0.0

        if self.serie_ocupacion.tamano() > 0:
            suma = 0
            for i in range(self.serie_ocupacion.tamano()):
                suma += self.serie_ocupacion.posicion(i)
            ocupacion_promedio = suma / self.serie_ocupacion.tamano()
        else:
            ocupacion_promedio = 0.0

        return {
            "minuto": self.minuto,
            "pasajeros_generados": generados,
            "pasajeros_abordados": abordados,
            "pasajeros_esperando": self._total_esperando(),
            "espera_promedio": espera_promedio,
            "ocupacion_promedio": ocupacion_promedio,
            "buses": self.buses.tamano(),
        }

    # --------------------------
    # Métodos privados (de uso interno)
    # --------------------------
    def _crear_bus(self, id: int, rotaciones: int) -> Bus:
        """
        Crea un bus con SU PROPIA ruta (una ColaCircular nueva con todas las
        paradas en orden), rotada para que arranque en la parada indicada.
        La rotación se hace antes de crear el bus porque este toma su parada
        inicial del frente de la ruta. O(P).
        """
        
        ruta_bus = ColaCircular()
        for i in range(self.paradas.tamano()):
            ruta_bus.encolar(self.paradas.posicion(i))
        
        for _ in range(rotaciones):
            ruta_bus.siguiente()
        
        return Bus(id, ruta_bus, self.capacidad_bus)
    
    def _generar_llegadas(self)-> None:
        """
        En cada parada se hacen intentos_llegada sorteos; en cada uno, con
        probabilidad tasa_llegada, llega un pasajero nuevo con destino distinto
        del origen. Así llegan entre 0 y K pasajeros por parada (K = intentos_llegada).
        O(P * K).

        Con K = 1 los llamados al generador aleatorio son exactamente los mismos
        y en el mismo orden que antes, así una simulación con semilla no cambia.
        """
        for i in range(self.paradas.tamano()):
            parada = self.paradas.posicion(i)
            for _ in range(self.intentos_llegada):
                if self._aleatorio.random() < parada.tasa_llegada:
                    # Destino al azar entre las OTRAS paradas, todas igual de probables:
                    # se elige entre 0 y n-2 y se salta el lugar del origen
                    destino = self._aleatorio.randrange(self.paradas.tamano() - 1)
                    if destino >= parada.id:
                        destino += 1

                    if self._aleatorio.random() < self.probabilidad_prioritario:
                        prioridad = PRIORIDAD_ALTA
                    else:
                        prioridad = PRIORIDAD_NORMAL

                    pasajero = Pasajero(self._proximo_id, parada.id, destino, prioridad, self.minuto)

                    self._proximo_id += 1
                    parada.recibir(pasajero)
    
    def _total_esperando(self):
        """Pasajeros esperando en todas las paradas. O(P)."""
        total = 0
        for i in range(self.paradas.tamano()):
            total += self.paradas.posicion(i).esperando()
        return total
    
    def _ocupacion_actual(self)-> float:
        """Ocupación promedio de la flota en este momento (0 a 1). O(B)."""
        suma = 0
        for i in range(self.buses.tamano()):
            suma += self.buses.posicion(i).ocupacion()
        return suma / self.buses.tamano()
    
    def _registrar_estadisticas(self) -> None:
        """Guarda una muestra por tick para las gráficas. O(P + B)."""
        self.serie_esperando.agregaralfinal(self._total_esperando())
        self.serie_ocupacion.agregaralfinal(self._ocupacion_actual())
    
    def _id_parada_mas_llena(self) -> int:
        """Devuelve el id de la parada con más pasajeros esperando (la primera si hay empate). O(P)."""
        id_mas_llena = 0
        for i in range(1, self.paradas.tamano()):
            if self.paradas.posicion(i).esperando() > self.paradas.posicion(id_mas_llena).esperando():
                id_mas_llena = i

        return id_mas_llena
    
    def _clave_espera(self, pasajero: Pasajero)-> tuple:
        """
        Arma la clave del pasajero en el índice de esperas (AVL): (espera, id). O(1).

        La espera sola se repite mucho (muchos esperan 2 o 3 ticks) y el AVL
        reemplaza el valor cuando una clave se repite; el id, que es único,
        desempata y evita perder pasajeros. Python compara las tuplas posición
        por posición: primero la espera y, si empatan, el id.
        Solo tiene sentido para pasajeros que ya abordaron (si no, la espera es None).
        """
        return (pasajero.tiempo_espera(), pasajero.id)
    
    def _minutos_a_ticks(self, minutos: int)->int:
        """
        Cuántos ticks hay que esperar, como mínimo, para completar `minutos`. O(1).

        Es el techo de minutos*60 / segundos_por_tick, calculado solo con
        enteros (sumar divisor - 1 antes de dividir redondea hacia arriba).
        Ejemplo: con 45 s por tick, 1 minuto = 60 s pide 2 ticks (90 s),
        porque 1 tick (45 s) se queda corto. La equivalencia es exacta.
        """
        return (minutos*60 + self.segundos_por_tick - 1) // self.segundos_por_tick

    def _ticks_a_minutos(self, ticks: int)-> float:
        """Pasa ticks a minutos para mostrar al usuario (puede tener decimales). O(1)."""
        return ticks * self.segundos_por_tick / 60

    def _limites_espera(self, minimo_ticks: int)-> tuple:
        """
        Límites del rango del AVL para "esperó minimo_ticks o más". O(1).

        Desde (minimo_ticks, -inf): queda antes que cualquier (minimo_ticks, id).
        Hasta (inf, inf): queda después de cualquier clave (espera, id).
        Python compara int con float sin problema y las tuplas posición por posición.
        """
        return ((minimo_ticks, -TOPE), (TOPE, TOPE))

