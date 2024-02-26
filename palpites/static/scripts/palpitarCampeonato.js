function allowDrop(event) {
    event.preventDefault()
}

function drag(event) {
    var draggedElement = event.target.closest('td')
    var dataValue = draggedElement.getAttribute('data-value')
    event.dataTransfer.setData("text", event.target.textContent)
    event.dataTransfer.setData("data-value", dataValue)
    draggedElement.classList.add("dragged-item")
    document.addEventListener("dragend", dragEndHandler)
}

function drop(event) {
    event.preventDefault()
    var data = event.dataTransfer.getData("text")
    var value = event.dataTransfer.getData("data-value")
    var td = event.target.closest('td')
    var tdValue = td.getAttribute('data-value')

    atualizarClassificacao(value,tdValue)
    limparDragsItem()
}

function atualizarClassificacao(valor1,valor2) {
    var cell1 = document.querySelector('td[data-value="' + valor1 + '"]')
    var cell2 = document.querySelector('td[data-value="' + valor2 + '"]')

    var conteudo = cell1.innerHTML
    
    valor1 = parseInt(valor1)
    valor2 = parseInt(valor2)

    if (valor1 < valor2){
        for (var i = valor1; i < valor2; i++) {
            var celulaAtual = document.querySelector('td[data-value="' + i + '"]')
            var celulaAnterior = document.querySelector('td[data-value="' + (i + 1) + '"]')
            var valorAtual = celulaAtual.getAttribute('data-value')
            celulaAtual.innerHTML = celulaAnterior.innerHTML
            celulaAtual.setAttribute('data-value',valorAtual)
        }
    }
    else{
        for (var i = valor1; i > valor2; i--) {
            var celulaAtual = document.querySelector('td[data-value="' + i + '"]')
            var celulaAnterior = document.querySelector('td[data-value="' + (i - 1) + '"]')
            var valorAtual = celulaAtual.getAttribute('data-value')
            celulaAtual.innerHTML = celulaAnterior.innerHTML
            celulaAtual.setAttribute('data-value',valorAtual)
        }
    }
    cell2.innerHTML = conteudo
    cell2.setAttribute('data-value', valor2)

}

function highlightDropArea(event) {
    event.preventDefault();
    var dropTarget = event.target
    dropTarget.classList.add("drop-highlight")
}

function unhighlightDropArea(event) {
    event.preventDefault();
    var dropTarget = event.target
    dropTarget.classList.remove("drop-highlight")
}

function limparDragsItem(){
    var drop = document.querySelector(".drop-highlight")
    var drag = document.querySelector(".dragged-item")

    drop.classList.remove("drop-highlight")
    drag.classList.remove("dragged-item")
}

function dragEndHandler() {
    // Limpa as classes quando o arraste é encerrado
    var draggedItem = document.querySelector(".dragged-item");
    var dropHighlight = document.querySelector(".drop-highlight");

    if (draggedItem) {
        draggedItem.classList.remove("dragged-item");
    }

    if (dropHighlight) {
        dropHighlight.classList.remove("drop-highlight");
    }

    // Remove o manipulador de eventos dragend após o uso
    document.removeEventListener("dragend", dragEndHandler);
}

async function processarPalpite(){
    for (i = 1; i <= 20; i++){
        var atual = document.querySelector('td[data-value="' + i + '"]')
        var imgElement = atual.querySelector('img')
        var escudoSrc = imgElement.getAttribute('src')
        var novaString = escudoSrc.replace(/..\/media\/Escudos\//, "")
        try {
            let resultado = await palpitar(i, novaString, "pc")
            if (i == 20){
                alert(resultado)
                if (resultado != "Erro ao processar palpite"){
                    window.location.href = "../campeonato/" + campeonatoId + "/" + edicaoId
                }
            }
        } catch (error) {
            console.error(error)
        }    
    }
}

var classificacao = []

function touchStart(event) {
    var touchedElement = event.target.closest('span')
    touchedElement.classList.add("opaque-div")
    addTime(touchedElement.getAttribute('data-value'))
}

function addTime(nome) {
    classificacao.push(nome)
    var cell1 = document.querySelector('td[data-value="cel_' + parseInt(classificacao.length) + '"]')
    cell1.innerHTML = nome
}

function undo(){
    var cell1 = document.querySelector('td[data-value="cel_' + parseInt(classificacao.length) + '"]')
    var timeElement = document.querySelector('span[data-value="' + cell1.innerHTML + '"]')
    timeElement.classList.remove("opaque-div")
    cell1.innerHTML = null
    classificacao.pop(classificacao.length)
}

function retirar(valor){
    valor = parseInt(valor)
    var cell1 = document.querySelector('td[data-value="cel_' + valor + '"]')
    var timeElement = document.querySelector('span[data-value="' + cell1.innerHTML + '"]')
    timeElement.classList.remove("opaque-div")
    classificacao.splice(valor-1, 1)
    for (valor; valor <= classificacao.length; valor++){
        var aux = document.querySelector('td[data-value="cel_' + valor + '"]')
        aux.innerHTML = classificacao[valor-1]
    }
    var aux = document.querySelector('td[data-value="cel_' + valor + '"]')
    aux.innerHTML = ""
}

function reset(){
    classificacao = []
    for (let i = 1; i<=20; i++){
        var aux = document.querySelector('td[data-value="cel_' + i + '"]')
        aux.innerHTML = ""
    }
    var divPalpiteMobile = document.querySelector('.palpiteMobile')
    var spans = divPalpiteMobile.querySelectorAll('span')
    spans.forEach(function(span) {
        span.classList.remove("opaque-div")
    })
}

async function processarPalpiteMobile(){
    for (i = 1; i <= 20; i++){
        try {
            let resultado = await palpitar(i, classificacao[i-1], "mobile")
            if (i == 20){
                alert(resultado)
                if (resultado != "Erro ao processar palpite"){
                    window.location.href = "../campeonato/" + campeonatoId + "/" + edicaoId
                }
            }
        } catch (error) {
            console.error(error)
        }    
    }
}

function palpitar(posicao, time, pc) {
    return new Promise(function(resolve, reject) {
        fetch('../registroPalpiteEdicao/' + edicaoId + '/' + posicao + '/' + time + '/' + pc)
        .then(function(response) {
            return response.json()
        })
        .then(function(data) {
            if (data["mensagem"] == "Falhou") {
                reject("Erro ao processar palpite")
            } else {
                resolve(data["mensagem"])
            }
        })
        .catch(function(error) {
            reject("Ocorreu um erro: " + error)
        });
    });
}