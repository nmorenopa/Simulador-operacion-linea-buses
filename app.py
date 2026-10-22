"""
Interfaz gráfica del simulador de buses (Tkinter).

FASE 1b: dibuja el fondo y, encima, las 32 celdas de la ruta con su número,
las 7 paradas sobre su celda y las esquinas de la vía, para comprobar a ojo
que la grid coincide con el dibujo. Todavía no hay buses ni simulación.
"""
import tkinter as tk
from pathlib import Path

from PIL import Image, ImageTk


# ---------------------------------------------------------------
# Rutas de archivos
# ---------------------------------------------------------------
# Path(__file__) es la ubicación de este archivo (app.py). Si armamos las
# rutas a partir de ahí, el programa encuentra las imágenes sin importar
# desde qué carpeta se ejecute.
CARPETA_PROYECTO = Path(__file__).resolve().parent
CARPETA_IMAGENES = CARPETA_PROYECTO / "imagenes"
RUTA_FONDO = CARPETA_IMAGENES / "FONDO.png"


# ---------------------------------------------------------------
# Constantes de la interfaz
# ---------------------------------------------------------------
# Si es True se dibujan las marcas de depuración (celdas, paradas, esquinas).
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

# El fondo tiene 7 letreros de parada, así que la simulación usa 7 paradas.
NUMERO_PARADAS = 7

# Cada parada es el ÍNDICE de su celda dentro de RUTA, en el orden de la ruta.
# La posición i de esta lista es la parada con id i del Simulador.
# La celda elegida es la que deja el letrero al frente del bus (según su
# sentido de marcha).
#
# LIMITACIÓN: el espaciado es desigual porque así están los letreros en el
# fondo actual. Separaciones en celdas: 5, 11, 4, 3, 5, 2, 2 (suman 32).
# Si se aprueba un fondo con letreros a igual distancia (FONDO_grid.png),
# basta con cambiar esta lista (y NUMERO_PARADAS si cambia la cantidad).
PARADAS = [
    1,    # P1: celda (3, 2),  arriba
    6,    # P2: celda (8, 2),  arriba
    17,   # P3: celda (11, 8), abajo
    21,   # P4: celda (7, 8),  abajo
    24,   # P5: celda (4, 8),  abajo
    29,   # P6: celda (2, 5),  izquierda
    31,   # P7: celda (2, 3),  izquierda
]

# Esquinas del circuito (solo para depuración), en sentido horario.
ESQUINAS = [
    (12, 2),   # E1: arriba a la derecha   -> píxel (750, 150)
    (12, 8),   # E2: abajo a la derecha    -> píxel (750, 510)
    (2, 8),    # E3: abajo a la izquierda  -> píxel (150, 510)
    (2, 2),    # E4: arriba a la izquierda -> píxel (150, 150)
]


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


def dibujar_depuracion(canvas):
    """
    Dibuja encima del fondo:
      - el borde de cada una de las 32 celdas de la ruta, con su índice;
      - la celda de cada parada resaltada, con su nombre (P1..P7);
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

    # Paradas: borde rojo grueso sobre su celda y el nombre en el centro
    for numero, indice in enumerate(PARADAS):
        columna, fila = RUTA[indice]
        x1 = columna * TAM_CELDA
        y1 = fila * TAM_CELDA
        canvas.create_rectangle(x1 + 2, y1 + 2, x1 + TAM_CELDA - 2, y1 + TAM_CELDA - 2,
                                outline="red", width=3)
        x, y = centro_celda(columna, fila)
        dibujar_etiqueta(canvas, x, y, f"P{numero + 1}", "red")

    # Esquinas: cuadrito azul en el centro de la celda y el nombre un poco más abajo
    radio = 4
    for numero, (columna, fila) in enumerate(ESQUINAS):
        x, y = centro_celda(columna, fila)
        canvas.create_rectangle(x - radio, y - radio, x + radio, y + radio,
                                fill="blue", outline="white")
        dibujar_etiqueta(canvas, x, y + 14, f"E{numero + 1}", "blue")


def main():
    """Crea la ventana y el Canvas con el fondo (y las marcas de depuración)."""
    ventana = tk.Tk()
    ventana.title("Simulador de buses")
    ventana.resizable(False, False)

    # Un solo Canvas para todo: fondo, marcas y (más adelante) los buses.
    canvas = tk.Canvas(ventana, width=ANCHO, height=ALTO, highlightthickness=0)
    canvas.pack()

    # anchor="nw": la esquina superior izquierda de la imagen va en (0, 0)
    canvas.create_image(0, 0, image=cargar_fondo(), anchor="nw")
    if MOSTRAR_DEPURACION:
        dibujar_depuracion(canvas)

    ventana.mainloop()


if __name__ == "__main__":
    main()
