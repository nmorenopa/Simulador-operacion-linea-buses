# Contexto del proyecto — Fase 2: Simulador de TransMilenio (ruta Portal Américas ↔ Portal Norte)

> Documento para que el asistente (Claude Code) y el equipo compartan el mismo contexto.
> Equipo: Pablo José Cárdenas, Nicolás Moreno Parra y Santiago Rodríguez Ortega.
> Curso: Estructuras de Datos. **Entrega: jueves 26 de noviembre de 2026.**

## 1. Objetivo del curso (lo que realmente importa)

El objetivo es **aprender y poder defender oralmente** cómo funcionan las estructuras de datos y
cuándo aplicarlas. El simulador es el vehículo, no el fin. Prioridad en este orden:

1. Que las estructuras nuevas estén implementadas **a mano por el equipo**.
2. Que todo funcione junto.
3. Que se vea profesional.

Si falta tiempo, se recorta primero lo visual, luego las estructuras extra. Nunca se reemplaza
una estructura por una librería.

## 2. Estado de partida (Fase 1, commit `80003fb`)

Simulador de una línea circular de 8 paradas con interfaz Tkinter. Ya existen, hechas por el equipo:

| Estructura | Uso actual |
|---|---|
| `Nodo` | Pieza base de las listas enlazadas |
| `ArregloDinamico` (crece ×1.618) | Flota, paradas, pasajeros a bordo, series de estadísticas |
| `Pila` | Historial para deshacer |
| `Cola` | Pasajeros en cada nivel de prioridad; operaciones pendientes de la interfaz |
| `ColaCircular` | Ruta de cada bus (rotar = avanzar a la siguiente parada) |
| `ColaPrioridad` (arreglo de colas) | Orden de abordaje en cada parada |

Arquitectura actual por capas: `estructuras/` → `simulador/` → `app.py` (Tkinter).
Hay 132 pruebas pytest que cubren las capas 1 y 2. La documentación completa del estado
anterior está en `docs/descripcion.md`.

## 3. Nuevo rumbo (Fase 2)

### 3.1 Qué se hace
Escalar el simulador a **una sola ruta de TransMilenio: Portal Américas ↔ Portal Norte**
(ida y vuelta), con **interfaz web** que dibuje el mapa de Bogotá.

### 3.2 Decisiones del grupo
1. **Sistema:** TransMilenio, por los problemas logísticos que el equipo conoce como residentes.
2. **Ruta piloto:** Portal Américas ↔ Portal Norte. Conecta el occidente con el norte, y hay
   evidencia de congestión en el Portal Américas y de afectaciones en la Autopista Norte.
   Se eligió portal a portal (y no una troncal) porque origen y destino están bien definidos;
   algunas troncales inician en estaciones compartidas donde los buses ya llegan con pasajeros.
3. **Interfaz web** (HTML, CSS y JavaScript) en lugar de Tkinter: permite un mapa real con zoom
   y una presentación más profesional. La lógica en Python ya está separada de la interfaz.
4. **Datos oficiales:** se guiarán por la información publicada por TransMilenio S.A. (entidad
   gestora, no dueña de los buses; los operan concesionarios) y por los datos abiertos de Bogotá.
   Lo que falte se estima y se declara como **supuesto del modelo**.

### 3.3 Alcance
- Una ruta lineal con dos sentidos. **Sin transbordos.**
- Estaciones reales sacadas de datos abiertos (GeoJSON de estaciones troncales, datos de 2023,
  sin licencia declarada: se cita como fuente y se verifica a mano).
- **Por confirmar:** que exista servicio directo Américas–Norte y qué estaciones recorre.
  La lista de estaciones se revisa manualmente y se guarda en `datos/`.
- Modelo de la ruta: `ColaCircular` de 2N posiciones (estaciones de ida y luego las de vuelta
  en orden inverso), de modo que avanzar siga siendo rotar.
- **Fuera de alcance (por ahora):** varias troncales, transbordos, grafos, rutas de alimentación.

### 3.4 Estructuras nuevas (implementadas por el equipo)
Propuesta, **pendiente de confirmar** con el equipo:

| Estructura | Necesidad que cubre | Prioridad |
|---|---|---|
| Árbol de segmentos | Consultas por rango sobre la ruta (pasajeros esperando o máxima ocupación entre dos estaciones), con actualización puntual | Núcleo |
| Montículo (heap) | Cola de eventos por tiempo y ranking de estaciones más saturadas | Núcleo |
| Árbol balanceado (AVL) | Índice ordenado de estaciones (por nombre o kilómetro) y búsqueda por rango | Núcleo |
| Árbol B+ | Histórico de viajes por rango de tiempo | Extra (se recorta primero) |

Grafos: no se han visto en clase; se dejan para una fase posterior (transbordos y camino mínimo).

## 4. Arquitectura objetivo (4 capas)

```
estructuras/   Capa 1: nodo, pila, cola, heap, AVL, árbol de segmentos... (genéricas)
simulador/     Capa 2: Pasajero, Estacion, Bus, Simulador (sin web, sin dibujo)
api/           Capa 3: FastAPI. Solo traduce peticiones a llamadas del Simulador
web/           Capa 4: index.html, css/, js/ (mapa, animación, panel de control)
datos/         JSON de la ruta (estaciones, coordenadas, sentido)
tests/         pytest para capas 1 y 2 (y pruebas simples de la API)
docs/          Documentación en Markdown
legacy/        app.py de Tkinter (se conserva hasta que la web funcione, luego se retira)
```

Reglas:
1. **Cada capa solo conoce la de abajo.**
2. **La API no tiene lógica de negocio.** Cada endpoint llama a un método del `Simulador` y
   devuelve su resultado. Si aparece un `if` de negocio en `api/`, está en el lugar equivocado.
3. **Un único `Simulador` en memoria** en el servidor.
4. **El navegador manda el reloj:** el front llama a `POST /avanzar` periódicamente.
5. **La animación es del front:** JS interpola la posición del bus entre el estado anterior y el
   nuevo (equivale al `animar_cuadro()` actual). No se usan WebSockets.
6. **Un solo comando para ejecutar:** FastAPI sirve también la carpeta `web/` (evita CORS y dos servidores).
7. Capa 1 sin dependencias de dominio (no sabe de buses ni pasajeros).

### Endpoints previstos (nombres tentativos, en español)
| Método y ruta | Llama a |
|---|---|
| `GET /estado` | `Simulador.estado()` |
| `GET /reporte` | `Simulador.reporte()` |
| `POST /avanzar` | `Simulador.avanzar_tick()` y devuelve el estado |
| `POST /pausar`, `POST /reanudar` | `pausar()`, `reanudar()` |
| `POST /agregar-bus` | `agregar_bus()` |
| `POST /deshacer` | `deshacer()` |
| `POST /reiniciar` | Crea un `Simulador` nuevo con los parámetros recibidos |

## 5. Tecnología

| Parte | Decisión | Motivo |
|---|---|---|
| Lenguaje del motor | Python 3.10+ | Ya lo dominan |
| API | **FastAPI + Uvicorn** | Los diccionarios de `estado()` y `reporte()` pasan a JSON casi sin trabajo |
| Frontend | **HTML + CSS + JavaScript plano** (módulos ES), **sin React** | Sin Node ni compilación; React no aporta a la materia |
| Mapa | Leaflet por CDN (necesita internet) | Zoom y desplazamiento ya resueltos. Revisar la política de uso de los mosaicos de OpenStreetMap |
| Pruebas | pytest | Ya existe |
| Se retira | Pillow | Era para los sprites de Tkinter |

Las versiones exactas de dependencias se fijan **después** de instalarlas (`pip freeze`) y se
verifican en la documentación oficial. No inventar APIs ni funciones: si hay duda, consultar.

## 6. Reglas de trabajo con el asistente de IA

### Qué SÍ hace el asistente (decisión del grupo para esta fase)
- Configurar el proyecto: carpetas, `requirements.txt`, `.gitignore`, README y paso a paso de instalación.
- Montar la **API FastAPI** (explicándola, porque el equipo quiere aprender a configurarla).
- Construir el **frontend** (HTML, CSS, JS): mapa, animación, panel de control, gráficas.
- Ayudar a **integrar** las piezas y a depurar.
- Revisar el código del equipo: errores, casos borde, complejidad (Big O), mejoras.
- Redactar con el equipo la documentación de cada pieza.

### Qué NO hace
- **No implementa las estructuras de datos** (`estructuras/`): las escribe el equipo. El asistente
  puede dar analogías, pistas, pseudocódigo y pruebas sugeridas, y revisar lo que el equipo escriba.
- No usa librerías para sustituir estructuras (`heapq`, `bisect`, `sortedcontainers`, `networkx`, etc.)
  como estructura de fondo. Las librerías sirven para interfaz, aleatoriedad, archivos y pruebas,
  y como apoyo para **validar** las estructuras propias.
- No reescribe el proyecto de una vez: trabaja por piezas pequeñas que el equipo entienda.
- No toma decisiones de alcance sin preguntar. Primero propone el plan y espera aprobación.

### Estilo
- Responder en español, claro y cercano. Explicar cada término nuevo la primera vez.
- Primero la idea (con analogía), luego pistas; el código completo solo cuando se pida,
  comentado línea por línea.
- Si algo excede lo visto en clase, proponer la versión simple y mencionar la avanzada como nota.
- Si una solución es insegura o dudosa, decirlo. Si no se sabe, decirlo.

## 7. Convenciones de código

- Python 3, clases y métodos **en español**, coherentes con lo ya existente.
- Cada estructura con **docstrings**, y cada método indicando su **complejidad**.
- La lógica del simulador **separada de la interfaz**, para probarla sin servidor ni navegador.
- Sin lógica en la API ni en el JS: el JS solo dibuja y manda órdenes.
- Comentarios en el JS y la API pensados para aprender (qué hace cada bloque y por qué).

## 8. Documentación y entregables

Todo en Markdown dentro de `docs/`:
- `explicacion_estructuras.md`: por qué y cómo se usó cada estructura, con su complejidad.
- `manual_usuario.md`: actualizado a la versión web.
- `registro_uso_ia.md`: **mantener al día** qué generó la IA y qué hizo el equipo, para calcular
  el porcentaje final. Corregir ahí cualquier descripción que ya no corresponda.
- `descripcion.md`: actualizar al terminar la fase.
- Documento de entrega de la fase (decisiones, fuentes en formato IEEE, interacciones con IA).
- Repositorio en GitHub con README claro, video de máximo 5 minutos y sustentación oral.

Pendientes de documentación detectados en la Fase 1 (aún sin resolver): `explicacion_estructuras.md`
dice "duplica" donde el código usa factor áureo; docstring de `bajar_en` dice O(n²) y es O(n);
`manual_usuario.md` menciona 20 % de prioritarios y el código usa 50 %; `.gitignore` tiene una línea
`.venv/.DS_Store` que probablemente son dos.

## 9. Cronograma (9 días: 17 al 26 de noviembre)

| Bloque | Qué | Quién guía |
|---|---|---|
| 1 | Entorno y esqueleto: estructura de carpetas, dependencias, "hola mundo" de API + página que la llame | Asistente |
| 2 | Datos de la ruta en `datos/` y `Simulador` adaptado a estaciones reales | Equipo (revisión del asistente) |
| 3 | **Estructuras núcleo** (segmentos, heap, AVL) con pruebas | **Equipo** |
| 4 | API completa y mapa web con buses animados | Asistente |
| 5 | Integrar las estructuras en el simulador y en el panel | Conjunto |
| 6 | Documentación, registro de IA, video, ensayo de sustentación | Equipo |

**Orden de recortes si falta tiempo:** pulido visual y gráficas → B+ → una de las estructuras
núcleo → funciones extra de la interfaz. Nunca se sustituye una estructura por una librería.

## 10. Preguntas abiertas

1. ¿Cuáles estructuras núcleo se confirman? (propuesta: segmentos, heap, AVL)
2. ¿Existe servicio directo Portal Américas–Portal Norte y cuáles son sus estaciones?
3. ¿Qué sistema operativo usa cada integrante? (afecta los comandos del paso a paso)
4. ¿Se conserva `app.py` en `legacy/` o se elimina al final?