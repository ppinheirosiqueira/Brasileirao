document.addEventListener('DOMContentLoaded', function() {
  window.usuarios = "voce"
  var selectUsuario = document.getElementById('usuario')
  var divCheckboxes = document.getElementById('checkboxes')
  var rodada_inicial = document.getElementById('rodada_inicial')
  var rodada_final = document.getElementById('rodada_final')

  // Obter o valor do último elemento <option>
  var ultimoValorOption = rodada_final.options[rodada_final.options.length - 1].value;
  rodada_final.value = ultimoValorOption

  fetch('user_result/' + window.usuarios + '/1/' + ultimoValorOption)
  .then(response => response.json())
  .then(data => {
      exibirGrafico(data);
  })
  .catch(error => {
      console.error(error);
  });

  selectUsuario.addEventListener('change',function(){
    var opcaoSelecionada = selectUsuario.value;
  
    if (opcaoSelecionada === 'selecionar') {
      divCheckboxes.style.display = 'block'; // Exibir checkboxes
      window.usuarios = ""
    } else {
      divCheckboxes.style.display = 'none'; // Ocultar checkboxes
      if (opcaoSelecionada === 'voce') window.usuarios = "voce"
      else window.usuarios = "todos"    
      var inicial = parseInt(rodada_inicial.value);
      var final = parseInt(rodada_final.value);      
      chamarGrafico(window.usuarios,inicial,final)
    }
  })

  rodada_inicial.addEventListener('change', function(){
    var inicial = parseInt(rodada_inicial.value);
    var final = parseInt(rodada_final.value);
    teste = validateForm(inicial,final)
    if (teste){
      chamarGrafico(window.usuarios,inicial,final)
    }
  })

  rodada_final.addEventListener('change', function(){
    var inicial = parseInt(rodada_inicial.value);
    var final = parseInt(rodada_final.value);
    teste = validateForm(inicial,final)
    if (teste){
      chamarGrafico(window.usuarios,inicial,final)
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

function modificarUsuario(nome){
  var id = nome + "Check" 
  if (document.getElementById(id).checked) {
    if (window.usuarios.length>0) window.usuarios += "+" + nome
    else window.usuarios += nome
  } else {
    var partes = window.usuarios.split("+")
    var string = ""
    partes.forEach(function(parte){
      if (parte != nome) string += parte + "+"
    })
    string = string.substring(0,string.length-1)
    window.usuarios = string
  }

  if (window.usuarios.length == 0){
    alert("Não é possível um gráfico sem pessoas")
    return
  }
  chamarGrafico(window.usuarios,parseInt(rodada_inicial.value),final = parseInt(rodada_final.value))
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

  try{
    window.myChart = new Chart(ctx, { // necessário o window. para tornar a variável global, dado que vou precisar acessar o chart fora do try
      type: 'line',
      data: data,
      options: options
    })
  }
  catch(error){
    window.myChart.data = data;
    window.myChart.options = options;
    // Atualize o gráfico
    myChart.update();
  }
}