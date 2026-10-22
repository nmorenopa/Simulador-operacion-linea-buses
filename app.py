"""
Interfaz gráfica del simulador de buses (Tkinter).

FASE 2a: dibuja el fondo, las 8 paradas y los buses del Simulador, cada uno
en la celda de su parada y con el sprite de su dirección. Todavía no hay
movimiento suave: un botón provisional avanza un tick y los buses saltan.

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
NUMERO_BUSES = 3
CAPACIDAD_BUS = 20
TASA_LLEGADA = 0.3              # Probabilidad de que llegue un pasajero por parada y minuto
PROBABILIDAD_PRIORITARIO = 0.2
SEMILLA = 42                    # Con la misma semilla, la simulación se repite igual


# ---------------------------------------------------------------
# Constantes de la interfaz
# ---------------------------------------------------------------
# Si es True se dibujan las marcas de depuración (celdas y esquinas).
# Las marcas de las paradas se dibujan siempre, porque son parte de la demo.
MOSTRAR_DEPURACION = True

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


def dibujar_etiqueta(canvas, x, y, texto, color):
    """
    Escribe un texto con un recuadro de color detrás, para que se lea bien
    sobre el fondo. Primero se crea el texto, luego se mide con bbox() y
    se dibuja el recuadro debajo con tag_lower().
    """
    id_texto = canvas.create_text(x, y, text=texto, fill="white",
                                  font=("Arial", 9, "bold"))
    x1, y1, x2, y2 = canvas.bbox(id_texto)
    id_recuadro = canvas.create_rectangle(x1 - 2, y1 - 1, x2 + 2, y2 + 1,
                                          fill=color, outline="")
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
    Dibuja la marca de cada parada, pensada para la demo:
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


def posiciones_buses(buses):
    """
    Recibe la lista de buses de Simulador.estado() y devuelve, para cada
    uno, una tupla (x, y, direccion) con dónde dibujarlo.

    Pasos:
      1. Se agrupan los buses por parada (diccionario id_parada -> buses).
      2. Cada parada se convierte en su celda de la ruta con PARADAS[id].
      3. Si en un grupo hay varios buses, se reparten a lo largo de la ruta,
         SEPARACION_BUSES px uno de otro y centrados en la parada:
         con 2 buses: -30 y +30; con 3 buses: -60, 0 y +60.
    """
    grupos = {}
    for bus in buses:
        if bus["parada"] not in grupos:
            grupos[bus["parada"]] = []
        grupos[bus["parada"]].append(bus)

    posiciones = []
    for id_parada, grupo in grupos.items():
        distancia_parada = PARADAS[id_parada] * TAM_CELDA
        cantidad = len(grupo)
        for j in range(cantidad):
            desplazamiento = (j - (cantidad - 1) / 2) * SEPARACION_BUSES
            posiciones.append(punto_en_ruta(distancia_parada + desplazamiento))
    return posiciones


def redibujar(canvas, simulador):
    """
    Borra los buses que estaban dibujados y los vuelve a dibujar con el
    estado actual del Simulador; también actualiza el minuto.

    Cada sprite de bus se crea con la etiqueta (tag) "bus". Así,
    canvas.delete("bus") borra SOLO los buses y deja el fondo y las marcas.
    """
    estado = simulador.estado()

    canvas.delete("bus")
    for x, y, direccion in posiciones_buses(estado["buses"]):
        # anchor="center": el centro del sprite queda en (x, y)
        canvas.create_image(x, y, image=sprites_bus[direccion],
                            anchor="center", tags="bus")

    canvas.itemconfigure("texto_minuto", text=f"Minuto: {estado['minuto']}")


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
    )

    # Un solo Canvas para todo: fondo, marcas y buses.
    canvas = tk.Canvas(ventana, width=ANCHO, height=ALTO, highlightthickness=0)
    canvas.pack()

    # anchor="nw": la esquina superior izquierda de la imagen va en (0, 0)
    canvas.create_image(0, 0, image=cargar_fondo(), anchor="nw")
    if MOSTRAR_DEPURACION:
        dibujar_depuracion(canvas)
    dibujar_paradas(canvas)   # Después, para que quede encima de la depuración
    crear_marcador_minuto(canvas)

    cargar_sprites()
    redibujar(canvas, simulador)

    # TEMPORAL (solo fase 2a): botón para avanzar un tick a mano y comprobar
    # que los buses saltan a la parada correcta. Se reemplaza en la fase 2b
    # por la animación con ventana.after().
    def avanzar_un_tick():
        simulador.avanzar_tick()
        redibujar(canvas, simulador)

    boton_tick = tk.Button(ventana, text="Avanzar tick", command=avanzar_un_tick)
    boton_tick.pack(pady=4)

    ventana.mainloop()


if __name__ == "__main__":
    main()
