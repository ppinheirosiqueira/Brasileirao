function mudarTema(tema){
    var csrftoken = $("input[name=csrfmiddlewaretoken]").val();
    $.post(`../alterar_tema`,
    {
        csrfmiddlewaretoken: csrftoken,
        'tema':tema,
    },
    function(data){
        alert(data.mensagem);
        location.reload();
    });
}

function mudarAgora(item,valor){
    var r = document.querySelector(':root');
    r.style.setProperty(item, valor);
}

function updateFilter() {
    var filter = `invert(${$('#invert').val()}%) sepia(${$('#sepia').val()}%) saturate(${$('#saturate').val()}%) hue-rotate(${$('#hue-rotate').val()}deg) brightness(${$('#brightness').val()}%) contrast(${$('#contrast').val()}%)`;
    mudarAgora('--filter',filter)
}

function temaCustomizado(){
    $.post(`../alterar_tema`,
    {
        csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        'tema': "customizado",
        'filtro': `invert(${$('#invert').val()}%) sepia(${$('#sepia').val()}%) saturate(${$('#saturate').val()}%) hue-rotate(${$('#hue-rotate').val()}deg) brightness(${$('#brightness').val()}%) contrast(${$('#contrast').val()}%)`,
        'fundo': $('#corFundo').val(),
        'fonte':  $('#corFonte').val(),
        'hover':  $('#corHover').val(),
        'borda':  $('#corBorda').val(),
        'selecionado':  $('#corSelecionado').val(),
        '0pontos':  $('#cor0').val(),
        '1pontos':  $('#cor1').val(),
        '2pontos':  $('#cor2').val(),
        '3pontos':  $('#cor3').val(),
    },
    function(data){
        alert(data.mensagem);
        location.reload();
    });
}