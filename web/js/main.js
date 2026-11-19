// Capa 4: lo que corre en el navegador.
// Regla: el JS solo DIBUJA y MANDA ÓRDENES. No calcula nada del simulador;
// eso lo hace Python y nos llega por la API.

// --- 1. Buscar en la página los elementos que vamos a usar -----------------
// document.getElementById busca la etiqueta que tiene ese id en index.html.
const cajaResultado = document.getElementById("resultado");
const botonConsultar = document.getElementById("boton-consultar");

// --- 2. Escribir un mensaje en la caja --------------------------------------
// tipo es "ok" o "error": se usa como clase CSS para pintar el borde.
// Usamos textContent (y no innerHTML) porque solo escribe texto: es más
// simple y más seguro (nunca interpreta lo recibido como HTML).
function mostrar(texto, tipo) {
    cajaResultado.textContent = texto;
    cajaResultado.className = tipo;
}

// --- 3. Consultar la API ----------------------------------------------------
// "async" permite usar "await": esperar la respuesta del servidor sin
// congelar la página (el navegador sigue respondiendo mientras tanto).
async function consultarSalud() {
    mostrar("Consultando la API…", "");

    try {
        // fetch hace la petición HTTP. Como la página y la API salen del
        // mismo servidor, basta con la ruta "/api/salud" (sin CORS).
        const respuesta = await fetch("/api/salud");

        // respuesta.ok es true si el código está entre 200 y 299.
        if (!respuesta.ok) {
            mostrar(`La API respondió con error ${respuesta.status}`, "error");
            return;
        }

        // .json() convierte el texto JSON en un objeto de JavaScript
        // (el "diccionario" que devolvió salud() en api/main.py).
        const datos = await respuesta.json();

        mostrar(
            "Conectado: la API respondió\n" +
                `Estado: ${datos.estado}\n` +
                `Mensaje: ${datos.mensaje}\n` +
                `Python del servidor: ${datos.version_python}`,
            "ok",
        );
    } catch (error) {
        // fetch lanza un error si no hubo respuesta: el servidor está apagado
        // o la página se abrió con doble clic (file:///...) en vez de por
        // http://127.0.0.1:8000/
        mostrar("No se pudo conectar con la API. ¿Está corriendo fastapi dev?", "error");
        console.error(error); // detalle técnico en la consola del navegador (F12)
    }
}

// --- 4. Cuándo se consulta --------------------------------------------------
// Al cargar la página, y cada vez que se pulse el botón.
consultarSalud();
botonConsultar.addEventListener("click", consultarSalud);
