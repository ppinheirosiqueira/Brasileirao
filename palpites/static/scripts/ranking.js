// Variáveis globais
var edicaoEscolhida
var rodadaEscolhida

window.addEventListener('load', function() {

    edicaoEscolhida = document.getElementById("edicao")
    rodadaEscolhida = document.getElementById("rodada")

    rodadaEscolhida.addEventListener('change', function(){fetchRanking()})
})

function mudarCampeonato(){
    var selectedOptionEdicao = edicaoEscolhida.value
    rodadaEscolhida.disabled = true;
    rodadaEscolhida.innerHTML = "";

    fetch('attRodadas/' + selectedOptionEdicao )
        .then(function(response) {
            return response.json()
        })
        .then(function(data) {
            var rodadas = JSON.parse(data)
            var optionTodas = document.createElement("option")
            optionTodas.value = 0
            optionTodas.text = "Todas"
            rodadaEscolhida.add(optionTodas)
            rodadas.forEach(function(rodada){
                var option = document.createElement("option")
                option.value = rodada.fields.num
                option.text = rodada.fields.nome
                rodadaEscolhida.add(option)
            })
            rodadaEscolhida.disabled = false
            rodadaEscolhida.value = 0
            fetchRanking()    
        })
        .catch(function(error) {
            console.log('Ocorreu um erro:', error)
    })
}

function fetchRanking(){
    var selectedOptionRodada = rodadaEscolhida.value
    var selectedOptionEdicao = edicaoEscolhida.value

    fetch('ranking/' + selectedOptionEdicao + '/' + selectedOptionRodada)
        .then(function(response) {
            return response.json()
        })
        .then(function(data) {
            exibirDados(data)
        })
        .catch(function(error) {
            console.log('Ocorreu um erro:', error);
        })
}

function cabecalho(){
    return `
    <thead>
        <tr>
            <th>Posição</th>
            <th>Usuário</th>
            <th>Pontuação Pepe</th>
            <th>Dif. Gols</th>
        </tr>
    </thead>
    `
}

function exibirDados(data) {
    resultadoDiv = document.getElementsByClassName('ranking')
    if (data.length){
        texto = cabecalho() + "<tbody>"
        data.forEach(function(jogador){
            texto += "<tr><td>"
            if (jogador.posicao == 1){
                texto += "<span class='ouro'>" + jogador.posicao + "</span></td>"
            }
            else if(jogador.posicao == 2){
                texto += "<span class='prata'>" + jogador.posicao + "</span></td>"
            }
            else if(jogador.posicao == 3){
                texto += "<span class='bronze'>" + jogador.posicao + "</span></td>"
            }
            else{
                texto += jogador.posicao + "</td>"
            }
            texto += "<td><a href=usuario/" + jogador.ids + ">" + jogador.usernames + "</a></td><td>" + jogador.pontosP + "</td><td>" + jogador.difGols + "</td></tr>"
        })
        resultadoDiv[0].innerHTML = texto + "</tbody>"
    }
    else{
        resultadoDiv[0].innerHTML = `<td class="erro">Não existe nenhuma pontuação de nenhum usuário no campeonato e rodada especificados</td>`
    }
}
