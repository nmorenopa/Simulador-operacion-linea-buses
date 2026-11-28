# datos/

Aquí irán los archivos JSON con la información de la ruta **Portal Américas ↔ Portal Norte**:
estaciones, coordenadas (para dibujarlas en el mapa) y sentido (ida o vuelta).

Por ahora la carpeta está vacía. Este README existe porque Git no guarda carpetas vacías.

Reglas para llenarla (Bloque 2, a cargo del equipo):

- Las estaciones salen de fuentes oficiales (TransMilenio S.A., datos abiertos de Bogotá) y
  **se revisan a mano** antes de guardarlas.
- Cada archivo indica su **fuente** (para citarla en formato IEEE en el documento de entrega).
- Lo que no venga en la fuente y haya que estimar se anota como **supuesto del modelo**.

**Investigación en curso (etapa 3):** las pautas, plantillas y criterios para recoger los datos
están en `datos/investigacion/README.md`. El JSON final (`datos/ruta_fb28.json`) lo arma el
asistente a partir de esos archivos.
