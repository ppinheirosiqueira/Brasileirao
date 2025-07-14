document.addEventListener('DOMContentLoaded', function() {
    if (temPalpite){
        pegar_palpite(edicaoId,idGrupo)
    }
})

function pegar_palpite(idCampeonato,idGrupo = null){
    var url
    if (idGrupo != null){
        url = '../pegarPalpite/' + idCampeonato + '/' + idGrupo
    }
    else{
        url = '../../pegarPalpite/' + idCampeonato
    }
    fetch(url)
    .then(function(response) {
        return response.json()
    })
    .then(function(data) {
        tabela = document.getElementsByClassName('palpites')[0]
        texto = `<thead><tr class="header"><th class="posicao">Posição</th>`
        data['palpites'].forEach(user => {
            texto += `<th>${user.nome}</th>`
        })
        times = JSON.parse(data['times'])
        texto += `</tr></thead><tbody>`
        quantidadePalpites = data['palpites'][0].palpites.length
        for (i=0; i < quantidadePalpites; i++){
            texto += adicionarLinha(i,data['palpites'],times)
        }
        texto += `</tbody>`
        tabela.innerHTML = texto
    })
    .catch(function(error) {
        console.log('Ocorreu um erro:', error)
    })
}

function adicionarLinha(posicao, palpites,times) {
    var row = "<tr><td class='posicao'>" + (posicao + 1) + "</td>"
    palpites.forEach(palpite => {
        row += `<td><img class="escudo" src="../../${times[palpite.palpites[posicao].time-1].fields.escudo}" alt="escudo ${times[palpite.palpites[posicao].time-1].fields.Nome}" title="${times[palpite.palpites[posicao].time-1].fields.Nome}"></td>`
    })
    row += "</tr>"
    return row
}