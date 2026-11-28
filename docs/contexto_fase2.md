# Contexto del proyecto — Fase 2: Simulador de TransMilenio (ruta Portal Américas ↔ Portal Norte)

> Documento para que el asistente (Claude Code) y el equipo compartan el mismo contexto.
> Equipo: Pablo José Cárdenas, Nicolás Moreno Parra y Santiago Rodríguez Ortega.
> Curso: Estructuras de Datos. **Entrega: fecha aún no fija** (se había aplazado al sábado
> 28-nov-2026; el 27-nov Nicolás indicó que no es definitiva). Se avanza etapa por etapa (§9).

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

- Un único servicio, el **FB28**: se llama **B28** cuando va de Portal Américas a Portal Norte y
  **F28** cuando va hacia Portal Américas.
- Se sigue modelando como **ruta circular** (ida + vuelta = un ciclo), por eso se conserva la
  `ColaCircular` de la Fase 1.

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
Estado al 27-nov: **montículo (mínimos y máximos), AVL y árbol de segmentos ya implementados**
como TDA (etapa 1). Su **uso está en discusión** (etapa 2); la tabla es solo la propuesta inicial
y la decide el equipo:

| Estructura | Necesidad que cubre | Prioridad |
|---|---|---|
| Árbol de segmentos | Consultas por rango sobre la ruta (pasajeros esperando o máxima ocupación entre dos estaciones), con actualización puntual | Núcleo |
| Montículo (heap) | Cola de eventos por tiempo y ranking de estaciones más saturadas | Núcleo |
| Árbol balanceado (AVL) | Índice ordenado de estaciones (por nombre o kilómetro) y búsqueda por rango | Núcleo |
| Árbol B+ | Histórico de viajes por rango de tiempo | Extra (se recorta primero) |

Grafos: no se han visto en clase; se dejan para una fase posterior (transbordos y camino mínimo).

## 4. Arquitectura objetivo (3 capas, nomenclatura de Nicolás)

```
CAPA 1 — Núcleo abstracto (Python puro, sin web)
  estructuras/   nodo, pila, cola, arreglo, montículo, AVL, árbol de segmentos... (genéricas)
  simulador/     entidades del dominio (Pasajero, Parada/Estación, Bus) y el Simulador
                 -> archivo clave: simulador/simulador.py
CAPA 2 — API (api/)
  FastAPI. "Puertas" GET y POST (no es un CRUD) que traducen peticiones a llamadas del Simulador
CAPA 3 — Interfaz web (web/)
  index.html, css/, js/: mapa de la ciudad, buses animados, panel de control

datos/    JSON de la ruta (estaciones, coordenadas, sentido)
tests/    pytest para las capas 1 y 2 (Playwright por evaluar para la capa 3)
docs/     Documentación en Markdown
legacy/   app.py de Tkinter (Fase 1, se conserva sin editar)
```

Dentro de la capa 1 se mantiene la separación: `estructuras/` no sabe de buses ni pasajeros, y
`simulador/` las usa. (Documentos anteriores hablaban de "4 capas": es la misma arquitectura,
contando `estructuras/` y `simulador/` por separado.)

Reglas:
1. **Cada capa solo conoce la de abajo.**
2. **La API no tiene lógica de negocio.** Cada endpoint llama a un método del `Simulador` y
   devuelve su resultado. Si aparece un `if` de negocio en `api/`, está en el lugar equivocado.
3. **Un único `Simulador` en memoria** en el servidor.
4. **El navegador manda el reloj:** el front llama a `POST /api/avanzar` periódicamente.
5. **La animación es del front:** JS interpola la posición del bus entre el estado anterior y el
   nuevo (equivale al `animar_cuadro()` actual). No se usan WebSockets.
6. **Un solo comando para ejecutar:** FastAPI sirve también la carpeta `web/` (evita CORS y dos servidores).
7. `estructuras/` sin dependencias de dominio (no sabe de buses ni pasajeros).

### Endpoints (todos con prefijo `/api/`; ya hechos: estado, reporte, avanzar, pausar, reanudar, agregar-bus, deshacer)
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

## 9. Plan de trabajo: 5 etapas (definido por Nicolás el 27-nov)

Se agota cada etapa antes de pasar a la siguiente. En **cada** etapa se hacen las pruebas con
pytest de las capas 1 y 2; para la capa 3 se evalúa Playwright.

| Etapa | Qué | Capa | Quién | Estado |
|---|---|---|---|---|
| 1 | Implementar de cero, como TDA y con lo visto en clase, cada estructura nueva (montículo, AVL, árbol de segmentos) | 1 | Equipo (IA revisa y prueba) | Lista; ajustes menores si una decisión posterior lo pide |
| 2 | Definir el uso y la aplicación de cada estructura nueva, con justificación, **sin quitar** ninguna estructura lineal de la Fase 1 | 1 | Equipo; la IA opina cuando se le pida | **En curso** |
| 3 | Implementar ese uso en `simulador/`; el cambio principal se refleja en `simulador.py` | 1 | Equipo / Nicolás en `simulador.py` (IA guía y revisa) | Pendiente |
| 4 | Configurar la API: todos los GET y POST del alcance, endpoints y enrutamiento | 2 | Nicolás con guía de la IA | Parcial (A1 y A2 hechos con la Fase 1 del simulador) |
| 5 | Interfaz web profesional (HTML, CSS, JS), ajustando el alcance a lo que el equipo imagina | 3 | IA en gran parte, con el equipo | Pendiente (solo esqueleto) |

El cronograma anterior por "Bloques" (17–28 nov) queda como historia en `plan_preparacion.md`.

**Orden de recortes si falta tiempo:** pulido visual y gráficas → funciones extra de la interfaz.
Nunca se sustituye una estructura por una librería.

## 10. Preguntas abiertas

1. ¿Para qué se usa cada estructura nueva y con qué justificación? (etapa 2)
2. ¿Existe servicio directo Portal Américas–Portal Norte y cuáles son sus estaciones?
3. ¿Qué sistema operativo usa cada integrante? (afecta los comandos del paso a paso)
4. ¿Se conserva `app.py` en `legacy/` o se elimina al final?