function loadFile() {
    const fileInput = document.getElementById('fileInput')
    const fileContentContainer = document.getElementById('fileContent')

    const file = fileInput.files[0]
    if (file) {
        const reader = new FileReader()

        reader.onload = function(e) {
            // Exibindo o conteúdo do arquivo no container
            fileContentContainer.innerText = e.target.result
        }

        reader.readAsText(file)
    }
}

function registrar() {
    const fileContent = document.getElementById('fileContent').innerText

    fetch('/registrar_rodada_feita', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.getElementsByName('csrfmiddlewaretoken')[0].value
        },
        body: fileContent
    }).then(response => response.json())
        .then(data => alert(data))
        .catch(error => console.error('Erro:', error))
}