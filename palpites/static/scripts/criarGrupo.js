function criarGrupo(){
    nomeInput = document.getElementById('group_name')
    edicaoInput = document.getElementById('edicao')

    if (nomeInput.value.length > 30){
        alert("O nome só pode ter até 30 caracteres")
        return
    }

    fetch('../create_group/' + idUsuario + '/' + nomeInput.value + '/' + edicaoInput.value )
    .then(function(response) {
        return response.json()
    })
    .then(function(data) {
        alert(data['mensagem'])
        if (data['grupos'] != null){
            var grupos = document.getElementById('grupos')
            var texto = ""
            gruposData = JSON.parse(data['grupos'])
            gruposData.forEach(grupo => {
                texto += `<li><a href="../grupo/${grupo.fields.pk}">${grupo.fields.nome}</a></li>`
            });
            grupos.innerHTML = texto
        }
    })
    .catch(function(error) {
        console.log('Ocorreu um erro:', error)
    })
}