# 🚌 Simulador de operación de TransMilenio (Portal Américas ↔ Portal Norte)

Simulador de una ruta de TransMilenio, ida y vuelta, en el que cada parte del funcionamiento
(flota, estaciones, abordaje, historial, consultas) se resuelve con **estructuras de datos
implementadas a mano** por el equipo. Proyecto del curso **Estructuras de Datos**.

El motor está en Python; la interfaz es una página web servida por una API en FastAPI.

## Inicio rápido

```bash
py -3.14 -m venv .venv                      # macOS / Linux: python3 -m venv .venv
source .venv/Scripts/activate               # activar: ver la tabla en docs/instalacion.md
python -m pip install -r requirements.txt
python -m pytest
fastapi dev
```

Luego abrir **http://127.0.0.1:8000/** (y **http://127.0.0.1:8000/docs** para la API).

Paso a paso completo, para Windows, macOS y Linux: **[docs/instalacion.md](docs/instalacion.md)**.

## Estructura del proyecto

```
estructuras/   Capa 1: estructuras de datos genéricas (pila, colas, arreglo dinámico…)
simulador/     Capa 2: Pasajero, Parada, Bus, Simulador (sin web, sin dibujo)
api/           Capa 3: FastAPI. Solo traduce peticiones a llamadas del Simulador
web/           Capa 4: index.html, css/, js/ (lo que ve el navegador)
datos/         JSON de la ruta (estaciones, coordenadas, sentido)
tests/         Pruebas con pytest
docs/          Documentación
legacy/        Versión anterior con Tkinter (Fase 1)
```

Cada capa solo conoce la de abajo.

## Documentación

- [Instalación paso a paso](docs/instalacion.md)
- [Contexto de la Fase 2](docs/contexto_fase2.md)
- [Descripción técnica](docs/descripcion.md)
- [Explicación de las estructuras de datos](docs/explicacion_estructuras.md)
- [Manual de usuario](docs/manual_usuario.md)
- [Registro de uso de IA](docs/registro_uso_ia.md)

## Versión anterior (Tkinter)

```bash
python -m pip install pillow
python -m legacy.app
```

## Equipo

- Pablo José Cárdenas
- Nicolás Moreno Parra
- Santiago Rodríguez Ortega
