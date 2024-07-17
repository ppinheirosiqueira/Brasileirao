function AttPagina(pagina){
    fetch('../../attPaginaEdicao/' + edicaoId + '/' + pagina)
    .then(response => response.json())
    .then(data => {
        atualizarPaginas(data, pagina)
        exibirPartidas(data)
    })
    .catch(error => {
        console.error(error)
    });
}

function atualizarPaginas(data, pagina){
    var pagination = document.getElementsByClassName("pagination")[0]

    pagination.innerHTML = ''

    if (pagina > 1){
        pagination.innerHTML += '<button onclick="AttPagina(' + (pagina - 1) + ')">Voltar</button> '
    }

    pagination.innerHTML += "Página " + pagina + " de " + data.total  

    if (pagina < data.total){
        pagination.innerHTML += ' <button onclick="AttPagina(' + (pagina + 1) + ')">Próxima</button>'
    }
}

function exibirPartidas(dados){
    var partidas = dados.partidas;
    var times = JSON.parse(dados.times)
    var container = document.getElementsByClassName("container-partidas")[0]
    var texto = ''
    partidas.forEach(function(jogo){
        texto += '<div class="partida">'
        texto += '<a href="../../partida/' + (-edicaoId) + '/' + jogo.pk +'">'
        texto += '<span class="texto nomeCampeonato">' + jogo.Rodada + '</span>'
        texto += '<img class="escudo" src="../../' + times[jogo.Mandante-1].fields.escudo + '" alt="escudo mandante" title="' + times[jogo.Mandante-1].fields.Nome +'">'
        texto += '<span class="texto">'
        if (jogo.golsMandante > -1 ){
            texto += jogo.golsMandante
        }
        texto += ' X '
        if (jogo.golsVisitante > -1 ){
            texto += jogo.golsVisitante
        }
        texto += '</span>'
        texto += '<img class="escudo" src="../../' + times[jogo.Visitante-1].fields.escudo + '" alt="escudo visitante" title="' + times[jogo.Visitante-1].fields.Nome +'">'
        texto += '</a>'       
        texto += '</div>'
    })

    container.innerHTML = texto
}