function AttPagina(pagina){
    fetch('attPagina/' + pagina)
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
    var partidas = JSON.parse(dados.partidas)
    var times = JSON.parse(dados.times)
    var container = document.getElementsByClassName("container-partidas")[0]
    var texto = ''
    partidas.forEach(function(jogo){
        texto += '<div class="partida">'
        texto += '<a href="partida/' + jogo.pk +'">'
        texto += '<span class="texto">' + jogo.fields.rodada + 'ª Rodada - </span>'
        texto += '<img class="escudo" src="' + times[jogo.fields.Mandante-1].fields.escudo + '" alt="escudo mandante">'
        texto += '<span class="texto">'
        if (jogo.fields.golsMandante > -1 ){
            texto += jogo.fields.golsMandante
        }
        texto += ' X '
        if (jogo.fields.golsVisitante > -1 ){
            texto += jogo.fields.golsVisitante
        }
        texto += '</span>'
        texto += '<img class="escudo" src="' + times[jogo.fields.Visitante-1].fields.escudo + '" alt="escudo visitante">'
        texto += '</a>'       
        texto += '</div>'
    })

    container.innerHTML = texto
}