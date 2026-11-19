# Instrucciones para el asistente (Claude Code)

- Proyecto de Estructuras de Datos. Los estudiantes deben poder explicar TODO el código en la sustentación.
- Contexto completo de la Fase 2 (TransMilenio, Portal Américas ↔ Portal Norte): `docs/contexto_fase2.md`.
- Responde en español, claro y cercano. Explica cada término nuevo la primera vez.
- Trabaja por piezas pequeñas y pide confirmación antes de pasar a la siguiente.
- Comenta el código en español, de forma didáctica.
- Cada vez que escribas o cambies un archivo, anótalo en `docs/registro_uso_ia.md` (fecha, archivo, qué hiciste).

## Quién escribe qué
- `estructuras/` y `simulador/` los implementa el EQUIPO. El asistente NO los escribe: da pistas,
  analogías, pseudocódigo y pruebas sugeridas, y revisa. Las correcciones las propone y solo las
  aplica con el visto bueno del equipo.
- Nunca sustituir una estructura propia por una librería (`heapq`, `bisect`, `sortedcontainers`, `networkx`…).
- `simulador/simulador.py` y los endpoints de `api/` solo los toca Nicolás (con ayuda del asistente).

## Arquitectura (cada capa solo conoce la de abajo)
- `estructuras/` (capa 1, sin nada de buses ni pasajeros) → `simulador/` (capa 2) → `api/` (capa 3) → `web/` (capa 4).
- La API NO tiene lógica de negocio: cada endpoint llama a un método del `Simulador` y devuelve su
  resultado. Endpoints con prefijo `/api/`. Un único `Simulador` en memoria.
- La web es HTML + CSS + JavaScript plano (módulos ES), sin React ni compilación. El JS solo dibuja
  y manda órdenes; la animación es del JS con `requestAnimationFrame`, sin bloquear la página.
  El navegador manda el reloj llamando a `POST /api/avanzar`. Sin WebSockets.
- Para escribir texto recibido de la API en la página, usar `textContent`, no `innerHTML`.
- Se arranca con `fastapi dev` (lee `pyproject.toml`); FastAPI sirve también la carpeta `web/`.
  El `app.mount("/", ...)` va siempre al final de `api/main.py`.
- No inventar APIs ni funciones de librerías: verificar en la documentación oficial y, si hay duda, decirlo.

## Versión anterior (`legacy/`)
- `legacy/app.py` es la interfaz Tkinter de la Fase 1. Se conserva funcionando y no se edita.
  Se abre con `python -m legacy.app` (necesita Pillow, instalado aparte).
