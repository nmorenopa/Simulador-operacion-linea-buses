# Simulador de una línea de buses: explicación de las estructuras de datos

## 1. Las cinco estructuras

### 1.1 Arreglo dinámico

- **Idea:** lista de elementos en posiciones consecutivas (0, 1, 2, ...) que crece sola cuando se llena. Permite acceso por posición.
- **Dónde se usa:** pasajeros a bordo del bus.
- **Por qué esta estructura:** en cada parada baja *cualquiera* según su destino, no solo el primero ni el último. Una cola o una pila no lo permiten.
- **Funcionamiento interno:**
  - Tiene una capacidad (por ejemplo 20, como se ve en "3/20" sobre cada bus).
  - Al llenarse, **duplica su capacidad (×2)**: crea un arreglo más grande y copia todo.
  - Duplicar cuesta O(n), pero ocurre tan pocas veces que agregar sale **O(1) amortizado**.
  - `bajar_en` **recorre el arreglo al revés (n→0)**: si borrara de adelante hacia atrás, los demás se correrían y se saltaría a alguien.
- **Analogía:** los asientos de un bus.
- **Demo:** la ocupación sube y baja, bajan según su destino y sale cualquiera, no solo el primero.

### 1.2 Pila (LIFO)

- **Idea:** *Last In, First Out*. El último en entrar es el primero en salir; solo se opera por la cima.
- **Dónde se usa:** historial del operador para deshacer.
- **Por qué esta estructura:** solo se deshace lo último que se hizo.
- **Analogía:** una pila de platos.
- **Demo:** se agrega un bus y se pausa; al presionar "Deshacer" sale primero la pausa y luego el bus.

### 1.3 Cola (FIFO)

- **Idea:** *First In, First Out*. Se agrega por el final y se saca por el inicio.
- **Dónde se usa:** fila de cada parada.
- **Por qué esta estructura:** los pasajeros se atienden por orden de llegada.
- **Analogía:** la fila de un banco.
- **Demo:** la fila de una parada crece según llegan pasajeros.

### 1.4 Cola con prioridad

- **Idea:** cada elemento tiene una prioridad; sale primero el de mayor prioridad y, entre iguales, el que llegó antes.
- **Dónde se usa:** orden de abordaje.
- **Por qué esta estructura:** los pasajeros prioritarios suben antes que los demás.
- **Detalle:** si no caben todos en el bus, los que sobran vuelven a la fila.
- **Analogía:** la fila preferencial.
- **Demo:** llega un pasajero prioritario y sube antes que los demás.

### 1.4 Cola circular

- **Idea:** cola FIFO cuyo final se conecta con el inicio, formando un ciclo.
- **Dónde se usa:** ruta de cada bus (A → B → C → A ...). Cada bus tiene la suya.
- **Por qué esta estructura:** el recorrido se repite sin fin.
- **Demo:** al llegar a la última parada, la ruta vuelve a empezar.

---

## 2. Estructuras nuevas de la Fase 2

> Estado: decisión de la **etapa 2** (uso y justificación). La implementación en `simulador/`
> es de la etapa 3. Aquí solo va el AVL; los usos del montículo y del árbol de segmentos
> todavía no se han definido.

### 2.1 Árbol AVL: índice de esperas de los pasajeros que ya abordaron

#### (a) Idea y analogía

- **Árbol binario de búsqueda (ABB):** cada nodo tiene una clave; a su izquierda quedan las
  claves menores y a su derecha las mayores. Buscar es como adivinar un número con "más alto /
  más bajo": cada paso descarta una rama entera.
- **AVL:** un ABB que **se reequilibra solo**. En cada nodo, la altura de sus dos lados difiere a
  lo más en 1; si una inserción lo desbalancea, una **rotación** (reacomodo local de 2 o 3 nodos)
  lo arregla. Por eso su altura es siempre O(log n).
- **Analogía: un archivador que se reacomoda solo.** Cada carpeta nueva entra directo en su lugar
  según su etiqueta, y si un cajón queda muy cargado frente a otro, el archivador corre unas pocas
  carpetas para quedar parejo. Nunca hay que sacar todo y volver a ordenar, y siempre se puede
  pedir "desde la etiqueta X hasta la Y" y sacar justo esas carpetas.

#### (b) Qué guarda y con qué clave

- **Qué:** los pasajeros que **ya abordaron** un bus. Se insertan en el momento de abordar.
- **Clave:** la tupla `(tiempo_espera, id_pasajero)`, donde
  `tiempo_espera = minuto_abordaje - minuto_llegada` (ya existe: `Pasajero.tiempo_espera()`).
- **Valor:** la **referencia** al objeto `Pasajero` completo (origen, destino, prioridad,
  minuto de llegada y de abordaje), no una copia.
- **¿Por qué una clave compuesta?** Las esperas son enteros pequeños (0, 1, 2… minutos) y se
  repiten muchísimo. Con la espera sola, dos pasajeros con 5 minutos tendrían la misma clave y el
  segundo **reemplazaría** al primero (esa es la política del AVL ante claves repetidas). Al
  agregar el `id_pasajero`, que es único, ninguna clave se repite y el orden es **total y
  estricto**: primero por espera y, entre iguales, por id.
- **Cómo compara Python las tuplas:** posición por posición. Compara el primer componente y solo
  si son iguales mira el segundo. Así `(5, 12) < (5, 40) < (6, 3)`.
- **Dueño:** el `Simulador`. La `Parada` no conoce el árbol: `abordar()` devuelve un
  `ArregloDinamico` con los pasajeros que subieron y el `Simulador` los inserta. La clave se arma
  en un solo método privado, `_clave_espera(pasajero)`.

#### (c) ¿Por qué un AVL y no otra estructura?

El equipo eligió con **dos premisas**:

1. **Dinamismo:** un AVL **no** conviene si la colección es pequeña o estática (sin inserciones
   después de cargarse): ahí un arreglo ordenado con búsqueda binaria, o un hash si no hay rangos,
   rinde igual o mejor. El AVL conviene cuando el conjunto **crece durante la ejecución** y hay que
   mantener el orden para búsquedas o rangos frecuentes.
2. **Relevancia:** de nada sirve acelerar una consulta que no aporta al objetivo del simulador:
   apoyar decisiones logísticas contra los colapsos.

| Alternativa | ¿Por qué no? |
|---|---|
| Arreglo ordenado | Los pasajeros abordan con esperas **desordenadas** (uno con 2 min, luego otro con 9). Mantener el orden obliga a correr elementos en cada inserción: **O(n)**. Nuestro `ArregloDinamico.insertar` es O(1) justamente porque **no** conserva el orden (manda al final el elemento desplazado), así que no sirve aquí. |
| Hash (diccionario) | Encuentra una clave exacta, pero no responde "todos los que esperaron entre 15 y 30 minutos": no guarda orden. |
| Contador, variable o histograma | "Peor espera", "cuántos superan un umbral fijo" o la distribución por minuto se resuelven en O(1) con una variable, un contador o un arreglo indexado por minuto de espera. Pero **no devuelven los registros**: no dicen *quiénes* ni *dónde*, ni sirven para un umbral que el operador elige en el momento. |
| **AVL** | Inserta en **O(log n)** sin reordenar todo, mantiene el orden y devuelve los registros completos de cualquier rango. Cumple las dos premisas. |

Otros usos del AVL que el equipo evaluó y **descartó** con las mismas premisas:

- *Estaciones por (troncal, abscisa) o por nombre:* carga única y pocas decenas; un arreglo
  ordenado basta (salvo que en la Fase 3 se agreguen portales o rutas durante la simulación).
- *Pasajeros por (minuto_llegada, id), incidentes por minuto:* las claves solo crecen, así que
  `agregaralfinal` ya mantiene el orden.
- *Series por minuto:* el minuto ya es el índice del arreglo.
- *Pasajeros que siguen esperando, flota por ocupación:* exigirían **eliminar**, que no está implementado.

**Frase para la defensa:** *"Un contador responde preguntas fijas. El AVL mantiene ordenados los
registros completos de los pasajeros que ya abordaron y permite responder preguntas que el
operador define en el momento: con cualquier umbral, ver quiénes y dónde. Es un diccionario
ordenado dinámico: inserta en O(log n) sin reordenar todo, y su costo no crece linealmente si la
red se amplía."*

#### (d) Consultas que habilita y su complejidad

n = pasajeros que ya abordaron; k = cantidad de registros devueltos.

| Pregunta del operador | Operación | Complejidad |
|---|---|---|
| Registrar a quien acaba de abordar | `insertar((espera, id), pasajero)` | O(log n) |
| ¿Quiénes esperaron N minutos o más? | `rango((t, -inf), (inf, inf))`, con t = N pasado a ticks | O(log n + k) |
| ¿Quiénes esperaron entre N y M minutos? | `rango((t1, -inf), (t2, inf))`, con N y M pasados a ticks | O(log n + k) |
| ¿Cuál fue la peor espera? | `maximo()` | O(log n) |
| Todos, ordenados por espera | `en_orden()` | O(n) |

- **Límites del rango:** se arman en `_limites_espera(minimo)` con la constante
  `TOPE = float("inf")`: desde `(minimo, -inf)` hasta `(TOPE, TOPE)`. Funciona porque Python
  compara `int` con `float` sin problema y las tuplas se comparan posición por posición: toda
  clave `(espera, id)` con `espera >= minimo` queda entre los dos límites. Usar `-inf` en el límite
  inferior evita depender de que los id empiecen en 0.
- **Unidades (decisión A2, ver `contexto_fase2.md` §3.5):** el reloj avanza en **ticks** de
  `SEGUNDOS_POR_TICK` segundos, así que `tiempo_espera` y la clave del AVL quedan **en ticks**.
  Todo lo que ve el usuario va **en minutos**, y la conversión vive dentro del `Simulador`:
  `consultar_esperas` recibe `minimo` en minutos y lo pasa a ticks antes de armar el rango
  ("esperó al menos N minutos" equivale a "esperó al menos ⌈N·60 / SEGUNDOS_POR_TICK⌉ ticks",
  redondeando hacia arriba). La API no convierte nada.
  La equivalencia es **exacta**, no una aproximación: como la espera se mide en ticks enteros,
  `ticks · SPT ≥ N · 60` se cumple exactamente cuando `ticks ≥ ⌈N·60 / SPT⌉`. El techo se calcula
  solo con enteros, `(N*60 + SPT - 1) // SPT`, para no depender de la división con decimales.
- **Del árbol a la pantalla:** el `Simulador` ofrece `consultar_esperas(minimo, limite)`. Valida
  que `minimo` sea un entero ≥ 0 (si no, `ValueError`, que la API traduce a un error 4xx sin
  lógica de negocio) y devuelve diccionarios, con las esperas en minutos: un **resumen por andén** (`pasajero.origen`, es
  decir, estación + sentido) **y prioridad**, más hasta `limite` registros. Como `rango` entrega
  orden **ascendente**, para mostrar primero las peores esperas se invierte la lista y se recorta.
  El `limite` evita enviar miles de registros en el JSON.
- **Uso en el panel:** un control de umbral y una tabla o gráfica por andén que consultan un
  endpoint de solo lectura (por ejemplo, `GET /api/esperas?minimo=N`). El operador ve dónde se
  concentran las esperas largas, si sufren más los prioritarios o los normales, y puede comparar
  corridas con la misma semilla (por ejemplo, con y sin un bus despachado).

**Agregados al AVL el 28-nov** (`estructuras/arbol_balanceado.py`, escritos por la IA con el visto
bueno de Nicolás): `maximo()` (la necesita este uso), `minimo()` y `techo()`. Igual que `piso`,
devuelven la pareja `(clave, valor)`, o `None` si el árbol está vacío; los tres son O(log n).

#### (e) Mejora futura (solo nota, no se implementa)

Hoy **contar** cuántos superan un umbral con `rango` cuesta O(log n + k), porque arma la lista.
Si cada nodo guardara el **tamaño de su subárbol** (cuántos nodos tiene debajo, incluido él),
contar un rango y sacar percentiles (por ejemplo, la espera que no supera el 90 % de los
pasajeros) costaría O(log n). Es una técnica avanzada (árbol de estadísticos de orden) y queda
fuera del alcance.

#### (f) ¿Qué pasa en la Fase 3 (más portales, rutas y troncales)?

El AVL en sí no cambia. Lo que hay que decidir es **cómo se arma la clave**, y como eso vive solo
en `_clave_espera` y `_limites_espera`, el cambio queda **acotado a esos dos métodos**. Hay dos
opciones; la elección queda **pendiente para la Fase 3**:

1. **Ampliar la clave a `(id_ruta, espera, id)`.** Filtrar **una** ruta sigue siendo un solo
   rango. Pero "esperaron ≥ N en **todas** las rutas" deja de ser un rango contiguo, porque las
   claves quedan agrupadas primero por ruta: hay que hacer un rango por ruta y unir los
   resultados. Como son pocas rutas, es aceptable.
2. **Mantener la clave `(espera, id)`** y guardar `id_ruta` en el `Pasajero`. La consulta global
   sigue siendo un solo rango, y filtrar por ruta se hace recorriendo el resultado, O(k).

Hoy **no** se agrega `id_ruta` con un valor fijo: un primer componente que siempre vale lo mismo
no aporta nada y es difícil de defender.

#### (g) Limitaciones (dichas con honestidad)

1. **Solo vale si el panel lo usa en vivo.** La justificación por relevancia depende de que la web
   tenga el control de umbral y la tabla o gráfica por andén. Si las esperas solo se vieran al
   terminar la simulación, el argumento se debilita.
2. **Contar no es O(log n).** `rango` devuelve una lista: contar con él cuesta O(log n + k). Ver (e).
3. **El argumento es de escala, no de velocidad actual.** Con los parámetros de la Fase 1 (tasa
   0,5 y 3 intentos) llegan en promedio 1,5 pasajeros por parada y minuto; con unas 50 paradas son miles por hora simulada, y
   más en la Fase 3. A esta escala, recorrer una lista hoy también sería rápido. La ventaja del
   AVL es que su costo no crece linealmente cuando la red crece.
4. **No tiene eliminar** (limitación declarada del AVL del equipo). Ante una clave repetida
   reemplaza el valor, pero en este uso nunca ocurre porque la clave incluye el id.
5. **Solo están los que ya abordaron.** Los pasajeros que siguen esperando no están en el índice:
   una fila que lleva mucho tiempo sin bus no aparece hasta que sus pasajeros suben.
6. **Memoria.** Al guardar la referencia, cada pasajero sigue en memoria aunque ya se haya bajado
   del bus. Con la escala de esta fase es aceptable.
7. **Resuelto (28-nov):** el destino aleatorio podía caer en la misma estación pero en el sentido
   contrario, o hacer que el pasajero pasara por el portal y volviera. Se decidió elegir el
   destino solo entre los andenes que quedan adelante en el mismo sentido (`contexto_fase2.md` §3.3.1).
8. **Pendiente de `datos/`:** mientras no estén las estaciones reales, el resumen usa el id de la
   parada. Cuando estén, cada fila incluirá el nombre de la estación y el sentido (B28/F28), para
   que la web pueda sumar los dos sentidos si quiere.

### 2.2 Montículo de máximos: cola de atención del operador

> El motor por tiempos, el despacho y los ticks en los que se apoya este uso están en
> `contexto_fase2.md` §3.5. Los valores provisionales están en `supuestos_y_datos_pendientes.md`.

#### (a) Idea y analogía

- **Montículo (heap):** un árbol binario **casi completo** (se llena nivel por nivel, de izquierda
  a derecha) guardado en un arreglo: el padre de la posición i está en (i-1)//2 y sus hijos en
  2i+1 y 2i+2. En uno **de máximos**, cada padre es mayor o igual que sus hijos, así que la
  **raíz siempre es el elemento mayor**. No está ordenado por completo: solo garantiza quién va arriba.
- **Analogía: la sala de urgencias de un hospital.** El *triage* (clasificación por gravedad) no
  atiende por orden de llegada sino al paciente **más grave**; entre dos igual de graves, al que
  lleva más tiempo esperando. El médico no necesita la lista entera ordenada, solo saber **a quién
  llamar ahora**. Si un paciente mejora o empeora, no se reescribe su ficha: se le hace una ficha
  nueva y la vieja se descarta cuando sale (esto es la invalidación perezosa, punto (d)).
- **En el simulador:** el operador no puede vigilar decenas de andenes a la vez. La cola le dice
  qué andén atender primero, y "atender" es **despachar un bus** hacia ese andén.

#### (b) Qué guarda y con qué clave

- **Estructura:** `Monticulo("maximos")` de `estructuras/monticulo.py`, dueño el `Simulador`.
  La `Parada` no conoce el montículo.
- **Única alerta de esta fase:** saturación de andén.
- **Elemento:** la tupla `(severidad, -tick_deteccion, -secuencia, (id_andén, versión))`.

| Componente | Qué es | Por qué está ahí |
|---|---|---|
| `severidad` | `esperando / capacidad_bus` (número decimal, calculado en ejecución) | Criterio principal: la más grave sale primero |
| `-tick_deteccion` | Tick en que empezó la saturación **actual** del andén, con signo menos. Se conserva al republicar y se reinicia si el andén sale de saturación y vuelve a entrar | Entre iguales, gana la alerta **más antigua**. En uno de máximos gana el mayor; el signo menos invierte el criterio |
| `-secuencia` | Contador global que nunca se repite, con signo menos | Desempate final reproducible con la semilla, y garantiza que Python **nunca llegue a comparar** los datos |
| `(id_andén, versión)` | A qué andén se refiere y qué versión de su alerta es | Sirve para descartar alertas viejas (punto (d)) |

- **¿Por qué compuesta?** Python compara las tuplas posición por posición y solo mira la
  siguiente si hay empate. Así, una sola comparación aplica los tres criterios en orden.
- **¿Por qué sin unicidad estricta?** Muchas alertas pueden tener la misma severidad, y al
  montículo **no le importa**: su regla es "padre mayor **o igual**", así que los empates conviven.
  Es la diferencia con el AVL, donde dos claves iguales chocaban y por eso se necesitó el id. Aquí
  la secuencia no está para que las claves sean únicas, sino por reproducibilidad y para no
  comparar los datos.

#### (c) ¿Por qué un montículo y no otra estructura?

Con las dos premisas del equipo:

1. **Dinamismo y tipo de prioridad:** un montículo es una cola de prioridad con orden no estricto.
   Si los niveles de prioridad son **fijos, discretos y pocos**, un arreglo de colas basta, incluso
   en tiempo constante. El montículo gana cuando el volumen es dinámico, o las prioridades son
   **amplias, continuas o calculadas en ejecución**, y cuando sus operaciones (ver la raíz en O(1),
   insertar y extraer en O(log n), sobre un arreglo contiguo y sin rotaciones) sirven a una
   operación concreta del simulador.
2. **Relevancia:** de nada sirve acelerar una consulta que no aporta al objetivo: apoyar
   decisiones logísticas ante colapsos en hora pico.

Este uso cumple las dos: la severidad es **continua y se calcula en ejecución** (no hay niveles
fijos), las alertas entran durante toda la simulación, y el operador ve primero el andén más
crítico y actúa con un solo gesto.

| Alternativa | ¿Por qué no? |
|---|---|
| `ColaPrioridad` de la Fase 1 (arreglo de colas) | Necesita un número **fijo y pequeño** de niveles: una cola por nivel. Con severidades continuas no hay niveles que fijar. Por eso conviven: `ColaPrioridad` para los pasajeros (2 niveles fijos) y montículo para las alertas (prioridad continua). |
| Arreglo ordenado | Ver la más urgente sería O(1), pero cada alerta nueva llega con una severidad cualquiera y mantener el orden obliga a correr elementos: **O(n)** por inserción. |
| Agenda de eventos (montículo de mínimos por minuto de llegada de los buses) | **Descartada en esta fase.** Con tiempos enteros y acotados, un simple contador por bus ("ticks que le faltan al tramo") hace lo mismo con menos complejidad. Volvería en la fase final, con incidentes de duración aleatoria y sin tope (ver (f)). |
| Montículo para la fila de abordaje | Son 2 niveles fijos, ya resueltos por `ColaPrioridad`, y además quitaría una estructura de la Fase 1. |
| Ranking de andenes críticos con el árbol de segmentos | Cada estructura debe tener un trabajo propio. Esa consulta se discute al decidir el árbol de segmentos. |

**Frase para la defensa:** *"La `ColaPrioridad` sirve cuando las prioridades son pocas y fijas,
como prioritario o normal. La severidad de un andén es un número continuo que cambia en cada
tick, y ahí un arreglo de colas no sirve. El montículo nos da en O(1) el andén más crítico y en
O(log n) registra cada alerta nueva, sin mantener ordenada toda la lista."*

#### (d) Invalidación perezosa: cómo manejar alertas que cambian sin poder borrarlas

El montículo del equipo **no puede borrar ni modificar** un elemento del medio, solo sacar la
raíz. En vez de actualizar una alerta, se publica una nueva y la vieja se descarta cuando llega
a la raíz. Por eso se llama **perezosa**: la limpieza se deja para cuando es inevitable.

**Lo que guarda el `Simulador` por andén** (arreglos `ArregloDinamico` indexados por `id_andén`):
`version` (empieza en 0), `ultima_publicada` (la severidad de la última alerta, o `None` si no
hay referencia) y `tick_deteccion` (cuándo empezó la saturación actual).

**"Bus en camino"** tiene una sola fuente de verdad: el atributo `bus.anden_destino` (el andén
hacia donde va un bus despachado, o `None`). No se guarda una bandera aparte por andén, que
podría quedar desincronizada. **Una vez por tick**, antes de evaluar, se recorre la flota (O(B),
con B buses) y se arma el conjunto de andenes con bus en camino; ese mismo conjunto se reutiliza
para evaluar todos los andenes, en vez de recorrer la flota por cada uno. Costo por tick: O(B + P).
`atender()` hace un recorrido propio al empezar, porque ocurre fuera del tick.

**Al final de cada tick** (después de las llegadas y del abordaje), para cada andén:

1. Si tiene **bus en camino**: no se hace nada. No genera ni acepta alertas.
2. Si **no está saturado** (`severidad < UMBRAL_SATURACION`): se **restablece la referencia**
   (`ultima_publicada = None`). La alerta vieja, si quedaba, se descartará al extraerla.
3. Si **está saturado**:
   - si no hay referencia, es la **primera alerta**: se anota `tick_deteccion` (el tick actual) y
     se publica. Por eso `tick_deteccion` se **reinicia** cada vez que el andén sale de saturación
     y vuelve a entrar;
   - si hay referencia, se publica una alerta nueva solo si la severidad **cambió un 20 % o más,
     subiendo o bajando**: `|severidad - ultima_publicada| / ultima_publicada >= CAMBIO_MINIMO`
     (con `CAMBIO_MINIMO = 0.20`). La regla es simétrica para que una alerta no quede con la
     severidad inflada cuando el andén baja pero sigue saturado.
   - **Publicar** = `version[id] += 1`, `ultima_publicada[id] = severidad` e
     `insertar((severidad, -tick_deteccion, -secuencia, (id, version[id])))`; después
     `secuencia += 1`. Solo la última versión de cada andén es válida.

**Al atender** (`Simulador.atender()`, detrás de `POST /api/atender`): se saca la raíz con
`extraer_raiz()` y se **descarta** si cumple cualquiera de estas condiciones:

- su versión no es la actual del andén (hay una alerta más reciente);
- el andén ya no está saturado;
- el andén ya tiene un bus en camino.

Se repite hasta hallar una alerta válida, y entonces `despachar_bus(id_andén)` envía el bus. Si
el montículo se vacía sin hallar ninguna, es un error controlado que la API devuelve como 4xx,
no un fallo. Solo se atiende la **raíz**: elegir una alerta a mano queda fuera de alcance.

**Se restablece la referencia** (`ultima_publicada = None`) en tres momentos, para que el andén
pueda volver a alertar desde cero:

- cuando sale de saturación;
- cuando el bus despachado llega (si sigue saturado, al final de ese tick se publica una alerta nueva);
- cuando se deshace el despacho.

**Ver las k más urgentes** (`GET /api/alertas?limite=k`): se extraen alertas hasta reunir k
válidas, **descartando** las obsoletas que aparezcan, y luego se **reinsertan exactamente las
mismas tuplas** (misma secuencia, sin recalcular ni cambiar versiones). El montículo queda
equivalente en sus alertas válidas. Aunque es un GET, descartar obsoletas no cambia el conjunto
de alertas válidas: es una **lectura lógicamente pura** (lo que el usuario puede observar no
cambia, aunque por dentro se limpie). Hay que hacerla dentro del candado de la API, como los demás
endpoints. `mostrar()` no sirve para esto, porque devuelve el orden interno del arreglo, no el
orden de urgencia.

#### (e) Complejidad

n = alertas guardadas en el montículo (válidas y obsoletas), P = andenes, B = buses en la flota,
d = alertas obsoletas descartadas en una operación, k = alertas pedidas.

| Operación | Cómo | Complejidad |
|---|---|---|
| Ver la alerta de la raíz | `ver_raiz()` | O(1) |
| Publicar una alerta | `insertar(...)` | O(log n) |
| Sacar la raíz | `extraer_raiz()` | O(log n) |
| Evaluar todos los andenes al final del tick | Lista de buses en camino + una revisión por andén + publicaciones | O(B + P + p·log n), con p = alertas publicadas en el tick |
| Atender | Lista de buses en camino + extraer hasta hallar una válida + elegir el portal más cercano sumando tramos | O(B + P + (d + 1)·log n) |
| Ver las k más urgentes | Extraer k válidas + d obsoletas, y reinsertar las k | O(B + (k + d)·log n) |

#### (f) ¿Cómo se conserva y se amplía en la fase final?

Los extras quedan vivos, pero **no se implementan ahora**:

1. **Nuevos tipos de alerta** (por ejemplo, bus retrasado frente a su tiempo programado). Como
   la secuencia es única, Python nunca compara los datos, así que su forma puede crecer sin tocar
   la cola: pasaría a `(tipo, id_objeto, versión)`, con versiones por tipo y objeto. La condición
   es definir severidades comparables entre tipos (en la misma escala).
2. **Incidentes o bloqueos de vía con duración aleatoria y sin tope.** Ahí sí volvería la agenda
   de eventos con el **montículo de mínimos**, que hoy queda implementado y probado pero sin uso.
3. **Permanencia variable en estación según la carga:** cambia el motor, no la cola de alertas.
4. **Más portales, rutas y troncales:** el despacho ya elige el portal con **menor tiempo de
   viaje** comparando todos, así que la regla sirve igual con más portales.

#### (g) Limitaciones (dichas con honestidad)

1. **El argumento es de diseño y escala, no de velocidad actual.** Con decenas de andenes, recorrer
   todas las alertas, o directamente todos los andenes, también sería rápido. La ventaja aparece
   cuando crecen las alertas y los andenes.
2. **El montículo de mínimos está implementado y probado, pero sin uso en esta fase.** Se reserva
   para la agenda de eventos de la fase final.
3. **Mostrar las k más urgentes no es gratis.** `mostrar()` da el orden interno del arreglo; para
   las k más urgentes hay que extraer y reinsertar, O(k log n).
4. **Las alertas obsoletas ocupan espacio** hasta que se extraen. El 20 % limita cuántas se acumulan.
5. **El orden refleja la severidad al publicar, no la de este instante**, con un error acotado al
   20 %. Si la severidad cambia menos que eso, la alerta conserva su valor anterior.
6. **Son supuestos del modelo:** la fórmula de severidad, `UMBRAL_SATURACION` (1.0 provisional:
   hay más gente esperando de la que cabe en un bus vacío), el 20 % y que el bus despachado vaya
   **expreso y vacío**. No se afirma que TransMilenio opere así sin una fuente.
7. **Depende de que las tasas sean distintas por andén y por franja horaria.** Con tasas iguales,
   todos los andenes se saturarían parecido y la cola no tendría nada que ordenar.

### 2.3 Árbol de segmentos: panorama de alertas por sector del corredor

> **Dos palabras que no hay que confundir:** un **tramo** es el trayecto entre **dos andenes
> consecutivos** (el que recorre un bus en tránsito); un **sector** es un **rango de andenes**
> que el operador elige en el momento, por ejemplo "de la estación X a la Y en sentido B28".

#### (a) Idea y analogía

- **Árbol de segmentos:** un árbol binario donde cada hoja es una posición de una secuencia y
  cada nodo guarda el **resumen** de las hojas que tiene debajo, es decir, de un segmento contiguo.
  La raíz resume toda la secuencia. Para consultar un rango, se juntan los resúmenes de unos pocos
  nodos que lo cubren exactamente, en vez de mirar cada posición.
- **Analogía: un torneo por llaves.** Cada partido enfrenta a dos y el ganador sube a la siguiente
  ronda. Cada llave recuerda **quién ganó** y **cuántos de sus jugadores clasificaron**. Para saber
  quién es el mejor entre los jugadores 5 y 12, no hay que repetir todos los partidos: basta
  juntar los resultados de las dos o tres llaves que cubren a esos jugadores. Si un jugador cambia
  de nivel, solo se rejuegan los partidos de su camino hasta la final.
- **En el simulador:** el montículo da el orden **global** de las alertas, pero no responde
  "¿cuál es el andén más crítico **dentro de este sector**?" (habría que extraer alertas hasta
  encontrar una del sector). El árbol responde, para el sector que elija el operador, **cuántos
  andenes tienen alerta pendiente** y **cuál es el más crítico**, en O(log n).

#### (b) Qué guarda cada hoja y cada nodo, y por qué la operación es asociativa

- **Estructura:** `ArbolSegmentos(datos, combinar, neutro)` de `estructuras/arbol_segmentos.py`,
  dueño el `Simulador`. El árbol sigue siendo genérico: la hoja, `combinar` y el neutro son del
  dominio y viven en el `Simulador`.
- **Índice:** las 2N posiciones de la ruta, en el orden de la `ColaCircular`. El sentido **B28**
  ocupa la primera mitad y **F28** la segunda. Dentro de cada mitad el índice crece en la
  dirección del viaje, así que un sector con ambos extremos del mismo sentido **nunca cruza el
  portal**.
- **Hoja del andén i:** `(severidad, i, pendiente)`:

| Componente | Valor |
|---|---|
| `severidad` | La severidad **publicada** de la alerta vigente del andén (la misma del montículo, con su error acotado al 20 %), o `0.0` si no tiene alerta vigente |
| `i` | El id del andén (su posición en la ruta) |
| `pendiente` | 1 si el andén tiene una alerta vigente, 0 si no |

- **Definición exacta de "andén pendiente":** un andén **saturado y sin bus en camino**, es decir,
  con una alerta vigente en el montículo. Un andén saturado que ya tiene un bus despachado **no**
  cuenta. Por eso el campo se llama `andenes_pendientes` y no "andenes saturados".
- **Neutro:** `(float("-inf"), float("inf"), 0)`. Es una tupla, porque el árbol copia el neutro en
  4n posiciones y debe ser **inmutable** (que nadie pueda modificarlo después).
- **`combinar(a, b)`:**
  - gana la **severidad mayor** y, si empatan, el **índice menor** (así el resultado es
    reproducible);
  - las cantidades de pendientes se **suman**.

  El nodo guarda la misma forma que una hoja: `(severidad del más crítico, su índice, cuántos
  pendientes hay debajo)`.
- **¿Por qué es asociativa?** Asociativa significa que `combinar(combinar(a, b), c)` da lo mismo
  que `combinar(a, combinar(b, c))`, así que no importa cómo se agrupen las llaves.
  - La parte del "ganador" elige el mejor según un **orden total** (primero la severidad mayor y
    luego el índice menor). Elegir el mejor de tres da igual sin importar cómo se agrupen.
  - La parte de la cantidad es una **suma**, que es asociativa.
  - Las dos partes no se mezclan, así que la combinación también es asociativa.
- **¿Por qué el neutro no altera?** Su severidad `-inf` pierde contra cualquier hoja real (todas
  valen ≥ 0) y suma 0 pendientes. Se comprobará con una prueba de tuplas al azar.
- **Si `pendientes == 0`** en el resultado, no hay "más crítico" y no se muestra.

#### (c) ¿Por qué un árbol de segmentos y no otra cosa?

**Premisa del equipo:** el árbol de segmentos es apropiado cuando hay una **secuencia indexada** y
una **operación asociativa de resumen** (el resumen de A ∪ B se obtiene combinando el de A y el de
B). Pierde valor si los datos son estáticos y las consultas se pueden precalcular una vez. Cobra
valor cuando los datos **cambian al avanzar la simulación** y se necesitan consultas y
actualizaciones rápidas sin recalcular todo, y cuando el resumen aporta información útil para la
operación.

Este uso cumple las cuatro condiciones:

1. **Secuencia indexada:** los andenes en el orden de la ruta.
2. **Operación asociativa:** máximo con índice más suma de pendientes.
3. **Datos dinámicos con pocas actualizaciones por tick:** la hoja solo cambia cuando se publica o
   se retira una alerta, no con cada pasajero que llega.
4. **Valor analítico:** el panorama de un sector elegido por el operador, que ninguna otra
   estructura del proyecto responde.

| Alternativa | ¿Por qué no? |
|---|---|
| Recorrido lineal del sector | Cuesta O(k) por consulta, con k andenes en el sector. Funciona, pero crece con el tamaño del sector y de la red; el árbol cuesta O(log n) |
| Un contador fijo por zona | Solo sirve para rangos **fijos** (por ejemplo, tres troncales definidas de antemano). El operador elige el sector **en el momento** |
| Sumas acumuladas (prefijos) | Responden una suma de rango en O(1), pero cada cambio obliga a recalcular O(n) prefijos, y **no dan el máximo** de un rango |
| Pasajeros esperando por andén (suma) — *primera idea, descartada* | Casi todas las hojas cambian en casi cada tick. Actualizar c hojas cuesta c·log n y reconstruir cuesta ~n: el árbol no ahorra nada. No cumple la premisa |
| Duración de cada tramo | Es constante en esta fase (estática). Solo tendría sentido con incidentes que cambien los tiempos (fase final) |
| Buses en tránsito por tramo | Tiene pocas actualizaciones (solo cuando un bus llega), pero mide la **oferta**, no la demanda. Queda como nota para la fase final (ver (f)) |
| Series por tick | Se agregan al final; las sumas acumuladas bastan |

**Frase para la defensa:** *"El montículo nos dice qué atender primero en toda la ruta; el árbol de
segmentos nos da el panorama de cualquier sector que el operador elija: cuántos andenes están
pendientes y cuál es el peor, en O(log n). Lo justifica que la hoja solo cambia cuando se publica
o se retira una alerta, así que hay pocas actualizaciones por tick y muchas consultas posibles."*

#### (d) Consultas que habilita y su complejidad

n = 2N andenes; c = transiciones de alerta en un tick.

| Operación | Cómo | Complejidad |
|---|---|---|
| Construir con todas las hojas en `(0.0, i, 0)` | `ArbolSegmentos(hojas, combinar, neutro)` | O(n) |
| Panorama de un sector | `consultar(id_desde, id_hasta)` | O(log n) |
| Total de andenes pendientes en toda la ruta (para `estado()`) | `consultar_todo()` | O(1) |
| Cambiar la hoja de un andén | `actualizar(i, hoja)` | O(log n) |
| Costo por tick | c actualizaciones, solo en las transiciones | O(c·log n) |

- **`Simulador.consultar_sector(id_desde, id_hasta)`** devuelve diccionarios (la API no convierte):
  `andenes_pendientes` y, si hay alguno, el andén más crítico (id, nombre, sentido, severidad
  publicada). Valida con `ValueError` claro que ambos ids existan, que sean **del mismo sentido**
  y que `id_desde <= id_hasta` en el orden de la ruta. Un sector con extremos de sentidos distintos
  **se rechaza**, no se parte en dos. La API traduce el `ValueError` a 4xx.
- **`estado()`** expone `andenes_pendientes` del total con `consultar_todo()`, en O(1).
- **Detrás:** `GET /api/sector?desde=ID&hasta=ID`, de solo lectura.
- **En la web:**
  - un **selector de sentido** (B28/F28);
  - el operador marca dos estaciones en el mapa y el JS toma de `GET /api/ruta` los ids de los
    andenes **de ese sentido**;
  - el JS **ordena los dos ids** (solo compara dos números, sin lógica de negocio) y llama al
    endpoint;
  - el panel muestra cuántos andenes están pendientes y cuál es el más crítico, y el sector puede
    resaltarse sobre la polilínea.

  Con el selector, mezclar sentidos o invertir el rango no debería ocurrir desde la interfaz; los
  `ValueError` del Simulador quedan como protección. Hacer clic directo sobre la polilínea es una
  mejora opcional, fuera del alcance.

#### (e) Un solo punto de publicación y las 5 transiciones

El árbol es una **copia derivada** de lo que publica el montículo. Para que nunca se contradigan,
**un único método privado del Simulador** cambia el estado de alerta de un andén y actualiza los
dos juntos. Ninguna otra parte del código toca el montículo ni el árbol directamente.

| # | Transición | Montículo | Hoja del árbol |
|---|---|---|---|
| 1 | Se publica una alerta nueva (cruza el umbral, o cambia ≥ `CAMBIO_MINIMO`) | Se inserta con versión + 1 | `(severidad_publicada, i, 1)` |
| 2 | El andén sale de saturación | Se restablece la referencia; la alerta vieja se descarta al extraerla | `(0.0, i, 0)` |
| 3 | Se despacha un bus hacia el andén (queda "bus en camino") | Se extrajo la alerta | `(0.0, i, 0)`: ya no hay alerta pendiente |
| 4 | Se deshace un despacho | Se quita el bus y se restablece la referencia | Queda `(0.0, i, 0)`; si el andén sigue saturado, se republica (transición 1) al final del siguiente tick |
| 5 | Reinicio | Montículo nuevo | Árbol nuevo con todas las hojas en `(0.0, i, 0)` |

Cuando llega el bus despachado no hay una transición nueva: se restablece la referencia y, si el
andén sigue saturado, al final de ese tick ocurre la transición 1.

**Importante:** las actualizaciones ocurren **solo** en estas transiciones, **no en cada tick**.
Eso es lo que justifica el árbol: pocas hojas cambian por tick.

**Construcción:** el constructor necesita una secuencia con `len()` y `[]`, y `ArregloDinamico` no
los tiene. Las hojas iniciales se arman en un `ArregloDinamico` y se pasa su `mostrar()`, que
devuelve una **lista copia** (verificado en `estructuras/arreglo_dinamico.py`). Esa lista se usa
solo para construir y luego se descarta.

#### (f) ¿Cómo se conserva y se amplía en la fase final?

Los extras quedan vivos, pero **no se implementan ahora**:

1. **Más rutas y troncales:** un árbol por ruta, o uno global con desplazamientos por ruta (los
   sectores pasarían a ser troncales o partes de ellas). Como el árbol **no tiene "agregar
   posición"**, agregar andenes exige reconstruirlo (O(n)) o usar un árbol por ruta.
2. **Árbol de buses en tránsito por tramo:** con la misma estructura y otra hoja, por ejemplo para
   la "racha más larga de tramos sin buses", que detecta tramos desatendidos. Mide la oferta y
   complementaría este, que mide la demanda.
3. **Árbol de duraciones de tramo**, si llegan los incidentes que cambian los tiempos.
4. **Extra opcional (fuera del alcance base):** un botón "atender el más crítico del sector" que
   despache un bus hacia el andén ganador.

Lo de hoy no les cierra la puerta: el árbol es genérico, y la hoja, `combinar` y el neutro viven
en el Simulador, así que otro uso solo cambia esas tres piezas.

#### (g) Limitaciones (dichas con honestidad)

1. **Los valores son la severidad publicada**, con error acotado al 20 %, no el estado exacto.
   Para el número exacto de pasajeros se consulta la `Parada`.
2. **Es una copia derivada:** si algo actualiza el montículo sin pasar por el punto único de
   publicación, se desincroniza. Por eso existen el punto único y las pruebas de consistencia.
3. **El argumento es de diseño y de escala, no de velocidad actual.** Con unas decenas de andenes
   (supuesto, depende de la etapa 3), recorrer el sector también sería rápido.
4. **Para sectores fijos bastaría un contador por sector.** El valor del árbol es el sector que el
   operador elige **en el momento**, igual que el umbral que elige en el AVL.
5. **Depende de la web:** si la interfaz no permite seleccionar un sector, la decisión pierde
   relevancia. La selección en el mapa **debe** entrar en la etapa 5.
6. **El desempate no coincide con el del montículo:** aquí gana el índice menor y allá la alerta
   más antigua. Ambos son correctos, pero en empates pueden señalar andenes distintos. Por eso las
   pruebas de consistencia comparan solo la severidad y la cantidad, no el id.
7. **Depende de dos condiciones del supuesto S5** (`supuestos_y_datos_pendientes.md`):
   `UMBRAL_SATURACION > 0`, y que nunca exista una alerta vigente con severidad publicada menor que
   el umbral. Así, una hoja pendiente (severidad ≥ umbral) siempre le gana a una hoja sin alerta
   (0.0). Si el equipo cambia el umbral, hay que revisar S5.
8. **Los andenes de llegada de cada portal nunca alertan solo por un supuesto** (S12: su tasa de
   llegada es 0, porque ahí solo se baja la gente). No es un hecho del dominio.
9. **"¿Por qué hay una lista de Python ahí?"** (respuesta para la sustentación): *"El constructor
   del árbol necesita una secuencia con `len()` y acceso por índice para construirse en O(n), y
   nuestro `ArregloDinamico` no tiene esos operadores. Armamos las hojas en un `ArregloDinamico` y
   le pasamos la copia que da `mostrar()`. Esa lista solo se usa durante la construcción y luego
   se descarta: no reemplaza a ninguna estructura, porque las hojas viven dentro del propio árbol,
   que las guarda en un `ArregloDinamico`."*

