document.addEventListener('DOMContentLoaded', function() {
  var usuario = document.getElementById('usuario')
  var rodada_inicial = document.getElementById('rodada_inicial')
  var rodada_final = document.getElementById('rodada_final');

  // Obter o valor do último elemento <option>
  var ultimoValorOption = rodada_final.options[rodada_final.options.length - 1].value;

    fetch('user_result/todos/1/' + ultimoValorOption)
    .then(response => response.json())
    .then(data => {
        exibirGrafico(data);
    })
    .catch(error => {
        console.error(error);
    });

    rodada_inicial.addEventListener('change', function(){
      var inicial = parseInt(rodada_inicial.value);
      var final = parseInt(rodada_final.value);
      teste = validateForm(inicial,final)
      if (teste){
        console.log("oi")
        chamarGrafico("todos",inicial,final)
      }
    })

    rodada_final.addEventListener('change', function(){
      var inicial = parseInt(rodada_inicial.value);
      var final = parseInt(rodada_final.value);
      teste = validateForm(inicial,final)
      if (teste){
        console.log("oi")
        chamarGrafico("todos",inicial,final)
      }
    })


});

function validateForm(inicial,final) {
    if (final < inicial) {
      alert('A rodada final deve ser maior que a rodada inicial.');
      return false; // Impede o envio do formulário se a validação falhar
    }
  
    return true; // Permite o envio do formulário se a validação passar
}

function chamarGrafico(usuarios,rod_ini,rod_fim){
    fetch('user_result/' + usuarios + '/' + rod_ini + '/' + rod_fim)
    .then(response => response.json())
    .then(data => {
        exibirGrafico(data);
    })
    .catch(error => {
        console.error(error);
    });
}

function exibirGrafico(data){
  var canvas = document.getElementById('grafico')
  var ctx = canvas.getContext('2d');

  var minimo = 30
  var maximo = 0

  data.datasets.forEach(function(dados){
    if (minimo > Math.min.apply(null, dados.data)){
      minimo = Math.min.apply(null, dados.data)
    }
    if (maximo < Math.max.apply(null, dados.data)){
      maximo =  Math.max.apply(null, dados.data)
    }
  })

  minimo = minimo - 5
  if (minimo < 0) minimo = 0
  maximo = maximo + 5
  if (maximo > 30) maximo = 30

  var options = {
      responsive: true,
      scales: {
        x: {
          display: true,
          title: {
            display: true,
            text: 'Rodada',
            color: 'white',
          },
          ticks: {
            color: 'white' 
          }
        },
        y: {
          min: minimo, // Valor mínimo do eixo Y
          max: maximo, // Valor máximo do eixo Y
          display: true,
          title: {
            display: true,
            text: 'Pontuação',
            color: 'white',
          },
          ticks: {
            color: 'white' 
          }
        }
      }
    }

  var myChart = new Chart(ctx, {
      type: 'line',
      data: data,
      options: options
  });
}