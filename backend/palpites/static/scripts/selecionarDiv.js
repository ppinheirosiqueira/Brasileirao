document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('input[name="seletorDiv"]').forEach(function(radio) {
        radio.addEventListener('change', exibirDivSelecionada);
    });
});

function exibirDivSelecionada() {
    var divs = document.querySelectorAll('.divConteudo');

    divs.forEach(function(div) {
        div.style.display = 'none';
    });

    var selecionado = document.querySelector('input[name="seletorDiv"]:checked').id;
    var divCorrespondente = document.getElementById(selecionado.replace('Seletor', ''));
    divCorrespondente.style.display = divCorrespondente.dataset.display;
}

window.onload = exibirDivSelecionada;
