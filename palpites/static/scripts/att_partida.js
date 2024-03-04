$(document).ready(function(){
    $("#att_partida").submit(function(e){
        e.preventDefault();
        var csrftoken = $("input[name=csrfmiddlewaretoken]").val();
        if ($("#data").val() != ""){
            $.post("../att_data_partida",
            {
                idPartida: $("#partida").val(),
                data: $("#data").val(),
                csrfmiddlewaretoken: csrftoken,
            },
            function(data){
                alert(data.mensagem);
                location.reload();
            });
        }
        else{
            $.post("../att_partida",
            {
                idPartida: $("#partida").val(),
                gMan: $("#gMan").val(),
                gVis:  $("#gVis").val(),
                csrfmiddlewaretoken: csrftoken,
            },
            function(data){
                alert(data.mensagem);
                location.reload();
            });
        }
    });
});