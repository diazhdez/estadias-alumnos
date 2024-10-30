const form = document.querySelector("form");
const fileInput = form.querySelector(".file-input");
const progressArea = document.querySelector(".progress-area");
const uploadedArea = document.querySelector(".uploaded-area");
const uploadBtn = document.querySelector("#uploadBtn"); // Asegúrate de tener un botón con este ID

// Variable para controlar si el archivo ya fue cargado
let fileUploaded = false;

form.addEventListener("click", (event) => {
    // Solo abrir el selector de archivos si no se ha subido un archivo
    if (!fileUploaded) {
        fileInput.click();
    }
});

fileInput.onchange = ({ target }) => {
    let file = target.files[0];

    // Validar que solo se permita subir archivos de Excel
    if (file && (file.type === "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" || file.type === "application/vnd.ms-excel")) {
        let fileName = file.name;
        if (fileName.length >= 12) {
            let splitName = fileName.split('.');
            fileName = splitName[0].substring(0, 12) + "." + splitName[1];
        }
        uploadBtn.classList.remove("hidden"); // Mostrar el botón
        uploadFile(file, fileName); // Pasa el archivo al método de subida
    } else {
        alert("Por favor, selecciona un archivo de Excel (.xls o .xlsx)"); // Mostrar alerta si no es un archivo de Excel
        fileInput.value = ""; // Limpiar el input
    }
}

function uploadFile(file, name) {
    let xhr = new XMLHttpRequest(); //CREANDO NUEVO OBJ XML (AJAX)
    xhr.open("POST", "/upload");
    xhr.upload.addEventListener("progress", ({ loaded, total }) => {
        let fileLoaded = Math.floor((loaded / total) * 100);
        let fileTotal = Math.floor(total / 1000);
        let fileSize;
        (fileTotal < 1024) ? fileSize = fileTotal + "KB" : fileSize = (loaded / (1024 * 1024)).toFixed(2) + " MB";
        let progressHTML = `<li class="row">
                                <i class="fas fa-file-alt"></i>
                                <div class="content">
                                <div class="details">
                                    <span class="name">${name} • Uploading</span>
                                    <span class="percent">${fileLoaded}%</span>
                                </div>
                                <div class="progress-bar">
                                    <div class="progress" style="width: ${fileLoaded}%"></div>
                                </div>
                                </div>
                            </li>`;
        progressArea.innerHTML = progressHTML;
        if (loaded == total) {
            progressArea.innerHTML = "";
            let uploadedHTML = `<li class="row">
                                    <div class="content">
                                    <i class="fas fa-file-alt"></i>
                                    <div class="details">
                                        <span class="name">${name} • Uploaded</span>
                                        <span class="size">${fileSize}</span>
                                    </div>
                                    </div>
                                    <i class="fas fa-check"></i>
                                </li>`; 
            uploadedArea.insertAdjacentHTML("afterbegin", uploadedHTML);

            // Marcar el archivo como subido
            fileUploaded = true; // Cambia esta variable para indicar que el archivo ya ha sido subido
        }
    });
    let formData = new FormData(form);
    xhr.send(formData);
}
