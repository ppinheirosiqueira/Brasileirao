async function selecionarEstatistica(valor){
    var dados = await callEstatistica(valor);
    var tabela  = document.querySelector('#estatisticas .ranking');

    tabela.innerHTML = cabecalho(valor);

    dados.forEach(function(vetor) {
        var linha = document.createElement('tr');
    
        if (valor=="cravadas"){
            retorno = cravada(vetor);
        }
        else if (valor == "avgPontos"){
            retorno = avgPontos(vetor);
        }
        else if (valor == "modaResultados" || valor == "modaPalpites"){
            retorno = moda(vetor);
        }
        else{
            retorno = classificacao(vetor);
        }

        retorno.forEach(function(dado) {
            linha.appendChild(dado);
        });
    
        tabela.appendChild(linha);
    })
}

async function callEstatistica(item){
    return fetch('../../estatistica/' + edicaoId + '/' + item)
        .then(function(response) {
            return response.json();
        })
        .catch(function(error) {
            console.log('Ocorreu um erro:', error);
        });
}

function cabecalho(valor){
    if (valor=="cravadas"){
        return `<thead>
                    <tr>
                        <th>Posição</th>
                        <th>Usuário</th>
                        <th>Nº de Cravadas</th>
                    </tr>
                </thead>
                <tbody>
        `
    }
    if (valor=="avgPontos"){
        return `<thead>
                    <tr>
                        <th>Posição</th>
                        <th>Usuário</th>
                        <th>Média Pontos</th>
                        <th>Média Dif. Gols</th>
                    </tr>
                </thead>
                <tbody>
            `
    }
    if (valor=="modaPalpites"){
        return `<thead>
                    <tr>
                        <th>Nº de Vezes</th>
                        <th>Gols Mandante</th>
                        <th>X</th>
                        <th>Gols Visitante</th>
                    </tr>
                </thead>
                <tbody>
            `
    }
    if (valor=="modaResultados"){
        return `<thead>
                    <tr>
                        <th>Nº de Vezes</th>
                        <th>Gols Mandante</th>
                        <th>X</th>
                        <th>Gols Visitante</th>
                    </tr>
                </thead>
                <tbody>
            `
    }
    return `<thead>
                <tr>
                    <th>Posição</th>
                    <th>Usuário</th>
                    <th>Pontuação</th>
                    <th>Nº de Cravadas</th>
                </tr>
            </thead>
            <tbody>
            `
}

function cravada(vetor){
    var celula1 = document.createElement('td');
    if (vetor[0] <= 3){
        celula1.appendChild(podio(vetor[0]));
    }
    else{
        celula1.textContent = vetor[0];
    }

    var celula2 = document.createElement('td');
    celula2.innerHTML = `<a href="../../usuario/${vetor[1]}">${vetor[2]}</a>`;

    var celula3 = document.createElement('td');
    celula3.textContent = vetor[3];

    return [celula1, celula2, celula3]
}

function avgPontos(vetor){
    var celula1 = document.createElement('td');
    if (vetor[0] <= 3){
        celula1.appendChild(podio(vetor[0]));
    }
    else{
        celula1.textContent = vetor[0];
    }

    var celula2 = document.createElement('td');
    celula2.innerHTML = `<a href="../../usuario/${vetor[1]}">${vetor[2]}</a>`;

    var celula3 = document.createElement('td');
    celula3.textContent = vetor[3].toFixed(2);

    var celula4 = document.createElement('td');
    celula4.textContent = vetor[4].toFixed(2);

    return [celula1, celula2, celula3, celula4]
}

function moda(vetor){
    var celula1 = document.createElement('td');
    celula1.textContent = vetor[0];

    var celula2 = document.createElement('td');
    celula2.textContent = vetor[1];

    var celula3 = document.createElement('td');
    celula3.innerHTML = "X";

    var celula4 = document.createElement('td');
    celula4.textContent = vetor[2];

    return [celula1, celula2, celula3, celula4]
}

function classificacao(vetor){
    var celula1 = document.createElement('td');
    if (vetor[0] <= 3){
        celula1.appendChild(podio(vetor[0]));
    }
    else{
        celula1.textContent = vetor[0];
    }

    var celula2 = document.createElement('td');
    celula2.innerHTML = `<a href="../../usuario/${vetor[1]}">${vetor[2]}</a>`;

    var celula3 = document.createElement('td');
    celula3.textContent = vetor[3];

    var celula4 = document.createElement('td');
    celula4.textContent = vetor[4];

    return [celula1, celula2, celula3, celula4]
}

function podio(valor){
    var spanAux = document.createElement('span');
    if (valor == 1){
        spanAux.className ="ouro";
    }
    else if (valor == 2){
        spanAux.className ="prata";
    }
    else{
        spanAux.className ="bronze";        
    }
    spanAux.textContent = valor;
    return spanAux;
}