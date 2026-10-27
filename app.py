"""
Interfaz gráfica del simulador de buses (Tkinter).

FASE 3: dibuja el fondo, los buses del Simulador (con su contador "c/n") y
los pasajeros que esperan en cada parada (azul = prioritario, gris = normal).
Con Play la simulación corre sola: en cada tick los buses se ANIMAN desde su
parada hasta la siguiente, siguiendo la vía. Una barra de controles debajo
del Canvas permite pausar, agregar buses, deshacer, terminar y reiniciar con
otros valores. Filas, contadores y reloj se actualizan cuando termina cada animación.
Al pulsar "Terminar" se abre una ventana aparte con las estadísticas en gráficas.

La animación es solo visual: avanzar_tick() cambia el estado de golpe y la
interfaz dibuja el recorrido entre el estado de antes y el de después.

Separación: la interfaz NO contiene lógica de la simulación. Solo crea el
Simulador, lee estado(), reporte() y las series de estadísticas, y llama
avanzar_tick(), pausar(), reanudar(), agregar_bus() y deshacer().
"""
import tkinter as tk
from pathlib import Path

from PIL import Image, ImageTk

from estructuras.cola import Cola
from simulador.simulador import Simulador


# ---------------------------------------------------------------
# Rutas de archivos
# ---------------------------------------------------------------
# Path(__file__) es la ubicación de este archivo (app.py). Si armamos las
# rutas a partir de ahí, el programa encuentra las imágenes sin importar
# desde qué carpeta se ejecute.
CARPETA_PROYECTO = Path(__file__).resolve().parent
CARPETA_IMAGENES = CARPETA_PROYECTO / "imagenes"
RUTA_FONDO = CARPETA_IMAGENES / "FONDO.png"

# Sprites del bus: uno por dirección, de 60x60 px. Este es el ÚNICO lugar
# donde aparecen sus nombres; para cambiar un sprite basta cambiarlo aquí.
CARPETA_BUS = CARPETA_IMAGENES / "bus"
ARCHIVOS_SPRITES = {
    "norte": "norte.png",   # Hacia arriba
    "sur": "sur.png",       # Hacia abajo
    "este": "este.png",     # Hacia la derecha
    "oeste": "oeste.png",   # Hacia la izquierda
}


# ---------------------------------------------------------------
# Parámetros de la simulación
# ---------------------------------------------------------------
# Valores elegidos para la demo: con tasa 0.5 y capacidad 10 la simulación es
# ESTABLE (los buses van casi llenos, ~90 % de ocupación, y se forman filas
# moderadas que no crecen sin control). Para saturarla y ver filas largas:
# bajar CAPACIDAD_BUS a 8 o subir TASA_LLEGADA a 0.6.
NUMERO_BUSES = 5
CAPACIDAD_BUS = 10
TASA_LLEGADA = 0.5              # Probabilidad de que llegue un pasajero por parada y minuto
PROBABILIDAD_PRIORITARIO = 0.2
INTENTOS_LLEGADA = 3            # Sorteos por parada y minuto: llegan de 0 a 3 pasajeros
SEMILLA = 42                   # Con la misma semilla, la simulación se repite igual


# ---------------------------------------------------------------
# Constantes de la interfaz
# ---------------------------------------------------------------
# Si es True se dibujan las marcas de depuración (celdas y esquinas).
MOSTRAR_DEPURACION = True

# Si es True se dibujan las placas blancas P1..P8 junto a cada parada.
# Están apagadas porque el fondo actual ya trae un letrero junto a cada parada;
# el código se conserva por si se vuelve a un fondo sin letreros.
MOSTRAR_PLACAS = False

# El fondo (900x600) se divide en una grid de celdas de 60x60 px:
# 15 columnas (0 a 14) y 10 filas (0 a 9). La vía mide justo una celda de ancho.
TAM_CELDA = 60
COLUMNAS = 15
FILAS = 10
ANCHO = COLUMNAS * TAM_CELDA   # 900
ALTO = FILAS * TAM_CELDA       # 600


def centro_celda(columna, fila):
    """Devuelve el píxel (x, y) del centro de una celda de la grid."""
    x = columna * TAM_CELDA + TAM_CELDA // 2
    y = fila * TAM_CELDA + TAM_CELDA // 2
    return x, y


# ---------------------------------------------------------------
# La ruta: las 32 celdas del circuito en sentido horario
# ---------------------------------------------------------------
# Medido sobre FONDO.png, la vía del circuito ocupa:
#   - lado de arriba:    fila 2,    columnas 2 a 12
#   - lado derecho:      columna 12, filas 2 a 8
#   - lado de abajo:     fila 8,    columnas 2 a 12
#   - lado izquierdo:    columna 2,  filas 2 a 8
# La ruta es la lista de esas celdas (columna, fila) en el orden en que el
# bus las recorre. La posición 0 es la esquina de arriba a la izquierda.
def construir_ruta():
    """Arma la lista de celdas del circuito, en sentido horario."""
    ruta = []
    for columna in range(2, 13):        # Arriba, de izquierda a derecha: 11 celdas
        ruta.append((columna, 2))
    for fila in range(3, 9):            # Derecha, de arriba hacia abajo: 6 celdas
        ruta.append((12, fila))
    for columna in range(11, 1, -1):    # Abajo, de derecha a izquierda: 10 celdas
        ruta.append((columna, 8))
    for fila in range(7, 2, -1):        # Izquierda, de abajo hacia arriba: 5 celdas
        ruta.append((2, fila))
    return ruta


RUTA = construir_ruta()   # 11 + 6 + 10 + 5 = 32 celdas

NUMERO_PARADAS = 8

# Cada parada es el ÍNDICE de su celda dentro de RUTA, en el orden de la ruta.
# La posición i de esta lista es la parada con id i del Simulador.
#
# ESPACIADO IGUAL: las 32 celdas del circuito se reparten entre 8 paradas,
# una cada 4 celdas (32 / 8 = 4). Así el bus recorre siempre la misma
# distancia entre una parada y la siguiente.
#
# Las paradas se ubican solo con la grid
#
#Si se cambia el fondo, basta con cambiar esta lista (y NUMERO_PARADAS si 
#cambia la cantidad).
PARADAS = [
    1,    # P1: celda (3, 2),  arriba
    5,    # P2: celda (7, 2),  arriba
    9,    # P3: celda (11, 2), arriba
    13,   # P4: celda (12, 5), derecha
    17,   # P5: celda (11, 8), abajo
    21,   # P6: celda (7, 8),  abajo
    25,   # P7: celda (3, 8),  abajo
    29,   # P8: celda (2, 5),  izquierda
]

# Esquinas del circuito (solo para depuración), en sentido horario.
ESQUINAS = [
    (12, 2),   # E1: arriba a la derecha   -> píxel (750, 150)
    (12, 8),   # E2: abajo a la derecha    -> píxel (750, 510)
    (2, 8),    # E3: abajo a la izquierda  -> píxel (150, 510)
    (2, 2),    # E4: arriba a la izquierda -> píxel (150, 150)
]

# Distancia (en píxeles, a lo largo de la ruta) entre dos buses que están
# en la misma parada: con 2 buses quedan a -30 y +30 px de la parada.
SEPARACION_BUSES = 60

# Animación: cuánto dura el recorrido de un tick y cada cuánto se dibuja un
# cuadro. 600 / 16 ≈ 38 cuadros (unos 60 cuadros por segundo).
DURACION_ANIMACION_MS = 600
PASO_ANIMACION_MS = 16

# Bucle automático: espera entre el fin de un tick y el siguiente, y cada
# cuánto se revisa si se quitó la pausa.
PAUSA_ENTRE_TICKS_MS = 200
REVISION_EN_PAUSA_MS = 100

# Tope de buses que deja agregar la interfaz (el Simulador no tiene tope).
MAX_BUSES = 10

# Cómo mostrar en pantalla cada acción de la Pila del Simulador.
NOMBRES_ACCIONES = {
    "agregar_bus": "agregar bus",
    "pausar": "pausar",
    "reanudar": "reanudar",
}

# Pasajeros que esperan: un punto por pasajero, en una fila sobre la acera.
MAX_PUNTOS_POR_PARADA = 12      # Si hay más, se muestra "+N" con los que no caben
DIAMETRO_PASAJERO = 10          # px
PASO_PASAJEROS = 13             # px entre centros de dos puntos seguidos (deja 3 px libres)
DISTANCIA_ACERA = 60            # px desde el centro de la vía hasta la línea de puntos
COLOR_PRIORITARIO = "#286EFF"   # Azul
COLOR_NORMAL = "#B9B9B9"        # Gris claro: con borde negro se distingue de la acera
COLOR_BORDE_PASAJERO = "black"


def direccion_entre(celda_actual, celda_siguiente):
    """
    Devuelve "norte", "sur", "este" u "oeste" según hacia dónde hay que
    moverse para ir de una celda a la vecina. Recuerda que en la pantalla
    la fila crece hacia ABAJO, así que fila + 1 es "sur".
    """
    columna1, fila1 = celda_actual
    columna2, fila2 = celda_siguiente
    if columna2 > columna1:
        return "este"
    if columna2 < columna1:
        return "oeste"
    if fila2 > fila1:
        return "sur"
    return "norte"


def punto_en_ruta(distancia):
    """
    Convierte una distancia recorrida a lo largo de la ruta (en píxeles,
    contando desde el centro de la celda 0) en un punto (x, y) de la
    pantalla y la dirección del tramo donde cae ese punto.

    Como la ruta es circular, la distancia se toma módulo el largo total
    (32 celdas * 60 px). Así una distancia negativa o mayor que el largo
    también funciona, y los desplazamientos doblan bien en las esquinas.
    """
    largo_total = len(RUTA) * TAM_CELDA
    distancia = distancia % largo_total

    # En qué celda empieza el tramo y qué fracción del tramo se ha recorrido
    indice = int(distancia // TAM_CELDA)
    fraccion = (distancia % TAM_CELDA) / TAM_CELDA

    celda_actual = RUTA[indice]
    celda_siguiente = RUTA[(indice + 1) % len(RUTA)]   # Después de la 31 viene la 0

    # Interpolación lineal entre los centros de las dos celdas
    x1, y1 = centro_celda(*celda_actual)
    x2, y2 = centro_celda(*celda_siguiente)
    x = x1 + (x2 - x1) * fraccion
    y = y1 + (y2 - y1) * fraccion

    return x, y, direccion_entre(celda_actual, celda_siguiente)


# ---------------------------------------------------------------
# Referencias a las imágenes
# ---------------------------------------------------------------
# Tkinter NO guarda las imágenes que se le pasan al Canvas: si en Python
# nadie más apunta a un PhotoImage, el recolector de basura lo borra y la
# imagen desaparece de la pantalla. Por eso las guardamos todas aquí.
imagenes_guardadas = []


def cargar_fondo():
    """Abre FONDO.png y lo convierte en un PhotoImage que Tkinter puede dibujar."""
    imagen = Image.open(RUTA_FONDO)
    foto = ImageTk.PhotoImage(imagen)
    imagenes_guardadas.append(foto)   # Guardar la referencia (ver arriba)
    return foto


# Diccionario dirección -> PhotoImage del bus. Se llena una sola vez en
# cargar_sprites() y, como es una variable del módulo, también guarda las
# referencias para que las imágenes no desaparezcan.
sprites_bus = {}


def cargar_sprites():
    """
    Carga los 4 sprites del bus (una sola vez, al iniciar). Se dibujan a
    60 px, sin escalar: un bus ocupa exactamente una celda.
    Tiene que llamarse después de crear la ventana (tk.Tk), porque Tkinter
    no puede crear un PhotoImage sin ventana.
    """
    for direccion, archivo in ARCHIVOS_SPRITES.items():
        imagen = Image.open(CARPETA_BUS / archivo)
        sprites_bus[direccion] = ImageTk.PhotoImage(imagen)


def dibujar_etiqueta(canvas, x, y, texto, color, tags=()):
    """
    Escribe un texto con un recuadro de color detrás, para que se lea bien
    sobre el fondo. Primero se crea el texto, luego se mide con bbox() y
    se dibuja el recuadro debajo con tag_lower().
    tags: etiquetas del Canvas para el texto y el recuadro (para poder borrarlos).
    """
    id_texto = canvas.create_text(x, y, text=texto, fill="white",
                                  font=("Arial", 9, "bold"), tags=tags)
    x1, y1, x2, y2 = canvas.bbox(id_texto)
    id_recuadro = canvas.create_rectangle(x1 - 2, y1 - 1, x2 + 2, y2 + 1,
                                          fill=color, outline="", tags=tags)
    canvas.tag_lower(id_recuadro, id_texto)


def hacia_la_acera(columna, fila):
    """
    Devuelve la dirección (dx, dy) que apunta desde una celda de la vía hacia
    la acera de afuera del circuito. Por ejemplo, en el lado de arriba la
    acera está arriba: (0, -1). (Las paradas nunca están en una esquina.)
    """
    if fila == 2:
        return 0, -1    # Lado de arriba: la acera está arriba
    if fila == 8:
        return 0, 1     # Lado de abajo: la acera está abajo
    if columna == 12:
        return 1, 0     # Lado derecho: la acera está a la derecha
    return -1, 0        # Lado izquierdo: la acera está a la izquierda


def dibujar_paradas(canvas):
    """
    Dibuja la placa de cada parada (solo si MOSTRAR_PLACAS es True):
      - una línea blanca en el borde exterior de su celda (el "andén"),
        para indicar dónde se detiene el bus;
      - un rectángulo blanco con su nombre (P1..P8) sobre la acera,
        justo afuera de ese borde.
    """
    mitad = TAM_CELDA // 2
    largo_linea = 20         # Mitad del largo de la línea del andén

    for numero, indice in enumerate(PARADAS):
        columna, fila = RUTA[indice]
        x, y = centro_celda(columna, fila)
        dx, dy = hacia_la_acera(columna, fila)

        # Punto en el borde exterior de la celda (entre la vía y la acera)
        borde_x = x + dx * mitad
        borde_y = y + dy * mitad

        # Línea del andén: va a lo largo del borde, es decir, perpendicular
        # a la dirección hacia la acera. Si (dx, dy) es (0, -1), la línea es
        # horizontal; si es (-1, 0), es vertical.
        canvas.create_line(borde_x - dy * largo_linea, borde_y - dx * largo_linea,
                           borde_x + dy * largo_linea, borde_y + dx * largo_linea,
                           fill="white", width=3)

        # Rectángulo con el nombre, 28 px hacia la acera desde el borde
        # (a esa distancia no tapa el letrero del fondo que está junto a P8)
        id_texto = canvas.create_text(borde_x + dx * 28, borde_y + dy * 28,
                                      text=f"P{numero + 1}", fill="black",
                                      font=("Arial", 9, "bold"))
        x1, y1, x2, y2 = canvas.bbox(id_texto)
        id_recuadro = canvas.create_rectangle(x1 - 3, y1 - 1, x2 + 3, y2 + 1,
                                              fill="white", outline="black")
        canvas.tag_lower(id_recuadro, id_texto)


def dibujar_depuracion(canvas):
    """
    Dibuja encima del fondo:
      - el borde de cada una de las 32 celdas de la ruta, con su índice;
      - la celda de cada parada resaltada en rojo;
      - las esquinas del circuito (E1..E4).
    Solo sirve para verificar las coordenadas.
    """
    # Celdas de la ruta: borde verde y su índice en la esquina superior izquierda
    for indice, (columna, fila) in enumerate(RUTA):
        x1 = columna * TAM_CELDA
        y1 = fila * TAM_CELDA
        canvas.create_rectangle(x1, y1, x1 + TAM_CELDA, y1 + TAM_CELDA,
                                outline="lime")
        canvas.create_text(x1 + 4, y1 + 3, text=str(indice), anchor="nw",
                           fill="lime", font=("Arial", 8))

    # Paradas: borde rojo grueso sobre su celda (el nombre lo pone dibujar_paradas)
    for indice in PARADAS:
        columna, fila = RUTA[indice]
        x1 = columna * TAM_CELDA
        y1 = fila * TAM_CELDA
        canvas.create_rectangle(x1 + 2, y1 + 2, x1 + TAM_CELDA - 2, y1 + TAM_CELDA - 2,
                                outline="red", width=3)

    # Esquinas: cuadrito azul en el centro de la celda y el nombre un poco más abajo
    radio = 4
    for numero, (columna, fila) in enumerate(ESQUINAS):
        x, y = centro_celda(columna, fila)
        canvas.create_rectangle(x - radio, y - radio, x + radio, y + radio,
                                fill="blue", outline="white")
        dibujar_etiqueta(canvas, x, y + 14, f"E{numero + 1}", "blue")


# ---------------------------------------------------------------
# Pasajeros que esperan en las paradas
# ---------------------------------------------------------------
# REGLA DE UBICACIÓN de la fila de puntos de cada parada:
#   1. Lado: la fila va sobre la ACERA de afuera del circuito, del mismo lado
#      que el letrero (hacia_la_acera), a DISTANCIA_ACERA = 60 px del centro de
#      la vía, o sea, por la mitad de la acera.
#   2. Inicio: el primer punto queda a la altura del centro de la celda de la
#      parada, justo al lado del letrero.
#   3. Hacia dónde crece: se ALEJA del letrero. En el fondo, los letreros de
#      arriba y de abajo están a la derecha de su parada, así que la fila
#      crece hacia la IZQUIERDA; los de los lados izquierdo y derecho están
#      en la parte de arriba, así que la fila crece hacia ABAJO.
#   4. Orden: primero los azules (prioritarios, los más cerca del letrero) y
#      después los grises (normales). Como máximo MAX_PUNTOS_POR_PARADA.
#   5. "+N": va del otro lado del letrero, donde empieza la fila: a la derecha
#      del letrero en los lados de arriba y abajo, y encima del letrero en los
#      lados izquierdo y derecho.
# La acera mide unos 60 px de fondo, por eso la fila va A LO LARGO de la
# acera: 12 puntos ocupan 12 * 13 = 156 px y no cabrían alejándose de la vía.

def hacia_donde_crece_la_fila(columna, fila):
    """
    Devuelve la dirección (dx, dy) en la que crece la fila de pasajeros:
    hacia la izquierda (-1, 0) en los lados de arriba y abajo, y hacia
    abajo (0, 1) en los lados izquierdo y derecho (ver la regla arriba).
    """
    dx, dy = hacia_la_acera(columna, fila)
    if dy != 0:
        return -1, 0    # Acera arriba o abajo: la fila es horizontal y va a la izquierda
    return 0, 1         # Acera a la izquierda o derecha: la fila es vertical y va hacia abajo


def puntos_de_parada(parada):
    """
    Recibe una parada de Simulador.estado()["paradas"] y calcula qué dibujar:
    devuelve (puntos, sobrantes, posicion_texto).
      - puntos: lista de (x, y, es_prioritario), primero los azules.
      - sobrantes: cuántos esperan pero no caben (el N de "+N"); sale del
        dato "esperando", no de contar puntos.
      - posicion_texto: (x, y) del centro del texto "+N".
    No dibuja nada, así se puede probar sin ventana.
    """
    visibles = min(parada["esperando"], MAX_PUNTOS_POR_PARADA)
    azules = min(parada["prioritarios"], visibles)
    sobrantes = parada["esperando"] - visibles

    columna, fila = RUTA[PARADAS[parada["id"]]]
    x_parada, y_parada = centro_celda(columna, fila)
    acera_x, acera_y = hacia_la_acera(columna, fila)
    crece_x, crece_y = hacia_donde_crece_la_fila(columna, fila)

    # Punto de partida: frente a la parada, a mitad de la acera
    inicio_x = x_parada + acera_x * DISTANCIA_ACERA
    inicio_y = y_parada + acera_y * DISTANCIA_ACERA

    puntos = []
    for k in range(visibles):
        x = inicio_x + crece_x * PASO_PASAJEROS * k
        y = inicio_y + crece_y * PASO_PASAJEROS * k
        puntos.append((x, y, k < azules))   # Los primeros "azules" son prioritarios

    # "+N" del otro lado del letrero: si la fila crece a la izquierda, el
    # texto va a la derecha (48 px); si crece hacia abajo, va encima (32 px).
    if crece_x != 0:
        posicion_texto = (inicio_x + 48, inicio_y)
    else:
        posicion_texto = (inicio_x, inicio_y - 32)

    return puntos, sobrantes, posicion_texto


def dibujar_pasajeros(canvas, paradas):
    """
    Borra los puntos anteriores y dibuja los de cada parada (y su "+N").
    Todo lleva la etiqueta "pasajero", así canvas.delete("pasajero") los
    quita todos antes de redibujar y no se acumulan.
    """
    canvas.delete("pasajero")
    radio = DIAMETRO_PASAJERO / 2
    for parada in paradas:
        puntos, sobrantes, (texto_x, texto_y) = puntos_de_parada(parada)
        for x, y, es_prioritario in puntos:
            color = COLOR_PRIORITARIO if es_prioritario else COLOR_NORMAL
            canvas.create_oval(x - radio, y - radio, x + radio, y + radio,
                               fill=color, outline=COLOR_BORDE_PASAJERO,
                               tags="pasajero")
        if sobrantes > 0:
            dibujar_etiqueta(canvas, texto_x, texto_y, f"+{sobrantes}", "black",
                             tags="pasajero")


def dibujar_leyenda(canvas):
    """Dibuja, debajo del minuto, qué significa cada color de punto."""
    canvas.create_rectangle(8, 36, 128, 76, fill="white", outline="black")
    radio = DIAMETRO_PASAJERO / 2
    for fila, (color, texto) in enumerate([(COLOR_PRIORITARIO, "Prioritario"),
                                           (COLOR_NORMAL, "Normal")]):
        y = 47 + fila * 18
        canvas.create_oval(18 - radio, y - radio, 18 + radio, y + radio,
                           fill=color, outline=COLOR_BORDE_PASAJERO)
        canvas.create_text(30, y, text=texto, anchor="w", font=("Arial", 10))


def distancia_de_parada(id_parada):
    """Distancia en px, a lo largo de la ruta, desde la celda 0 hasta la celda de una parada."""
    return PARADAS[id_parada] * TAM_CELDA


def desplazamientos_buses(buses):
    """
    Recibe la lista de buses de Simulador.estado() y devuelve un diccionario
    id_bus -> desplazamiento en px a lo largo de la ruta respecto a su parada.

    Si un bus está solo en su parada, su desplazamiento es 0. Si varios
    coinciden, se reparten SEPARACION_BUSES px uno de otro, centrados en la
    parada: con 2 buses: -30 y +30; con 3 buses: -60, 0 y +60.
    """
    # 1. Agrupar los buses por parada (diccionario id_parada -> lista de buses)
    grupos = {}
    for bus in buses:
        if bus["parada"] not in grupos:
            grupos[bus["parada"]] = []
        grupos[bus["parada"]].append(bus)

    # 2. Repartir los buses de cada grupo
    desplazamientos = {}
    for grupo in grupos.values():
        cantidad = len(grupo)
        for j, bus in enumerate(grupo):
            desplazamientos[bus["id"]] = (j - (cantidad - 1) / 2) * SEPARACION_BUSES
    return desplazamientos


def posiciones_buses(buses):
    """
    Recibe la lista de buses de Simulador.estado() y devuelve un diccionario
    id_bus -> (x, y, direccion) con dónde y con qué sprite dibujar cada bus
    cuando está detenido en su parada (incluido su desplazamiento).
    """
    desplazamientos = desplazamientos_buses(buses)
    posiciones = {}
    for bus in buses:
        distancia = distancia_de_parada(bus["parada"]) + desplazamientos[bus["id"]]
        posiciones[bus["id"]] = punto_en_ruta(distancia)
    return posiciones


# Etiquetas (tags) del Canvas para los objetos de cada bus. Un bus se dibuja
# con 3 objetos: el sprite, el texto "c/n" y el recuadro negro detrás del texto.
#   "bus"           -> todos los objetos de todos los buses (para borrarlos juntos)
#   "bus_<id>"      -> los 3 objetos de UN bus (para moverlos juntos)
#   "sprite_<id>"   -> solo la imagen de ese bus (para cambiarle el sprite)
#   "contador_<id>" -> solo el texto y el recuadro "c/n" de ese bus

def etiqueta_bus(id_bus):
    """Etiqueta de todos los objetos de un bus, por ejemplo "bus_2"."""
    return f"bus_{id_bus}"


def etiqueta_sprite(id_bus):
    """Etiqueta de la imagen de un bus, por ejemplo "sprite_2"."""
    return f"sprite_{id_bus}"


def etiqueta_contador(id_bus):
    """Etiqueta del contador "c/n" de un bus, por ejemplo "contador_2"."""
    return f"contador_{id_bus}"


def dibujar_contador(canvas, id_bus, x, y, pasajeros, capacidad):
    """
    Dibuja (o vuelve a dibujar) el contador "c/n" de un bus centrado en (x, y),
    encima de su sprite: texto blanco sobre un recuadro negro, para que se lea
    sobre el azul del bus. c = pasajeros a bordo, n = capacidad.
    """
    canvas.delete(etiqueta_contador(id_bus))
    dibujar_etiqueta(canvas, x, y, f"{pasajeros}/{capacidad}", "black",
                     tags=("bus", etiqueta_bus(id_bus), etiqueta_contador(id_bus)))


def dibujar_buses(canvas, buses):
    """
    Borra todos los objetos de bus que hubiera y dibuja cada bus en su
    parada: primero el sprite y encima su contador "c/n".
    Como todo lleva la etiqueta "bus", canvas.delete("bus") no deja objetos
    sueltos (por ejemplo, cuando Deshacer quita un bus).
    """
    canvas.delete("bus")
    posiciones = posiciones_buses(buses)
    for bus in buses:
        x, y, direccion = posiciones[bus["id"]]
        # anchor="center": el centro del sprite queda en (x, y)
        canvas.create_image(x, y, image=sprites_bus[direccion], anchor="center",
                            tags=("bus", etiqueta_bus(bus["id"]), etiqueta_sprite(bus["id"])))
        dibujar_contador(canvas, bus["id"], x, y, bus["pasajeros"], bus["capacidad"])


def actualizar_contadores(canvas, buses):
    """
    Vuelve a escribir el contador "c/n" de cada bus, donde está su sprite
    ahora. Se llama al terminar la animación de un tick.
    """
    for bus in buses:
        x, y = canvas.coords(etiqueta_sprite(bus["id"]))
        dibujar_contador(canvas, bus["id"], x, y, bus["pasajeros"], bus["capacidad"])


def actualizar_minuto(canvas, minuto):
    """Cambia el texto del recuadro del minuto (sin crear objetos nuevos)."""
    canvas.itemconfigure("texto_minuto", text=f"Minuto: {minuto}")


def redibujar(canvas, simulador):
    """
    Dibuja los buses, los pasajeros y el minuto según el estado actual del
    Simulador. Se usa al iniciar; durante la animación los sprites se MUEVEN,
    no se redibujan.
    """
    estado = simulador.estado()
    dibujar_buses(canvas, estado["buses"])
    dibujar_pasajeros(canvas, estado["paradas"])
    actualizar_minuto(canvas, estado["minuto"])


# ---------------------------------------------------------------
# Animación de un tick
# ---------------------------------------------------------------
# Cómo funciona, en tres pasos:
#   1. calcular_trayectos(): con el estado de ANTES y el de DESPUÉS del tick
#      se calcula, para cada bus, desde qué distancia de la ruta sale y
#      cuántos px debe recorrer.
#   2. animar_cuadro(): dibuja UN cuadro (mueve cada sprite a la fracción
#      del recorrido que toca) y le pide a Tkinter, con canvas.after(), que la
#      vuelva a llamar dentro de PASO_ANIMACION_MS para el siguiente cuadro.
#   3. Cuando se dibuja el último cuadro ya no se programa otro after():
#      se llama a la función al_terminar.
#
# ¿Por qué after() y no un ciclo con time.sleep()? Tkinter dibuja la ventana
# y atiende los clics en su ciclo principal (mainloop). Si nuestro código se
# queda dormido dentro de un ciclo, mainloop no corre y la ventana se congela.
# Con after() cada cuadro es una llamada corta: termina, Tkinter redibuja la
# pantalla y, pasado el tiempo pedido, llama al siguiente cuadro.

def recorrido_entre_paradas(id_salida, id_llegada):
    """
    Distancia en px a lo largo de la ruta desde la parada de salida hasta la
    de llegada, siempre hacia adelante. El módulo (%) hace que la vuelta de
    P8 (celda 29) a P1 (celda 1) dé (1 - 29) % 32 = 4 celdas = 240 px,
    en vez de un número negativo.
    """
    celdas = (PARADAS[id_llegada] - PARADAS[id_salida]) % len(RUTA)
    return celdas * TAM_CELDA


def calcular_trayectos(estado_antes, estado_despues):
    """
    Devuelve una lista de trayectos (id_bus, distancia_inicial, recorrido),
    uno por evento del tick. Si no hubo eventos (simulación en pausa), la
    lista queda vacía y no se anima nada.

    El desplazamiento por buses que comparten parada se incluye en ambos
    extremos: el bus sale de donde estaba dibujado (con el desplazamiento de
    antes) y llega exactamente a donde lo pone posiciones_buses() después.
    """
    desplazamientos_antes = desplazamientos_buses(estado_antes["buses"])
    desplazamientos_despues = desplazamientos_buses(estado_despues["buses"])

    trayectos = []
    for evento in estado_despues["eventos"]:
        id_bus = evento["bus"]
        inicio = distancia_de_parada(evento["parada"]) + desplazamientos_antes[id_bus]
        recorrido = (recorrido_entre_paradas(evento["parada"], evento["siguiente_parada"])
                     - desplazamientos_antes[id_bus]
                     + desplazamientos_despues[id_bus])
        trayectos.append((id_bus, inicio, recorrido))
    return trayectos


def total_cuadros():
    """Cuántos cuadros tiene la animación: 600 ms / 16 ms ≈ 38."""
    return max(1, round(DURACION_ANIMACION_MS / PASO_ANIMACION_MS))


def posicion_en_cuadro(trayecto, cuadro, cuadros):
    """
    Devuelve (x, y, direccion) de un bus en el cuadro dado (de 1 a cuadros).
    fraccion va de 0 a 1: en el último cuadro vale exactamente 1 y el bus
    queda en su punto de llegada.
    """
    id_bus, inicio, recorrido = trayecto
    fraccion = cuadro / cuadros
    return punto_en_ruta(inicio + recorrido * fraccion)


def mover_bus(canvas, id_bus, x, y, direccion):
    """
    Mueve un bus a (x, y) con el sprite de la dirección dada, junto con su
    contador. No borra ni crea objetos, así no hay parpadeo.

    El sprite se pone exactamente en (x, y) con coords(). El contador (texto
    y recuadro) se desplaza lo mismo que el sprite con move(dx, dy), así
    lo sigue durante todo el recorrido.
    """
    x_actual, y_actual = canvas.coords(etiqueta_sprite(id_bus))
    canvas.move(etiqueta_contador(id_bus), x - x_actual, y - y_actual)
    canvas.coords(etiqueta_sprite(id_bus), x, y)
    canvas.itemconfigure(etiqueta_sprite(id_bus), image=sprites_bus[direccion])


def animar_cuadro(canvas, trayectos, cuadro, cuadros, al_terminar):
    """
    Dibuja un cuadro de la animación moviendo todos los buses a la vez, y
    programa el siguiente con canvas.after(). Así todos llegan juntos.

    canvas.after(ms, funcion, arg1, arg2, ...) NO espera: solo le deja a
    Tkinter el encargo "dentro de ms milisegundos llama a funcion(arg1, ...)"
    y regresa de inmediato.
    """
    for trayecto in trayectos:
        x, y, direccion = posicion_en_cuadro(trayecto, cuadro, cuadros)
        mover_bus(canvas, trayecto[0], x, y, direccion)

    if cuadro < cuadros:
        canvas.after(PASO_ANIMACION_MS, animar_cuadro,
                     canvas, trayectos, cuadro + 1, cuadros, al_terminar)
    else:
        al_terminar()


def crear_marcador_minuto(canvas):
    """
    Crea, en la esquina superior izquierda, el recuadro donde se muestra el
    minuto. El texto lleva la etiqueta "texto_minuto" para que redibujar()
    lo cambie con itemconfigure, sin crear objetos nuevos.
    """
    canvas.create_rectangle(8, 8, 128, 32, fill="white", outline="black")
    canvas.create_text(16, 20, text="Minuto: 0", anchor="w",
                       font=("Arial", 11, "bold"), tags="texto_minuto")


def validar_parametros(texto_tasa, texto_capacidad):
    """
    Revisa lo que el usuario escribió en los campos de tasa y capacidad.
    Devuelve (tasa, capacidad, None) si los dos valores sirven, o
    (None, None, mensaje_de_error) si alguno no sirve. No dibuja nada.
      - Tasa: número entre 0 y 1 (se acepta coma decimal, por ejemplo "0,5").
      - Capacidad: entero mayor o igual a 1.
    """
    try:
        tasa = float(texto_tasa.strip().replace(",", "."))
    except ValueError:
        return None, None, "La tasa de llegada debe ser un número entre 0 y 1"
    if not 0 <= tasa <= 1:      # También descarta "nan", que no cumple ninguna comparación
        return None, None, "La tasa de llegada debe estar entre 0 y 1"

    try:
        capacidad = int(texto_capacidad.strip())
    except ValueError:
        return None, None, "La capacidad del bus debe ser un número entero"
    if capacidad < 1:
        return None, None, "La capacidad del bus debe ser 1 o más"

    return tasa, capacidad, None


def crear_simulador(tasa_llegada, capacidad_bus):
    """
    Crea un Simulador nuevo con la tasa y la capacidad dadas y el resto de
    parámetros tomados de las constantes del inicio del archivo.
    """
    return Simulador(
        numero_paradas=NUMERO_PARADAS,
        numero_buses=NUMERO_BUSES,
        capacidad_bus=capacidad_bus,
        tasa_llegada=tasa_llegada,
        probabilidad_prioritario=PROBABILIDAD_PRIORITARIO,
        semilla=SEMILLA,
        intentos_llegada=INTENTOS_LLEGADA,
    )


# ---------------------------------------------------------------
# Ventana de estadísticas (se abre al pulsar "Terminar")
# ---------------------------------------------------------------
# Es una ventana aparte (tk.Toplevel) con SU PROPIO Canvas: el Canvas del
# mapa no se toca. Las gráficas se dibujan a mano con rectángulos, líneas,
# arcos y textos del Canvas; así no hace falta otra librería y cada gráfica
# se puede explicar línea por línea.
#
# Los datos salen del Simulador, sin modificarlo:
#   - reporte(): totales y promedios (tarjetas y gráfica de anillo).
#   - estado(): cuántos esperan AHORA en cada parada (gráfica de barras).
#   - serie_esperando y serie_ocupacion: el Simulador guarda una muestra por
#     minuto "para las gráficas" (gráficas de línea). Solo se leen con
#     mostrar(), que devuelve una copia en una lista de Python.

ANCHO_ESTADISTICAS = 900
ALTO_ESTADISTICAS = 640
MARGEN_ESTADISTICAS = 20
SEPARACION_PANELES = 16

COLOR_FONDO_ESTADISTICAS = "#F2F4F8"
COLOR_PANEL = "white"
COLOR_BORDE_PANEL = "#D5DAE3"
COLOR_TEXTO = "#1F2937"
COLOR_TEXTO_SUAVE = "#6B7280"
COLOR_CUADRICULA = "#E5E7EB"
COLOR_ESPERANDO = "#E8710A"          # Naranja: pasajeros esperando
COLOR_ESPERANDO_SUAVE = "#FCE3CC"    # Relleno bajo la línea (el Canvas no tiene transparencia)
COLOR_OCUPACION = "#1A4FA0"          # Azul oscuro: ocupación de la flota
COLOR_OCUPACION_SUAVE = "#D6E2F5"
COLOR_ABORDARON = "#2E9E5B"          # Verde: pasajeros que ya subieron a un bus


def paso_escala(maximo, divisiones):
    """
    Elige cuánto vale cada línea de la cuadrícula del eje Y para que
    'divisiones' líneas alcancen a cubrir 'maximo', usando solo números
    "redondos" (1, 2, 5, 10, 20, 50, ...).
    Ejemplo: maximo=37 y divisiones=4 -> 10 (el eje queda 0, 10, 20, 30, 40).
    """
    base = 1
    while True:
        for multiplo in (1, 2, 5):
            if multiplo * base * divisiones >= maximo:
                return multiplo * base
        base *= 10


def dibujar_panel(canvas, x, y, ancho, alto, titulo=None):
    """Dibuja un recuadro blanco con borde (y su título arriba a la izquierda, si se da)."""
    canvas.create_rectangle(x, y, x + ancho, y + alto, fill=COLOR_PANEL,
                            outline=COLOR_BORDE_PANEL)
    if titulo is not None:
        canvas.create_text(x + 14, y + 18, text=titulo, anchor="w",
                           fill=COLOR_TEXTO, font=("Arial", 11, "bold"))


def dibujar_tarjeta(canvas, x, y, ancho, alto, valor, texto, color):
    """
    Tarjeta con un número grande (valor) y lo que significa (texto) debajo.
    La franja de color a la izquierda ayuda a relacionarla con las gráficas.
    """
    dibujar_panel(canvas, x, y, ancho, alto)
    canvas.create_rectangle(x, y, x + 5, y + alto, fill=color, outline="")
    canvas.create_text(x + 16, y + 30, text=valor, anchor="w",
                       fill=color, font=("Arial", 18, "bold"))
    canvas.create_text(x + 16, y + alto - 18, text=texto, anchor="w",
                       fill=COLOR_TEXTO_SUAVE, font=("Arial", 9))


def dibujar_cuadricula(canvas, izq, der, arriba, abajo, paso, divisiones, sufijo=""):
    """
    Dibuja las líneas horizontales de la cuadrícula y, a su izquierda, el
    valor de cada una (0, paso, 2*paso, ...). Abajo queda el 0 y arriba el tope.
    """
    for k in range(divisiones + 1):
        yy = abajo - (abajo - arriba) * k / divisiones
        canvas.create_line(izq, yy, der, yy, fill=COLOR_CUADRICULA)
        # :g quita los decimales que sobran (25.0 -> "25")
        canvas.create_text(izq - 6, yy, text=f"{k * paso:g}{sufijo}", anchor="e",
                           fill=COLOR_TEXTO_SUAVE, font=("Arial", 8))


def dibujar_grafica_linea(canvas, x, y, ancho, alto, titulo, valores, color,
                          color_suave, tope=None, sufijo="", promedio=None):
    """
    Gráfica de línea de una serie con un valor por minuto (valores[i] es el
    minuto i + 1). Debajo de la línea se rellena un área de color suave.
      - tope: valor que queda en la parte de arriba del eje Y. Si es None se
        calcula con paso_escala() a partir del valor más grande.
      - promedio: si se da, se dibuja como una línea punteada horizontal
        (su valor va en el título, para que el texto no tape la línea).
    """
    dibujar_panel(canvas, x, y, ancho, alto, titulo)

    # Zona donde va la gráfica: el panel menos el espacio del título y los ejes
    izq = x + 48
    der = x + ancho - 16
    arriba = y + 42
    abajo = y + alto - 28

    if len(valores) == 0:
        canvas.create_text((izq + der) / 2, (arriba + abajo) / 2,
                           text="Aún no hay minutos simulados",
                           fill=COLOR_TEXTO_SUAVE, font=("Arial", 10))
        return

    divisiones = 4
    if tope is None:
        paso = paso_escala(max(valores), divisiones)
        tope = paso * divisiones
    else:
        paso = tope / divisiones

    # Cada valor se convierte en un punto (px). El minuto define la x (de
    # izquierda a derecha) y el valor la y (en el Canvas la y crece hacia abajo,
    # por eso se resta desde "abajo").
    n = len(valores)
    puntos = []
    for i in range(n):
        if n == 1:
            px = (izq + der) / 2
        else:
            px = izq + (der - izq) * i / (n - 1)
        py = abajo - (abajo - arriba) * valores[i] / tope
        puntos.extend([px, py])   # create_line y create_polygon reciben x1, y1, x2, y2, ...

    # Orden de dibujo: lo último que se dibuja queda encima.
    # 1) Relleno: un polígono que baja desde la línea hasta el eje X
    if n >= 2:
        canvas.create_polygon(izq, abajo, *puntos, der, abajo,
                              fill=color_suave, outline="")
    # 2) Cuadrícula encima del relleno, para que se sigan viendo las líneas
    dibujar_cuadricula(canvas, izq, der, arriba, abajo, paso, divisiones, sufijo)
    # 3) La línea de la serie y un punto en el último valor (el "ahora")
    if n >= 2:
        canvas.create_line(*puntos, fill=color, width=2)
    ultimo_x, ultimo_y = puntos[-2], puntos[-1]
    canvas.create_oval(ultimo_x - 4, ultimo_y - 4, ultimo_x + 4, ultimo_y + 4,
                       fill=color, outline="white", width=2)

    # 4) Promedio como línea punteada (dash = 4 px de línea, 3 px de hueco)
    if promedio is not None:
        py = abajo - (abajo - arriba) * promedio / tope
        canvas.create_line(izq, py, der, py, fill=color, dash=(4, 3))

    # Eje X: solo el primer y el último minuto, para no amontonar números
    canvas.create_text(izq, abajo + 12, text="min 1", anchor="w",
                       fill=COLOR_TEXTO_SUAVE, font=("Arial", 8))
    canvas.create_text(der, abajo + 12, text=f"min {n}", anchor="e",
                       fill=COLOR_TEXTO_SUAVE, font=("Arial", 8))


def dibujar_barras_paradas(canvas, x, y, ancho, alto, paradas):
    """
    Una barra por parada con los pasajeros que esperan AHORA. Cada barra se
    apila en dos partes con los mismos colores del mapa: abajo los
    prioritarios (azul) y encima los normales (gris).
    """
    dibujar_panel(canvas, x, y, ancho, alto, "Esperando ahora en cada parada")

    # Leyenda en la esquina superior derecha
    leyenda_x = x + ancho - 190
    for texto, color in (("Prioritarios", COLOR_PRIORITARIO), ("Normales", COLOR_NORMAL)):
        canvas.create_rectangle(leyenda_x, y + 13, leyenda_x + 10, y + 23,
                                fill=color, outline="")
        canvas.create_text(leyenda_x + 14, y + 18, text=texto, anchor="w",
                           fill=COLOR_TEXTO_SUAVE, font=("Arial", 8))
        leyenda_x += 95

    izq = x + 48
    der = x + ancho - 16
    arriba = y + 48
    abajo = y + alto - 28

    divisiones = 4
    maximo = max(parada["esperando"] for parada in paradas)
    paso = paso_escala(maximo, divisiones)
    tope = paso * divisiones
    dibujar_cuadricula(canvas, izq, der, arriba, abajo, paso, divisiones)

    # Cada parada tiene un "hueco" del mismo ancho; la barra ocupa el 60 %
    hueco = (der - izq) / len(paradas)
    ancho_barra = hueco * 0.6
    for i, parada in enumerate(paradas):
        centro = izq + hueco * (i + 0.5)
        x1 = centro - ancho_barra / 2
        x2 = centro + ancho_barra / 2
        prioritarios = parada["prioritarios"]
        normales = parada["esperando"] - prioritarios
        alto_prioritarios = (abajo - arriba) * prioritarios / tope
        alto_normales = (abajo - arriba) * normales / tope

        if prioritarios > 0:
            canvas.create_rectangle(x1, abajo - alto_prioritarios, x2, abajo,
                                    fill=COLOR_PRIORITARIO, outline="")
        if normales > 0:
            canvas.create_rectangle(x1, abajo - alto_prioritarios - alto_normales,
                                    x2, abajo - alto_prioritarios,
                                    fill=COLOR_NORMAL, outline="")
        # Total encima de la barra y nombre de la parada debajo
        canvas.create_text(centro, abajo - alto_prioritarios - alto_normales - 8,
                           text=str(parada["esperando"]), fill=COLOR_TEXTO,
                           font=("Arial", 8, "bold"))
        canvas.create_text(centro, abajo + 12, text=f"P{parada['id'] + 1}",
                           fill=COLOR_TEXTO_SUAVE, font=("Arial", 8))


def dibujar_anillo(canvas, x, y, ancho, alto, abordados, esperando):
    """
    Gráfica de anillo: de todos los pasajeros generados, qué parte ya subió
    a un bus (verde) y qué parte sigue esperando (naranja).
    """
    dibujar_panel(canvas, x, y, ancho, alto, "¿Qué pasó con los generados?")
    total = abordados + esperando
    if total == 0:
        canvas.create_text(x + ancho / 2, y + alto / 2, text="Aún no llegan pasajeros",
                           fill=COLOR_TEXTO_SUAVE, font=("Arial", 10))
        return

    radio = 62
    grosor = 20
    centro_x = x + 26 + radio
    centro_y = y + alto / 2 + 12
    caja = (centro_x - radio, centro_y - radio, centro_x + radio, centro_y + radio)

    # create_arc dibuja una "rebanada" de pastel. Los ángulos van en grados:
    # 0° es a la derecha (las 3 en punto) y 90° arriba. Con start=90 y un
    # extent negativo, la rebanada arranca arriba y gira como el reloj.
    if esperando == 0:
        canvas.create_oval(*caja, fill=COLOR_ABORDARON, outline="")
    elif abordados == 0:
        canvas.create_oval(*caja, fill=COLOR_ESPERANDO, outline="")
    else:
        grados_abordados = 360 * abordados / total
        canvas.create_arc(*caja, start=90, extent=-grados_abordados,
                          fill=COLOR_ABORDARON, outline="")
        canvas.create_arc(*caja, start=90 - grados_abordados,
                          extent=-(360 - grados_abordados),
                          fill=COLOR_ESPERANDO, outline="")
    # Un círculo blanco en el centro convierte el pastel en un anillo
    interior = radio - grosor
    canvas.create_oval(centro_x - interior, centro_y - interior,
                       centro_x + interior, centro_y + interior,
                       fill=COLOR_PANEL, outline="")
    # int() redondea hacia abajo: si alguien sigue esperando nunca dice "100 %"
    canvas.create_text(centro_x, centro_y - 7, text=f"{int(100 * abordados / total)} %",
                       fill=COLOR_TEXTO, font=("Arial", 14, "bold"))
    canvas.create_text(centro_x, centro_y + 13, text="abordaron",
                       fill=COLOR_TEXTO_SUAVE, font=("Arial", 8))

    # Leyenda a la derecha del anillo, con las cantidades
    leyenda_x = centro_x + radio + 22
    filas = (("Abordaron", abordados, COLOR_ABORDARON),
             ("Siguen esperando", esperando, COLOR_ESPERANDO),
             ("Generados", total, COLOR_TEXTO))
    for k, (texto, cantidad, color) in enumerate(filas):
        fila_y = centro_y - 40 + k * 40
        canvas.create_rectangle(leyenda_x, fila_y - 5, leyenda_x + 10, fila_y + 5,
                                fill=color, outline="")
        canvas.create_text(leyenda_x + 16, fila_y, text=texto, anchor="w",
                           fill=COLOR_TEXTO_SUAVE, font=("Arial", 8))
        canvas.create_text(leyenda_x + 16, fila_y + 15, text=str(cantidad), anchor="w",
                           fill=COLOR_TEXTO, font=("Arial", 11, "bold"))


def dibujar_estadisticas(canvas, reporte, paradas, serie_esperando,
                         serie_ocupacion, tasa, capacidad):
    """
    Dibuja toda la ventana de estadísticas en el Canvas dado:
      encabezado | 6 tarjetas con reporte() | 2 gráficas de línea por minuto |
      barras por parada y anillo de abordados.
    """
    m = MARGEN_ESTADISTICAS
    s = SEPARACION_PANELES
    ancho_util = ANCHO_ESTADISTICAS - 2 * m

    # Encabezado
    canvas.create_text(m, 26, text="Estadísticas de la simulación", anchor="w",
                       fill=COLOR_TEXTO, font=("Arial", 16, "bold"))
    canvas.create_text(m, 52, anchor="w", fill=COLOR_TEXTO_SUAVE, font=("Arial", 10),
                       text=f"Simulación terminada en el minuto {reporte['minuto']}  ·  "
                            f"tasa de llegada {tasa}  ·  capacidad {capacidad} por bus")

    # Fila de tarjetas: los valores de reporte()
    tarjetas = (
        (str(reporte["pasajeros_generados"]), "Generados", COLOR_TEXTO),
        (str(reporte["pasajeros_abordados"]), "Abordaron un bus", COLOR_ABORDARON),
        (str(reporte["pasajeros_esperando"]), "Siguen esperando", COLOR_ESPERANDO),
        (f"{reporte['espera_promedio']:.1f} min", "Espera promedio", COLOR_ESPERANDO),
        (f"{reporte['ocupacion_promedio'] * 100:.0f} %", "Ocupación promedio", COLOR_OCUPACION),
        (str(reporte["buses"]), "Buses en servicio", COLOR_OCUPACION),
    )
    separacion_tarjetas = 10
    ancho_tarjeta = (ancho_util - separacion_tarjetas * (len(tarjetas) - 1)) / len(tarjetas)
    for i, (valor, texto, color) in enumerate(tarjetas):
        dibujar_tarjeta(canvas, m + i * (ancho_tarjeta + separacion_tarjetas), 76,
                        ancho_tarjeta, 78, valor, texto, color)

    # Fila de gráficas de línea (una muestra por minuto)
    y_lineas = 170
    ancho_mitad = (ancho_util - s) / 2
    ahora_esperando = serie_esperando[-1] if serie_esperando else 0
    dibujar_grafica_linea(canvas, m, y_lineas, ancho_mitad, 220,
                          f"Pasajeros esperando (ahora: {ahora_esperando})",
                          serie_esperando, COLOR_ESPERANDO, COLOR_ESPERANDO_SUAVE)
    # La ocupación viene de 0 a 1: se pasa a porcentaje para leerla mejor
    ocupacion_porcentaje = [valor * 100 for valor in serie_ocupacion]
    promedio_ocupacion = reporte["ocupacion_promedio"] * 100
    if serie_ocupacion:
        titulo_ocupacion = f"Ocupación de la flota (promedio: {promedio_ocupacion:.0f} %)"
    else:
        titulo_ocupacion = "Ocupación de la flota"
        promedio_ocupacion = None          # Sin minutos no hay línea de promedio
    dibujar_grafica_linea(canvas, m + ancho_mitad + s, y_lineas, ancho_mitad, 220,
                          titulo_ocupacion, ocupacion_porcentaje,
                          COLOR_OCUPACION, COLOR_OCUPACION_SUAVE,
                          tope=100, sufijo=" %", promedio=promedio_ocupacion)

    # Fila de abajo: barras por parada (más ancha) y anillo
    y_abajo = y_lineas + 220 + s
    alto_abajo = ALTO_ESTADISTICAS - m - y_abajo
    ancho_barras = 520
    dibujar_barras_paradas(canvas, m, y_abajo, ancho_barras, alto_abajo, paradas)
    dibujar_anillo(canvas, m + ancho_barras + s, y_abajo, ancho_util - ancho_barras - s,
                   alto_abajo, reporte["pasajeros_abordados"], reporte["pasajeros_esperando"])


# ---------------------------------------------------------------
# La aplicación: Canvas, barra de controles y bucle automático
# ---------------------------------------------------------------
# BUCLE AUTOMÁTICO (sin time.sleep, todo con after()):
#
#   Play --> ciclo() --> avanzar_un_tick() --> animación (38 cuadros con after)
#              ^                                         |
#              |                                         v
#              +--- after(200 ms) <--- terminar_tick(): dibuja pasajeros,
#                   (o 100 ms si está       contadores y minuto; ejecuta las
#                    en pausa: revisa)      operaciones pendientes
#
# OPERACIONES DEL OPERADOR (Play/Pausa, Agregar bus, Deshacer, Aplicar):
# no se ejecutan a mitad de una animación. Cada clic mete la operación en la
# Cola "pendientes" (FIFO: se ejecutan en el orden en que se pidieron). Si no
# hay animación, se ejecutan enseguida; si la hay, terminar_tick() las
# ejecuta todas justo al terminar, antes de pedir el siguiente tick.

class InterfazSimulador:
    """
    Guarda todo lo que la interfaz necesita recordar entre un clic y otro.

    Atributos:
        ventana: la ventana de Tkinter.
        simulador: el Simulador actual.
        canvas: el único Canvas (900x600) con el fondo, los pasajeros y los buses.
        tasa, capacidad: valores con los que se creó el Simulador actual
            (se muestran en el encabezado de las estadísticas).
        iniciado: False hasta el primer Play (al abrir la app no corre nada).
        terminada: True después de pulsar "Terminar"; solo queda reiniciar.
        animando: True mientras se anima un tick.
        id_ciclo: identificador del after() que llamará a ciclo(), o None.
        pendientes: Cola (estructuras/cola.py) de operaciones que esperan a
            que termine la animación.
        boton_play: botón Play/Pausa (su texto sale de estado()["en_pausa"]).
        etiqueta_mensaje: etiqueta donde se muestran los mensajes al usuario.
        ventana_estadisticas: la ventana (tk.Toplevel) de estadísticas, o
            None si está cerrada.
        canvas_estadisticas: el Canvas de esa ventana, donde van las gráficas.
    """

    def __init__(self, ventana):
        """Crea el Canvas, los controles y el primer Simulador (sin arrancar)."""
        self.ventana = ventana
        self.tasa = TASA_LLEGADA
        self.capacidad = CAPACIDAD_BUS
        self.simulador = crear_simulador(self.tasa, self.capacidad)
        self.iniciado = False
        self.terminada = False
        self.ventana_estadisticas = None
        self.canvas_estadisticas = None
        self.animando = False
        self.id_ciclo = None
        self.pendientes = Cola()

        # Un solo Canvas para todo: fondo, marcas, pasajeros y buses.
        self.canvas = tk.Canvas(ventana, width=ANCHO, height=ALTO, highlightthickness=0)
        self.canvas.pack()

        # anchor="nw": la esquina superior izquierda de la imagen va en (0, 0)
        self.canvas.create_image(0, 0, image=cargar_fondo(), anchor="nw")
        if MOSTRAR_DEPURACION:
            dibujar_depuracion(self.canvas)
        if MOSTRAR_PLACAS:
            dibujar_paradas(self.canvas)   # Encima de la depuración
        crear_marcador_minuto(self.canvas)
        dibujar_leyenda(self.canvas)
        cargar_sprites()

        self.crear_controles()
        redibujar(self.canvas, self.simulador)
        self.actualizar_controles()

    # ----------------------------- controles -----------------------------

    def crear_controles(self):
        """
        Crea la barra de controles DEBAJO del Canvas (un tk.Frame), así el
        Canvas no cambia de tamaño ni de coordenadas.
        """
        barra = tk.Frame(self.ventana)
        barra.pack(fill="x", padx=8, pady=6)

        # Fila 1: botones de operación y la Pila de operaciones
        fila_botones = tk.Frame(barra)
        fila_botones.pack(fill="x")
        self.boton_play = tk.Button(fila_botones, text="▶ Play", width=10,
                                    command=lambda: self.pedir_operacion(("play_pausa",)))
        self.boton_play.pack(side="left")
        tk.Button(fila_botones, text="Agregar bus",
                  command=lambda: self.pedir_operacion(("agregar_bus",))).pack(side="left", padx=4)
        tk.Button(fila_botones, text="Deshacer",
                  command=lambda: self.pedir_operacion(("deshacer",))).pack(side="left")
        tk.Button(fila_botones, text="Terminar",
                  command=lambda: self.pedir_operacion(("terminar",))).pack(side="left", padx=4)
        self.etiqueta_historial = tk.Label(fila_botones, anchor="w")
        self.etiqueta_historial.pack(side="left", padx=12)

        # Fila 2: parámetros para reiniciar la simulación
        fila_parametros = tk.Frame(barra)
        fila_parametros.pack(fill="x", pady=(6, 0))
        tk.Label(fila_parametros, text="Tasa de llegada (0 a 1)").pack(side="left")
        self.entrada_tasa = tk.Entry(fila_parametros, width=6)
        self.entrada_tasa.insert(0, str(TASA_LLEGADA))
        self.entrada_tasa.pack(side="left", padx=(4, 12))
        tk.Label(fila_parametros, text="Capacidad del bus (entero >= 1)").pack(side="left")
        self.entrada_capacidad = tk.Entry(fila_parametros, width=6)
        self.entrada_capacidad.insert(0, str(CAPACIDAD_BUS))
        self.entrada_capacidad.pack(side="left", padx=(4, 12))
        tk.Button(fila_parametros, text="Aplicar y reiniciar",
                  command=self.pedir_reinicio).pack(side="left")

        # Última fila: mensajes para el usuario
        self.etiqueta_mensaje = tk.Label(barra, text="Pulse Play para empezar", anchor="w",
                                         fg="#1A4FA0")
        self.etiqueta_mensaje.pack(fill="x", pady=(4, 0))

    def actualizar_controles(self):
        """
        Pone el texto del botón Play/Pausa según el estado del Simulador:
        dice "Pausa" solo si la simulación ya arrancó y NO está en pausa.
        También muestra la Pila de operaciones (tamaño y acción del tope).
        Se llama después de cada operación y de cada tick, así lo que se ve
        siempre coincide con estado() (también tras Deshacer).
        """
        estado = self.simulador.estado()
        if self.iniciado and not estado["en_pausa"]:
            self.boton_play.config(text="⏸ Pausa")
        else:
            self.boton_play.config(text="▶ Play")

        ultima = estado["ultima_accion"]
        if ultima is None:
            texto_ultima = "ninguna"
        else:
            texto_ultima = NOMBRES_ACCIONES.get(ultima, ultima)
        self.etiqueta_historial.config(
            text=f"Historial: {estado['historial']} acciones - última: {texto_ultima}")

    def mostrar_mensaje(self, texto):
        """Muestra un texto en la etiqueta de mensajes."""
        self.etiqueta_mensaje.config(text=texto)

    # ----------------------- operaciones del operador -----------------------

    def pedir_operacion(self, operacion):
        """
        Recibe un clic del operador como una tupla, por ejemplo ("play_pausa",),
        y la mete en la Cola de pendientes. Si no hay animación se ejecuta ya;
        si la hay, se ejecutará en terminar_tick().
        """
        self.pendientes.agregar(operacion)
        if self.animando:
            self.mostrar_mensaje("Se hará al terminar el movimiento de los buses")
        else:
            self.ejecutar_pendientes()

    def ejecutar_pendientes(self):
        """Saca de la Cola y ejecuta, en orden de llegada, todas las operaciones pendientes."""
        while not self.pendientes.esta_vacia():
            self.ejecutar_operacion(self.pendientes.borrar())
        self.actualizar_controles()

    def ejecutar_operacion(self, operacion):
        """
        Llama al método que corresponde según el nombre de la operación.
        Si la simulación ya terminó, solo se acepta "aplicar" (reiniciar).
        """
        nombre = operacion[0]
        if self.terminada and nombre != "aplicar":
            self.mostrar_mensaje('La simulación terminó: use "Aplicar y reiniciar" para empezar otra')
            return
        if nombre == "play_pausa":
            self.alternar_play_pausa()
        elif nombre == "agregar_bus":
            self.agregar_bus()
        elif nombre == "deshacer":
            self.deshacer()
        elif nombre == "terminar":
            self.terminar()
        elif nombre == "aplicar":
            self.reiniciar(operacion[1], operacion[2])

    def pedir_reinicio(self):
        """
        Botón "Aplicar y reiniciar": valida los campos EN EL MOMENTO del clic.
        Si algo no sirve, solo muestra el error (no cambia nada). Si sirve,
        pide la operación ("aplicar", tasa, capacidad), que espera a que
        termine la animación como las demás.
        """
        tasa, capacidad, error = validar_parametros(self.entrada_tasa.get(),
                                                    self.entrada_capacidad.get())
        if error is not None:
            self.mostrar_mensaje(error)
            return
        self.pedir_operacion(("aplicar", tasa, capacidad))

    def reiniciar(self, tasa, capacidad):
        """
        Crea un Simulador NUEVO con la tasa y capacidad dadas y el resto de
        constantes (no se cambian atributos del Simulador viejo desde fuera).
        Se pierde todo lo del Simulador anterior, incluida su Pila de
        operaciones: es lo esperado, porque es otra simulación.
        Cancela el after() pendiente del bucle y deja la app sin iniciar
        (hay que pulsar Play), y redibuja buses, pasajeros y minuto desde cero.
        Cierra la ventana de estadísticas: eran de la simulación anterior.
        """
        self.cancelar_ciclo()
        self.iniciado = False
        self.terminada = False
        self.cerrar_estadisticas()
        self.tasa = tasa
        self.capacidad = capacidad
        self.simulador = crear_simulador(tasa, capacidad)
        redibujar(self.canvas, self.simulador)
        self.mostrar_mensaje(f"Reiniciado con tasa {tasa} y capacidad {capacidad}. "
                             "Pulse Play para empezar")

    def agregar_bus(self):
        """
        Agrega un bus con simulador.agregar_bus() (el Simulador lo pone en la
        parada más llena). Con MAX_BUSES buses no se llama al Simulador.
        Se vuelven a dibujar todos los buses: el nuevo aparece con su sprite y
        su contador, y si comparte parada los demás se reacomodan.
        """
        if len(self.simulador.estado()["buses"]) >= MAX_BUSES:
            self.mostrar_mensaje(f"No se pueden agregar más buses: el máximo es {MAX_BUSES}")
            return
        self.simulador.agregar_bus()
        estado = self.simulador.estado()
        dibujar_buses(self.canvas, estado["buses"])
        nuevo = estado["buses"][-1]
        self.mostrar_mensaje(f"Se agregó el bus {nuevo['id'] + 1} en la parada P{nuevo['parada'] + 1}")

    def deshacer(self):
        """
        Deshace la última operación con simulador.deshacer() y muestra el texto
        que devuelve. Si se quitó un bus, dibujar_buses() borra todo lo que
        tiene la etiqueta "bus" y vuelve a dibujar los que quedan, así no
        quedan objetos sueltos. Si se deshizo una pausa, el bucle lo nota solo
        (ciclo() revisa estado()["en_pausa"]).
        """
        mensaje = self.simulador.deshacer()
        if mensaje is None:
            mensaje = "No hay nada que deshacer"
        self.mostrar_mensaje(mensaje)
        dibujar_buses(self.canvas, self.simulador.estado()["buses"])

    def alternar_play_pausa(self):
        """
        - Primer Play: arranca el bucle SIN llamar a reanudar(), para no meter
          en la Pila una acción que no ocurrió (el Simulador no estaba en pausa).
        - Después: Pausa llama a pausar() y Play llama a reanudar(), así las
          dos quedan en la Pila de operaciones del Simulador.
        """
        if not self.iniciado:
            self.iniciado = True
            self.mostrar_mensaje("Simulación en marcha")
            self.programar_ciclo(0)
        elif self.simulador.estado()["en_pausa"]:
            self.simulador.reanudar()
            self.mostrar_mensaje("Simulación reanudada")
        else:
            self.simulador.pausar()
            self.mostrar_mensaje("Simulación en pausa")

    def terminar(self):
        """
        Botón "Terminar": acaba la simulación actual y muestra sus
        estadísticas finales. NO llama a pausar() del Simulador, porque eso
        metería en la Pila una acción que Deshacer podría revertir: solo
        detiene el bucle de la interfaz. Después solo queda "Aplicar y reiniciar".
        """
        self.cancelar_ciclo()
        self.iniciado = False
        self.terminada = True
        minuto = self.simulador.estado()["minuto"]
        self.mostrar_mensaje(f"Simulación terminada en el minuto {minuto}. "
                             'Use "Aplicar y reiniciar" para empezar otra')
        self.mostrar_estadisticas()

    # ------------------------- ventana de estadísticas -------------------------

    def mostrar_estadisticas(self):
        """
        Abre la ventana de estadísticas con los datos finales del Simulador.
        Si quedara una abierta, primero se cierra, para no tener dos.
        """
        self.cerrar_estadisticas()
        self.ventana_estadisticas = tk.Toplevel(self.ventana)
        self.ventana_estadisticas.title("Estadísticas de la simulación")
        self.ventana_estadisticas.resizable(False, False)
        # transient: la ventana queda siempre por encima de la principal
        self.ventana_estadisticas.transient(self.ventana)
        # Si el usuario la cierra con la X, también se olvida la referencia
        self.ventana_estadisticas.protocol("WM_DELETE_WINDOW", self.cerrar_estadisticas)
        self.canvas_estadisticas = tk.Canvas(
            self.ventana_estadisticas, width=ANCHO_ESTADISTICAS,
            height=ALTO_ESTADISTICAS, highlightthickness=0,
            bg=COLOR_FONDO_ESTADISTICAS)
        self.canvas_estadisticas.pack()

        dibujar_estadisticas(self.canvas_estadisticas,
                             self.simulador.reporte(),
                             self.simulador.estado()["paradas"],
                             self.simulador.serie_esperando.mostrar(),
                             self.simulador.serie_ocupacion.mostrar(),
                             self.tasa, self.capacidad)

    def cerrar_estadisticas(self):
        """Cierra la ventana de estadísticas, si está abierta."""
        if self.ventana_estadisticas is not None:
            self.ventana_estadisticas.destroy()
            self.ventana_estadisticas = None
            self.canvas_estadisticas = None

    # --------------------------- bucle automático ---------------------------

    def programar_ciclo(self, espera_ms):
        """Pide a Tkinter que llame a ciclo() dentro de espera_ms (cancela el pedido anterior)."""
        self.cancelar_ciclo()
        self.id_ciclo = self.ventana.after(espera_ms, self.ciclo)

    def cancelar_ciclo(self):
        """Cancela el after() pendiente del bucle, si lo hay."""
        if self.id_ciclo is not None:
            self.ventana.after_cancel(self.id_ciclo)
            self.id_ciclo = None

    def ciclo(self):
        """
        Un paso del bucle automático. Si la simulación está en pausa no pide
        un tick: vuelve a revisar dentro de REVISION_EN_PAUSA_MS.
        """
        self.id_ciclo = None
        if not self.iniciado or self.animando:
            return
        if self.simulador.estado()["en_pausa"]:
            self.programar_ciclo(REVISION_EN_PAUSA_MS)
        else:
            self.avanzar_un_tick()

    def avanzar_un_tick(self):
        """
        Avanza la simulación UN minuto y anima el recorrido de los buses.
        El minuto, los pasajeros y los contadores solo cambian al terminar.
        """
        estado_antes = self.simulador.estado()
        self.simulador.avanzar_tick()          # Salto instantáneo del modelo
        estado_despues = self.simulador.estado()

        trayectos = calcular_trayectos(estado_antes, estado_despues)
        self.animando = True
        # lambda: "cuando termine la animación, llama a terminar_tick con
        # el estado de después" (animar_cuadro llama a al_terminar sin argumentos)
        animar_cuadro(self.canvas, trayectos, 1, total_cuadros(),
                      lambda: self.terminar_tick(estado_despues))

    def terminar_tick(self, estado_despues):
        """
        Se llama tras el último cuadro de la animación: dibuja las filas, los
        contadores y el minuto nuevos, ejecuta las operaciones que se pidieron
        durante la animación y programa el siguiente paso del bucle.
        """
        dibujar_pasajeros(self.canvas, estado_despues["paradas"])
        actualizar_contadores(self.canvas, estado_despues["buses"])
        actualizar_minuto(self.canvas, estado_despues["minuto"])
        self.animando = False

        self.ejecutar_pendientes()

        if self.iniciado:
            if self.simulador.estado()["en_pausa"]:
                self.programar_ciclo(REVISION_EN_PAUSA_MS)
            else:
                self.programar_ciclo(PAUSA_ENTRE_TICKS_MS)


def main():
    """Crea la ventana y la interfaz, y arranca el ciclo principal de Tkinter."""
    ventana = tk.Tk()
    ventana.title("Simulador de buses")
    ventana.resizable(False, False)
    InterfazSimulador(ventana)
    ventana.mainloop()


if __name__ == "__main__":
    main()
