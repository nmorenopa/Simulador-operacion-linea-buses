"""
Interfaz gráfica del simulador de buses (Tkinter).

FASE 2c: dibuja el fondo, los buses del Simulador y los pasajeros que esperan
en cada parada (azul = prioritario, gris = normal). Un botón provisional
avanza un tick y los buses se ANIMAN desde su parada hasta la siguiente,
siguiendo la vía (giran en las esquinas y cambian de sprite). Las filas de
pasajeros y el reloj se actualizan cuando termina la animación.

La animación es solo visual: avanzar_tick() cambia el estado de golpe y la
interfaz dibuja el recorrido entre el estado de antes y el de después.

Separación: la interfaz NO contiene lógica de la simulación. Solo crea el
Simulador, llama avanzar_tick() y lee estado() para dibujar.
"""
import tkinter as tk
from pathlib import Path

from PIL import Image, ImageTk

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
# Para que en la demo se vean filas largas en las paradas: subir TASA_LLEGADA
# (por ejemplo 0.5), bajar CAPACIDAD_BUS (por ejemplo 5) o usar menos buses.
NUMERO_BUSES = 5
CAPACIDAD_BUS = 20
TASA_LLEGADA = 0.4              # Probabilidad de que llegue un pasajero por parada y minuto
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
# Las paradas se ubican solo con la grid, por eso los letreros dibujados en
# FONDO.png no coinciden del todo con ellas: algunas paradas no tienen letrero
# y algunos letreros quedan sin parada. Para que eso no confunda, cada parada
# lleva su propia marca (ver dibujar_paradas). Si se cambia el fondo, basta
# con cambiar esta lista (y NUMERO_PARADAS si cambia la cantidad).
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


def etiqueta_bus(id_bus):
    """
    Etiqueta (tag) única del sprite de un bus en el Canvas, por ejemplo "bus_2".
    Con ella se encuentra el sprite para moverlo sin guardar su número de item.
    """
    return f"bus_{id_bus}"


def dibujar_buses(canvas, buses):
    """
    Borra los sprites de bus que hubiera y crea uno por bus, en su parada.

    Cada sprite lleva dos etiquetas: "bus" (la comparten todos, así
    canvas.delete("bus") borra SOLO los buses y deja el fondo y las marcas)
    y "bus_<id>" (única, para poder moverlo durante la animación).
    """
    canvas.delete("bus")
    for id_bus, (x, y, direccion) in posiciones_buses(buses).items():
        # anchor="center": el centro del sprite queda en (x, y)
        canvas.create_image(x, y, image=sprites_bus[direccion], anchor="center",
                            tags=("bus", etiqueta_bus(id_bus)))


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
    Mueve el sprite existente de un bus a (x, y) y le pone el sprite de la
    dirección dada. No borra ni crea objetos, así no hay parpadeo.
    """
    canvas.coords(etiqueta_bus(id_bus), x, y)
    canvas.itemconfigure(etiqueta_bus(id_bus), image=sprites_bus[direccion])


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


def main():
    """Crea la ventana, el Simulador y el Canvas con el fondo, las paradas y los buses."""
    ventana = tk.Tk()
    ventana.title("Simulador de buses")
    ventana.resizable(False, False)

    simulador = Simulador(
        numero_paradas=NUMERO_PARADAS,
        numero_buses=NUMERO_BUSES,
        capacidad_bus=CAPACIDAD_BUS,
        tasa_llegada=TASA_LLEGADA,
        probabilidad_prioritario=PROBABILIDAD_PRIORITARIO,
        semilla=SEMILLA,
        intentos_llegada=INTENTOS_LLEGADA,
    )

    # Un solo Canvas para todo: fondo, marcas y buses.
    canvas = tk.Canvas(ventana, width=ANCHO, height=ALTO, highlightthickness=0)
    canvas.pack()

    # anchor="nw": la esquina superior izquierda de la imagen va en (0, 0)
    canvas.create_image(0, 0, image=cargar_fondo(), anchor="nw")
    if MOSTRAR_DEPURACION:
        dibujar_depuracion(canvas)
    if MOSTRAR_PLACAS:
        dibujar_paradas(canvas)   # Después, para que quede encima de la depuración
    crear_marcador_minuto(canvas)
    dibujar_leyenda(canvas)

    cargar_sprites()
    redibujar(canvas, simulador)

    # Bandera: True mientras hay una animación en curso. Mientras lo sea no se
    # puede pedir otro tick (además el botón queda desactivado).
    animando = False

    def avanzar_un_tick():
        """
        Avanza la simulación UN minuto y anima el recorrido de los buses.
        El minuto mostrado solo cambia cuando termina la animación.
        """
        nonlocal animando     # Para poder cambiar la variable de main()
        if animando:
            return

        estado_antes = simulador.estado()
        simulador.avanzar_tick()          # Salto instantáneo del modelo
        estado_despues = simulador.estado()

        trayectos = calcular_trayectos(estado_antes, estado_despues)
        if not trayectos:
            return            # En pausa: no hubo eventos, no hay nada que animar

        animando = True
        boton_tick.config(state="disabled")

        def al_terminar():
            """
            Se llama tras el último cuadro: muestra las filas de pasajeros y el
            minuto nuevos, y libera el botón.
            """
            nonlocal animando
            dibujar_pasajeros(canvas, estado_despues["paradas"])
            actualizar_minuto(canvas, estado_despues["minuto"])
            animando = False
            boton_tick.config(state="normal")

        animar_cuadro(canvas, trayectos, 1, total_cuadros(), al_terminar)

    # PROVISIONAL: este botón se reemplaza en la fase 3 por los controles
    # definitivos (reproducir, pausar, etc.).
    boton_tick = tk.Button(ventana, text="Avanzar tick", command=avanzar_un_tick)
    boton_tick.pack(pady=4)

    ventana.mainloop()


if __name__ == "__main__":
    main()
