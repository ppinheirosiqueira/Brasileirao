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