/*function showUploadButton(key) {
    const uploadButton = document.getElementById(`upload-${key}`);
    uploadButton.style.display = 'block';
}*/

function updateFileName(key) {
    const fileInput = document.getElementById(`archivo-${key}`);
    const fileNameContainer = document.getElementById(`fileNameContainer-${key}`);
    const fileNameDisplay = document.getElementById(`fileName-${key}`);

    // Verifica si hay un archivo seleccionado
    if (fileInput.files.length > 0) {
        const fileName = fileInput.files[0].name;
        fileNameDisplay.textContent = fileName;
        fileNameContainer.style.display = 'block';
    } else {
        fileNameContainer.style.display = 'none';
    }
}
