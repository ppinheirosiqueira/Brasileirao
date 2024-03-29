var tipo = 0
if(isPc == "False"){
    isPc = false
}
else{
    isPc = true
}

window.addEventListener('load', function() {

    rodadaIEscolhida = document.getElementById("rodadaInicial")
    rodadaFEscolhida = document.getElementById("rodadaFinal")

    rodadaIEscolhida.addEventListener('change', function(){
        var inicial = parseInt(rodadaIEscolhida.value);
        var final = parseInt(rodadaFEscolhida.value);
        teste = validateForm(inicial,final)
        if (teste){
            fetchClassificacao()
        }
    })

    rodadaFEscolhida.addEventListener('change', function(){
        var inicial = parseInt(rodadaIEscolhida.value);
        var final = parseInt(rodadaFEscolhida.value);
        teste = validateForm(inicial,final)
        if (teste){
            fetchClassificacao()
        }
    })
})

function validateForm(inicial,final) {
    if (final < inicial) {
        alert('A rodada final deve ser maior que a rodada inicial.')
        return false
    }
    return true
}

function fetchClassificacao(){
    var selectedRodadaI = rodadaIEscolhida.value
    var selectedRodadaF = rodadaFEscolhida.value

    fetch('../../classificacao/' + edicaoId + '/' + selectedRodadaI + '/' + selectedRodadaF + '/' + tipo)
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            exibirDadosClassificacao(data)
        })
        .catch(function(error) {
            console.log('Ocorreu um erro:', error);
        })
}

function attClassificacao(valor) {
    tipo = valor
    fetchClassificacao()
}

function cabecalhoClassificacao(){
    if (isPc){
        return`
        <thead>
            <tr>
                <th>#</th>
                <th>Time</th>
                <th>P</th>
                <th>J</th>
                <th>V</th>
                <th>E</th>
                <th>D</th>
                <th>GP</th>
                <th>GC</th>
                <th>SG</th>
                <th>Aproveitamento</th>
            </tr>
        </thead>
        <tbody>
        `
    }
    return`
    <thead>
        <tr>
            <th>#</th>
            <th>Time</th>
            <th>P</th>
            <th>J</th>
            <th>V</th>
            <th>E</th>
            <th>D</th>
            <th>SG</th>
        </tr>
    </thead>
    <tbody>
    `

}

function exibirDadosClassificacao(data){
    var classificacaoDiv = document.getElementsByClassName('tabelaClassificacao')[0]
    var aux = 1
    if (data.length){
        texto = cabecalhoClassificacao()
        if(isPc){
            data.forEach(function(time){
                texto += "<tr>"
                texto += '<td>' + aux + '</td>'
                texto += '<td class="nome">' + time.time + '</td>'
                texto += "<td>" + time.pontos + "</td>"
                texto += "<td>" + time.jogos + "</td>"
                texto += "<td>" + time.vitorias + "</td>"
                texto += "<td>" + time.empates + "</td>"
                texto += "<td>" + time.derrotas + "</td>"
                texto += "<td>" + time.gols_pro + "</td>"
                texto += "<td>" + time.gols_contra + "</td>"
                texto += "<td>" + time.saldo_gols + "</td>"
                texto += "<td>" + time.aproveitamento.toFixed(2) + "%</td>"
                aux += 1
            })
        }
        else{
            data.forEach(function(time){
                texto += "<tr>"
                texto += '<td>' + aux + '</td>'
                texto += '<td class="nome">' + time.time + '</td>'
                texto += "<td>" + time.pontos + "</td>"
                texto += "<td>" + time.jogos + "</td>"
                texto += "<td>" + time.vitorias + "</td>"
                texto += "<td>" + time.empates + "</td>"
                texto += "<td>" + time.derrotas + "</td>"
                texto += "<td>" + time.saldo_gols + "</td>"
                aux += 1
            })
        }
        texto += `</tbody>`
    }
    classificacaoDiv.innerHTML = texto
}
