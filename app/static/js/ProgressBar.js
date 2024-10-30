// Selección de los elementos necesarios
const circularProgress = document.querySelector(".circular-progress"),
      progressValue = document.querySelector(".progress-value");

// Datos del progreso recibidos desde el backend
let progressEndValue = 75; // Porcentaje de ejemplo, este valor debería venir desde el backend

let progressStartValue = 0,
    speed = 20;

// Función para animar la barra de progreso
let progress = setInterval(() => {
    progressStartValue++;

    // Actualiza el texto del porcentaje
    progressValue.textContent = `${progressStartValue}%`;

    // Actualiza el color de la barra circular según el progreso
    circularProgress.style.background = `conic-gradient(
        #7d2ae8 ${progressStartValue * 3.6}deg,
        #ededed 0deg
    )`;

    // Detiene la animación cuando alcanza el valor final
    if (progressStartValue >= progressEndValue) {
        clearInterval(progress);
    }
}, speed);
