window.addEventListener('load', function() {
// Parte do Ranking

var anoEscolhido = document.getElementById("ano")
var rodadaEscolhida = document.getElementById("rodada")

anoEscolhido.addEventListener("change", function() {
    var selectedOptionAno = anoEscolhido.value
    var selectedOptionRodada = rodadaEscolhida.value

    fetch('ranking/' + selectedOptionAno + '/' + selectedOptionRodada)
    .then(response => response.json())
    .then(data => {
        exibirDados(data);
    })
    .catch(error => {
        console.error(error);
    });
})

rodadaEscolhida.addEventListener('change', function(){
    var selectedOptionRodada = rodadaEscolhida.value
    var selectedOptionAno = anoEscolhido.value

    fetch('ranking/' + selectedOptionAno + '/' + selectedOptionRodada)
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            exibirDados(data);
        })
        .catch(function(error) {
            console.log('Ocorreu um erro:', error);
        });
});
  
function exibirDados(data) {
    resultadoDiv = document.getElementsByClassName('ranking')
    if (data.length != 0){
        texto = cabecalho()
        data.forEach(function(jogador){
            texto += "<span class='posicao"
            if (jogador.posicao == 1){
                texto += " ouro'>"
            }
            else if(jogador.posicao == 2){
                texto += " prata'>"
            }
            else if(jogador.posicao == 3){
                texto += " bronze'>"
            }
            else{
                texto += "'>"
            }
            texto += jogador.posicao + "</span><span class='usuario'><a href=user/" + jogador.ids + ">" + jogador.usernames + "</a></span><span class='pontos'>" + jogador.pontosP + "</span><span class='pontos'>" + jogador.pontosS + "</span>"
        })
        resultadoDiv[0].innerHTML = texto
    }
    else{
        resultadoDiv[0].innerHTML = "Não existe nenhuma pontuação de nenhum usuário na rodada e ano especificados"
    }

}
});

function cabecalho(){
    return `
    <h2>Posição</h2>
    <h2>Usuário</h2>
    <div class="tooltip">
        <span class="tooltiptext pepe">
            Acertou o número de gols do mandante: 1 ponto
            <br>
            Acertou o número de gols do visitante: 1 ponto
            <br>
            Acertou quem venceu ou empatou: 1 ponto
        </span>
        <h2>Pontuação Pepe</h2>
    </div>
    <div class="tooltip">
        <span class="tooltiptext shroud">
            Acertou quem venceu ou empatou: 1 ponto
            <br>
            Caso acertou quem venceu/empatou e acertou o número de gols do mandante: 1 ponto
            <br>
            Caso acertou quem venceu/empatou e acertou o número de gols do visitante: 1 ponto
        </span>
        <h2>Pontuação Shroud</h2>
    </div>
    `
}