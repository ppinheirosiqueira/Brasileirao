// Parte do Ranking

var anoEscolhido = document.getElementById("ano")
var rodadaEscolhida = document.getElementById("rodada")

anoEscolhido.addEventListener("change", function() {
    var selectedOptionAno = anoEscolhido.value
    var selectedOptionRodada = rodadaEscolhida.value

    // Fazer a requisição AJAX usando fetch()
    fetch('ranking/' + selectedOptionAno + '/' + selectedOptionRodada)
    .then(response => response.json())
    .then(data => {
        // Tratar a resposta da requisição
        exibirDados(data);
    })
    .catch(error => {
        // Tratar erros
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
            // Manipule os dados retornados aqui
            exibirDados(data);
        })
        .catch(function(error) {
            console.log('Ocorreu um erro:', error);
        });
});
  
function exibirDados(data) {
    //var resultadoDiv = document.getElementById('grafico');
    resultadoDiv = document.getElementsByClassName('ranking')
    if (data.length != 0){
        texto = "<ul><li><h3>Posição</h3><h3>Usuário</h3><h3>Pontuação Pepe</h3><h3>Pontuação Shroud</h3></li>"
        data.forEach(function(jogador){
            texto += "<li><span>" + jogador.posicao + "</span><span>" + jogador.usernames + "</span><span>" + jogador.pontosP + "</span><span>" + jogador.pontosS + "</span></li></ul>"
        })
        resultadoDiv[0].innerHTML = texto
    }
    else{
        resultadoDiv[0].innerHTML = "Não existe nenhuma pontuação de nenhum usuário na rodada e ano especificados"
    }

}