# Supuestos del modelo y datos pendientes — Fase 2

> Lista viva de cada dato real que falta y de cada supuesto del modelo, con su valor provisional.
> **Regla: no hay cifras inventadas.** Lo que no tiene fuente queda como `pendiente` y se marca
> como **PLACEHOLDER**. Los datos reales de TransMilenio los investiga y define el **equipo en la
> etapa 3**. Cuando un valor se confirme, se actualiza su fila con la fuente (en formato IEEE en
> el documento de entrega) y la fecha.

Última actualización: 28-nov-2026 (etapa 2, con los usos del AVL, el montículo y el árbol de
segmentos cerrados).

## 1. Datos reales de la ruta (los investiga el equipo)

| # | Dato | Valor provisional | Fuente | Quién lo define | Etapa |
|---|---|---|---|---|---|
| D1 | Confirmar que existe el servicio directo B28/F28 Portal Américas ↔ Portal Norte | Se asume que existe (**PLACEHOLDER**) | pendiente (TransMilenio S.A.) | Equipo | 3 |
| D2 | Lista oficial de estaciones del servicio, en orden, por sentido | **PLACEHOLDER**: sin lista; mientras tanto, paradas con id numérico | pendiente | Equipo | 3 |
| D3 | Coordenadas (latitud, longitud) de cada estación | **PLACEHOLDER**: sin coordenadas | pendiente (GeoJSON de estaciones troncales de datos abiertos de Bogotá, 2023, sin licencia declarada: citar y verificar a mano) | Equipo | 3 |
| D4 | Tiempo de cada tramo entre andenes consecutivos (segundos) | **PLACEHOLDER**: sin valor | pendiente (o se calcula con D3 y S1) | Equipo | 3 |
| D5 | Demanda por estación y franja horaria (tasa de llegada propia de cada andén) | **PLACEHOLDER**: sin valor; hoy hay una sola tasa global de la Fase 1 | pendiente (por ejemplo, validaciones por estación y franja en datos abiertos de TransMilenio) | Equipo | 3 |
| D6 | Franjas de hora pico y su multiplicador de demanda | **PLACEHOLDER**: sin valor | pendiente | Equipo | 3 |
| D7 | Hipótesis: en la mañana la demanda fuerte va de Américas hacia el norte y en la tarde se invierte | **Sin verificar**: no se da por cierta | pendiente (sale de D5) | Equipo | 3 |
| D8 | Capacidad del bus (¿articulado o biarticulado?) | **PLACEHOLDER**: hoy 10 (valor de la Fase 1, no es real) | pendiente | Equipo | 3 |

## 2. Supuestos y parámetros del modelo (decisiones del equipo)

| # | Supuesto o parámetro | Valor provisional | Fuente | Quién lo define | Etapa |
|---|---|---|---|---|---|
| S1 | Velocidad comercial supuesta (si D4 se calcula como distancia / velocidad) | **PLACEHOLDER**: sin valor | pendiente | Equipo | 3 |
| S2 | Hora del día en que empieza la simulación | **PLACEHOLDER**: sin valor | Decisión del modelo | Equipo | 3 |
| S3 | `SEGUNDOS_POR_TICK` (duración de un tick) | **PLACEHOLDER**: se fija cuando existan los tiempos reales (D4); 30 s fue solo un ejemplo | Decisión del modelo (opción A2 aprobada) | Equipo | 3 |
| S4 | Tope de flota (máximo de buses que puede haber con los despachos) | **PLACEHOLDER**: sin valor | Decisión del modelo | Equipo | 3 |
| S5 | `UMBRAL_SATURACION`: un andén está saturado si `esperando / capacidad_bus >= umbral` | 1.0 (provisional: hay más gente esperando de la que cabe en un bus vacío). **Condiciones de las que depende el árbol de segmentos:** (a) `UMBRAL_SATURACION > 0`; (b) nunca existe una alerta vigente con severidad publicada menor que el umbral (si baja del umbral, el andén sale de saturación y su hoja vuelve a `(0.0, i, 0)`). Se cubre con una prueba: con alertas generadas al azar, ninguna hoja vigente queda por debajo del umbral. **Si el equipo cambia el umbral, revisar S5** | Supuesto del modelo | Equipo | 3 |
| S6 | `CAMBIO_MINIMO`: cambio relativo de severidad (subiendo o bajando) para publicar una alerta nueva | 0.20 (20 %) | Supuesto del modelo | Equipo | 3 |
| S7 | Fórmula de severidad | `esperando / capacidad_bus` | Supuesto del modelo | Equipo | 3 |
| S8 | El bus despachado viaja **expreso y vacío** desde el portal hasta el andén saturado | Sí | Supuesto del modelo (no se afirma que TransMilenio lo haga sin una fuente) | Equipo | 3 |
| S9 | Permanencia en estación (tiempo que el bus se queda en el andén) | 0 ticks (la permanencia según la carga es un extra de la fase final) | Supuesto del modelo | Equipo | 3 |
| S10 | Probabilidad de pasajero prioritario (global, igual para todas las paradas) | 0.5 (valor de la Fase 1, no es real) | pendiente | Equipo | 3 |
| S11 | Trazado del tramo en el mapa | Línea recta entre estaciones consecutivas (seguir el corredor real es un extra) | Decisión del modelo | Equipo / IA en la web | 5 |
| S12 | Tasa de llegada en los andenes de **llegada** de cada portal (fin de un sentido, donde solo se baja la gente) | 0. Por eso esos andenes nunca alertan: es **consecuencia de este supuesto**, no un hecho del dominio. Se cubre con una prueba que lo verifique | Supuesto del modelo | Equipo | 3 |
| S13 | Destino de cada pasajero | Aguas abajo en su mismo sentido, hasta el portal de llegada (nadie "da la vuelta" dentro del bus). Decidido el 28-nov en `contexto_fase2.md` §3.3.1; **se implementa en la etapa 3** | Decisión del modelo | Equipo | 3 |
