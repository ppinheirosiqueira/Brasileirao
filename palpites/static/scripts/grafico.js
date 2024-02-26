document.addEventListener('DOMContentLoaded', function() {
  // Definição de variáveis globais 
  window.usuarios = "voce"
  var rodada_final = document.getElementById('rodada_final')

  fetch('user_result/' + window.usuarios + '/' +  document.getElementById('campeonato').value + '/1/' + rodada_final.value)
  .then(response => response.json())
  .then(data => {
      exibirGrafico(data)
  })
  .catch(error => {
      console.error(error)
  })
})

function validateForm(inicial,final) {
  if (parseInt(final) < parseInt(inicial)) {
    alert('A rodada final deve ser maior que a rodada inicial.')
    return false; // Impede o envio do formulário se a validação falhar
  }

  return true; // Permite o envio do formulário se a validação passar
}

function mudarRodadaInicial(value){
  var final = rodada_final.value
  teste = validateForm(value,final)
  if (teste){
    chamarGrafico(window.usuarios,value,final)
  }
}

function mudarRodadaFinal(value){
  var inicial = rodada_inicial.value
  teste = validateForm(inicial,value)
  if (teste){
    chamarGrafico(window.usuarios,inicial,value)
  }
}

function mudarCampeonatoGrafico(value){
  rodada_inicial = document.getElementById('rodada_inicial')
  rodada_final = document.getElementById('rodada_final')
  rodada_inicial.disabled = true
  rodada_inicial.innerHTML = ""
  rodada_final.disabled = true
  rodada_final.innerHTML = ""

  fetch('attRodadas/' + value )
      .then(function(response) {
          return response.json()
      })
      .then(function(data) {
          var rodadas = JSON.parse(data)
          rodadas.forEach(function(rodada,index){
            var option = document.createElement("option")
            option.value = rodada.fields.num
            option.text = rodada.fields.nome
            rodada_inicial.add(option)

            var clonedOption = option.cloneNode(true)
            rodada_final.add(clonedOption)

            if (index === 0) {
              rodada_inicial.value = rodada.fields.num
            }
            if (index === rodadas.length - 1) {
              rodada_final.value = rodada.fields.num
            }
          })
          rodada_inicial.disabled = false
          rodada_final.disabled = false
          chamarGrafico(window.usuarios, rodada_inicial.value, rodada_final.value)
        })
      .catch(function(error) {
          console.log('Ocorreu um erro:', error)
  })
}

function mudarUsuario(value){
  var inicial = parseInt(document.getElementById('rodada_inicial').value)
  var final = parseInt(document.getElementById('rodada_final').value)
  var divCheckboxes = document.getElementById('checkboxes')
  var divRadio = document.getElementById('radios')
  if (value === 'selecionar') {
    divCheckboxes.style.display = 'block'
    divRadio.style.display = 'none'
    window.usuarios = ""
  }
  else if (value === 'grupo'){
    divCheckboxes.style.display = 'none'
    divRadio.style.display = 'block'
    window.usuarios = ""
  } else {
    divCheckboxes.style.display = 'none'
    divRadio.style.display = 'none'
    if (value === 'voce') window.usuarios = "voce"
    else window.usuarios = "todos"    
    chamarGrafico(window.usuarios,inicial,final)
  }
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
  var inicial = parseInt(document.getElementById('rodada_inicial').value)
  var final = parseInt(document.getElementById('rodada_final').value)
  chamarGrafico(window.usuarios,inicial,final)
}

function chamarGrafico(usuarios,rod_ini,rod_fim){
  fetch('user_result/' + usuarios + '/' + document.getElementById('campeonato').value + '/' + rod_ini + '/' + rod_fim)
  .then(response => response.json())
  .then(data => {
      exibirGrafico(data)
  })
  .catch(error => {
      console.error(error)
  })
}

function chamarGrupo(grupo){
  var inicial = parseInt(document.getElementById('rodada_inicial').value)
  var final = parseInt(document.getElementById('rodada_final').value)
  fetch('user_result/grupo+' + grupo + '/' + inicial + '/' + final)
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

  var clrDark = getComputedStyle(document.body).getPropertyValue('--fc');

  var options = {
    responsive: true,
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'Rodada',
          color: clrDark,
        },
        ticks: {
          color: clrDark
        }
      },
      y: {
        min: minimo, // Valor mínimo do eixo Y
        max: maximo, // Valor máximo do eixo Y
        display: true,
        title: {
          display: true,
          text: 'Pontuação',
          color: clrDark,
        },
        ticks: {
          color: clrDark
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