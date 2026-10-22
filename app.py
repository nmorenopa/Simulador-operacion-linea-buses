import tkinter as tk
from PIL import Image, ImageTk

# Crear ventana
ventana = tk.Tk()
ventana.title("simulador de buses")
ventana.geometry("900x600")
ventana.resizable(False, False)

# Cargar imagen con la misma resolución de la ventana
imagen = Image.open("imagenes/fondo.png")
imagen = imagen.resize((900, 600))
fondo = ImageTk.PhotoImage(imagen)

# Colocar imagen como fondo
etiqueta_fondo = tk.Label(ventana, image=fondo)
etiqueta_fondo.place(x=0, y=0, relwidth=1, relheight=1)

ventana.mainloop()  