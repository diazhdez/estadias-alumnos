document.addEventListener("DOMContentLoaded", () => {
    const guardarBtn = document.getElementById("guardar-configuracion");
    const nuevaContraseñaInput = document.getElementById("nueva_contraseña");
    const confirmarContraseñaInput = document.getElementById("confirmar_contraseña");
    const togglePasswordButtons = document.querySelectorAll(".toggle-password");
    
    // Crear elementos para el indicador de fuerza
    const strengthIndicator = document.createElement("div");
    const strengthText = document.createElement("small");

    // Configurar clases para los elementos
    strengthIndicator.classList.add("strength-indicator");
    strengthText.classList.add("strength-text");

    // Agregar el indicador y texto debajo del campo de nueva contraseña
    const passwordContainer = nuevaContraseñaInput.closest(".form-group");
    passwordContainer.appendChild(strengthIndicator);
    passwordContainer.appendChild(strengthText);

    // Validación de fuerza de contraseña en tiempo real
    nuevaContraseñaInput.addEventListener("input", () => {
        const strength = calculatePasswordStrength(nuevaContraseñaInput.value);
        updateStrengthIndicator(strength);
    });

    // Evento de guardar cambios
    guardarBtn.addEventListener("click", () => {
        const nuevaContraseña = nuevaContraseñaInput.value.trim();
        const confirmarContraseña = confirmarContraseñaInput.value.trim();

        // Limpia errores previos
        clearErrors();

        // Validaciones
        if (!nuevaContraseña || !confirmarContraseña) {
            showError(confirmarContraseñaInput, "Por favor, completa ambos campos de contraseña.");
            return;
        }

        if (nuevaContraseña.length < 8) {
            showError(nuevaContraseñaInput, "La contraseña debe tener al menos 8 caracteres.");
            return;
        }

        if (nuevaContraseña !== confirmarContraseña) {
            showError(confirmarContraseñaInput, "Las contraseñas no coinciden. Inténtalo nuevamente.");
            return;
        }

        nuevaContraseñaInput.value = "";
        confirmarContraseñaInput.value = "";
        strengthIndicator.style.width = "0"; // Limpia la barra de fuerza
        strengthText.textContent = ""; // Limpia el texto
    });

    // Función para mostrar mensajes de error
    function showError(input, message) {
        input.classList.add("error");

        const errorMessage = document.createElement("small");
        errorMessage.textContent = message;
        errorMessage.classList.add("error-message");
        input.parentNode.appendChild(errorMessage);
    }

    // Limpia errores previos
    function clearErrors() {
        document.querySelectorAll(".error").forEach((input) => {
            input.classList.remove("error");
        });

        document.querySelectorAll(".error-message").forEach((message) => {
            message.remove();
        });
    }

    // Alternar visibilidad de contraseñas
    togglePasswordButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const input = button.previousElementSibling;
            const isPassword = input.getAttribute("type") === "password";

            // Cambia el tipo de input
            input.setAttribute("type", isPassword ? "text" : "password");

            // Cambia el ícono
            button.innerHTML = isPassword
                ? '<i class="bx bx-hide"></i>' // Ojo con raya
                : '<i class="bx bx-show"></i>'; // Ojo abierto
        });
    });

    // Calcula la fuerza de la contraseña
    function calculatePasswordStrength(password) {
        let strength = 0;

        if (password.length >= 8) strength++; // Longitud mínima
        if (/[A-Z]/.test(password)) strength++; // Letras mayúsculas
        if (/[a-z]/.test(password)) strength++; // Letras minúsculas
        if (/[0-9]/.test(password)) strength++; // Números
        if (/[\W_]/.test(password)) strength++; // Caracteres especiales

        return strength;
    }

    // Actualiza el indicador de fuerza de la contraseña
    function updateStrengthIndicator(strength) {
        const messages = [
            "Muy débil",
            "Débil",
            "Aceptable",
            "Buena",
            "Muy fuerte",
        ];

        const colors = [
            "#ff4d4d", // Muy débil - rojo
            "#ff884d", // Débil - naranja
            "#ffd54d", // Aceptable - amarillo
            "#4dff88", // Buena - verde claro
            "#4dff4d", // Muy fuerte - verde
        ];

        const widths = ["20%", "40%", "60%", "80%", "100%"];

        // Actualiza la barra de fuerza
        strengthIndicator.style.width = widths[strength - 1] || "0";
        strengthIndicator.style.backgroundColor = colors[strength - 1] || "#e0e0e0";

        // Actualiza el texto debajo de la barra
        strengthText.textContent = messages[strength - 1] || "";
        strengthText.style.color = colors[strength - 1] || "#333";
    }
});