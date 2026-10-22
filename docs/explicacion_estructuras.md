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


## 4. Un minuto en el simulador

1. **Llegan pasajeros** → Cola: se forman en la fila de su parada.
2. **Bajan pasajeros** → Arreglo dinámico: sale quien llegó a su destino.
3. **Suben pasajeros** → Cola con prioridad: los prioritarios, primero.
4. **Avanza el bus** → Cola circular: pasa a la siguiente parada.

Aparte, cuando el operador agrega un bus o pausa, puede deshacer la última acción (**Pila**).

