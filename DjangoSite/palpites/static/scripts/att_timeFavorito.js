$(document).ready(function() {
    $('#submitTimeFavorito').click(function() {
        var csrftoken = $("input[name=csrfmiddlewaretoken]").val();
        $.post(`../alterar_time_favorito`,
        {
            'idTime': $('#timeFavorito').val(),
            csrfmiddlewaretoken: csrftoken,
        },
        function(data){
            alert(data.mensagem);
            location.reload();
        });
    });
});