function criarModificador(){
    rodada = document.getElementById('rodada').value
    modificador = document.getElementById('modificador').value

    if (modificador > 99999 || modificador < 0.01){
        alert("O modificador precisa estar dentro do intervalo de 0.01 e 99999")
        return
    }

    fetch('../../create_mod/' + idGrupo + '/' + rodada + '/' + modificador )
        .then(function(response) {
            return response.json()
        })
        .then(function(data) {
            alert(data['mensagem'])
            lista = document.getElementById('listaModificadores')
            texto = ""
            data['rodadasModificadas'].forEach(modificador => {
                texto += `<li>${modificador.nome} - ${modificador.modificador} - <button onClick="excluirModificador(${modificador.id})"><img src="../static/icons/trash.svg" alt="excluir modificador"></button></li>`
            })
            lista.innerHTML = texto 
        })
        .catch(function(error) {
            console.log('Ocorreu um erro:', error)
    })
}

function excluirModificador(valor){
    fetch('../../delete_mod/' + valor)
        .then(function(response) {
            return response.json()
        })
        .then(function(data) {
            lista = document.getElementById('listaModificadores')
            texto = ""
            data['rodadasModificadas'].forEach(modificador => {
                texto += `<li>${modificador.nome} - ${modificador.modificador} - <button onClick="excluirModificador(${modificador.id})"><img src="../static/icons/trash.svg" alt="excluir modificador"></button></li>`
            })
            lista.innerHTML = texto 
        })
        .catch(function(error) {
            console.log('Ocorreu um erro:', error)
    })
}