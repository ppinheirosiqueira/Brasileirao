var edicaoEscolhida

window.addEventListener('load', function() {
    edicaoEscolhida = document.getElementById("edicaoCampeonato")
})

function mudarCampeonato(){
    var selectedOptionEdicao = edicaoEscolhida.value
    var table = document.getElementsByClassName('aproveitamento')[0]

    fetch('../attRankingTimes/' + idUsuario + '/' + selectedOptionEdicao )
        .then(function(response) {
            return response.json()
        })
        .then(function(data) {
            if (data['data'] != null) {
                var texto = cabecalho()
                texto += "<tbody>"
                data['data'].forEach(time => {
                    texto +=    `<tr>
                                    <td><a href="../time/${time[1]}"><img src="../${time[0]}" alt="escudo" class="escudo"></a></td>
                                    <td>${time[2].toFixed(2)}</td>
                                    <td>${time[3].toFixed(2)}</td>
                                    <td>${time[4]}</td>
                                </tr>`
                })
                texto += "</tbody>"
                table.innerHTML = texto
            }
            else{
                table.innerHTML = "Nenhum jogo deste campeonato ocorreu ainda"
            }
        })
        .catch(function(error) {
            console.log('Ocorreu um erro:', error)
    })
}

function cabecalho(){
    return `<thead>
            <tr>
                <th>Time</th>
                <th>% Pepe</th>
                <th>Média Dif. Gols</th>
                <th>Número de Jogos Palpitados</th>
            </tr>
        </thead>`
}