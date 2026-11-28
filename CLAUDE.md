# Instrucciones para el asistente (Claude Code)

- Proyecto de Estructuras de Datos. Los estudiantes deben poder explicar TODO el código en la sustentación.
- Contexto completo de la Fase 2 (TransMilenio, ruta FB28, Portal Américas ↔ Portal Norte): `docs/contexto_fase2.md`.
- Responde en español, claro y cercano. Explica cada término nuevo la primera vez.
- Trabaja por piezas pequeñas y pide confirmación antes de pasar a la siguiente.
- Comenta el código en español, de forma didáctica.
- Cada vez que escribas o cambies un archivo, anótalo en `docs/registro_uso_ia.md` (fecha, archivo, qué hiciste).

## Plan de trabajo de la Fase 2 (nomenclatura de Nicolás)
"Fase 2" = la segunda entrega del curso. Dentro de ella hay 5 **etapas**, en orden, y no se salta
a la siguiente sin agotar la actual. Detalle y estado en `docs/contexto_fase2.md` §9.
1. **Estructuras como TDA**, de cero, con lo visto en clase (montículo, AVL, árbol de segmentos). Lista;
   solo ajustes menores cuando una decisión de la etapa 2 o 3 lo pida.
2. **Uso y aplicación** de cada estructura nueva, con justificación clara, sin quitar ninguna
   estructura lineal de la Fase 1. ← **estamos aquí**. La IA opina solo cuando Nicolás lo pida.
3. **Implementar ese uso** en `simulador/` (el cambio principal se ve en `simulador.py`).
4. **API completa**: todos los GET y POST que pida el alcance, enrutamiento listo.
5. **Interfaz web** profesional (HTML + CSS + JS). Aquí la IA hace la mayor parte, ajustando el
   alcance con las ideas del equipo.
- En cada etapa: pruebas con pytest para las capas 1 y 2; para la capa 3, evaluar Playwright.

## Quién escribe qué
- `estructuras/` y `simulador/` los implementa el EQUIPO. El asistente NO los escribe: da pistas,
  analogías, pseudocódigo y pruebas sugeridas, y revisa. Las correcciones las propone y solo las
  aplica con el visto bueno del equipo.
- Nunca sustituir una estructura propia por una librería (`heapq`, `bisect`, `sortedcontainers`, `networkx`…).
- `simulador/simulador.py` y los endpoints de `api/` solo los toca Nicolás (con ayuda del asistente).

## Arquitectura: 3 capas (cada capa solo conoce la de abajo)
- **Capa 1 — Núcleo abstracto** (`estructuras/` + `simulador/`, archivo clave `simulador/simulador.py`):
  estructuras, entidades del dominio y el `Simulador`. Por dentro, `estructuras/` no sabe nada de
  buses ni pasajeros; `simulador/` usa las estructuras.
- **Capa 2 — API** (`api/`): las "puertas" que usa la web. Solo GET (consultar) y POST (ordenar);
  no es un CRUD. NO tiene lógica de negocio: cada endpoint llama a un método del `Simulador` y
  devuelve su resultado. Endpoints con prefijo `/api/`. Un único `Simulador` en memoria.
- **Capa 3 — Interfaz web** (`web/`): materializa la capa 1 en un mapa animado. HTML + CSS +
  JavaScript plano (módulos ES), sin React ni compilación. El JS solo dibuja y manda órdenes; la
  animación es del JS con `requestAnimationFrame`, sin bloquear la página.
  El navegador manda el reloj llamando a `POST /api/avanzar`. Sin WebSockets.
- Para escribir texto recibido de la API en la página, usar `textContent`, no `innerHTML`.
- Se arranca con `fastapi dev` (lee `pyproject.toml`); FastAPI sirve también la carpeta `web/`.
  El `app.mount("/", ...)` va siempre al final de `api/main.py`.
- No inventar APIs ni funciones de librerías: verificar en la documentación oficial y, si hay duda, decirlo.

## Versión anterior (`legacy/`)
- `legacy/app.py` es la interfaz Tkinter de la Fase 1. Se conserva funcionando y no se edita.
  Se abre con `python -m legacy.app` (necesita Pillow, instalado aparte).
