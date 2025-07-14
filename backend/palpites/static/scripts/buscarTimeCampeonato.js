document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('campeonato').onchange = function() {
    var edicao = this.value
    fetch('/timesCampeonato/' + edicao)
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao buscar os times.')
            }
            return response.json()
        })
        .then(data => {
            document.getElementById('mandante').innerHTML = ''
            document.getElementById('visitante').innerHTML = ''
            document.getElementById('rodada').innerHTML = ''

            data.times.forEach(function(time) {
                var optionMandante = document.createElement('option')
                optionMandante.value = time.id
                optionMandante.textContent = time.nome
                document.getElementById('mandante').appendChild(optionMandante)

                var optionVisitante = document.createElement('option')
                optionVisitante.value = time.id
                optionVisitante.textContent = time.nome
                document.getElementById('visitante').appendChild(optionVisitante)
            })

            data.rodadas.forEach(function(rodada) {
                var optionRodada = document.createElement('option')
                optionRodada.value = rodada.id
                optionRodada.textContent = rodada.nome
                document.getElementById('rodada').appendChild(optionRodada)
            })

            optionNovaRodada = document.createElement('option')
            optionNovaRodada.value = 0
            optionNovaRodada.textContent = "Nova Rodada"
            document.getElementById('rodada').appendChild(optionNovaRodada)

            if (document.getElementById('rodada').options.length === 1) {
                document.getElementById('numRodada').style.display = 'block';
                document.getElementById('nomeRodada').style.display = 'block';
                document.getElementById('labelNumRodada').style.display = 'block';
                document.getElementById('labelNomeRodada').style.display = 'block';
            }
        })
        .catch(error => {
            console.error(error)
        })
    }
})

function checkRodada(value){
    if (value === '0') {
        document.getElementById('numRodada').style.display = 'block'
        document.getElementById('nomeRodada').style.display = 'block'
        document.getElementById('labelNumRodada').style.display = 'block'
        document.getElementById('labelNomeRodada').style.display = 'block'
    } else {
        document.getElementById('numRodada').style.display = 'none'
        document.getElementById('nomeRodada').style.display = 'none'
        document.getElementById('labelNumRodada').style.display = 'none'
        document.getElementById('labelNomeRodada').style.display = 'none'
    }
}