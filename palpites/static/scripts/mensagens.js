function abrirMensagem(id){
    fetch('../pegarMensagem/' + id)
    .then(function(response) {
        return response.json()
    })
    .then(function(data) {
        attTitulos(data['titulos'])
        attMensagem(data['mensagem'])
    })
    .catch(function(error) {
        console.log('Ocorreu um erro:', error)
    })
}

function marcarNaoLido(id){
    fetch('../marcarNaoLida/' + id)
    .then(function(response) {
        return response.json()
    })
    .then(function(data) {
        attTitulos(data['titulos'])
    })
    .catch(function(error) {
        console.log('Ocorreu um erro:', error)
    })
}

function attTitulos(titulos){
    tituloDiv = document.getElementsByClassName('titulos')[0]
    texto = "<h2>Lista de Mensagens</h2>"
    if (titulos.length === 0) {
        texto += "Você não tem nenhuma mensagem"
    } else {
        titulos.forEach(titulo => {
            if (titulo.lida){
                texto += `<div class="mensagemTitulo">`
            }
            else{
                texto += `<div class="mensagem-nao-lida mensagemTitulo">`
            }
            texto += `<span class='titulo' onClick="abrirMensagem(${titulo.idMensagem})">${titulo.titulo}</span>
            <span class='marcarNaoLido' onClick="marcarNaoLido(${titulo.idMensagem})">Marcar como não lido</span>
            <span class="from"><b>De:</b> <a href="../../usuario/${titulo.idFrom}">${titulo.from}</a></span></div>`
        });
    }
    tituloDiv.innerHTML = texto
}

function attMensagem(mensagem){
    mensagemDiv = document.getElementById('mensagem')
    texto = `<span class='titulo'>Titulo: ${mensagem.titulo}</span>`
    texto += `<span class="lixo" onClick="apagarMensagem(${mensagem.idMensagem})"><img src="../../static/icons/trash.svg" alt="Apagar mensagem" title="Apagar Mensagem"></span>`
    texto += `<span class="from"><b>De:</b> <a href="../../usuario/${mensagem.idFrom}">${mensagem.from}</a></span>`
    texto += `<span class="mensagem">${mensagem.texto}</span>`
    mensagemDiv.innerHTML = texto
}

function apagarMensagem(id){
    fetch('../apagarMensagem/' + id)
    .then(function(response) {
        return response.json()
    })
    .then(function(data) {
        attTitulos(data['titulos'])
        mensagemDiv = document.getElementById('mensagem')
        mensagemDiv.innerHTML = "Nenhuma Mensagem Selecionada"
    })
    .catch(function(error) {
        console.log('Ocorreu um erro:', error)
    })
}

function apagarMensagemCelular(id){
    fetch('../apagarMensagem/' + id)
    .then(function(response) {
        return response.json()
    })
    .then(function(data) {
        window.location.href = '../mensagens'
    })
    .catch(function(error) {
        console.log('Ocorreu um erro:', error)
    })
}