document.addEventListener('DOMContentLoaded', function() {
    const themeButton = document.getElementsByClassName('theme-toggle')[0]

    if (document.getElementsByClassName('theme-toggle').length > 0) {
        themeButton.addEventListener('click', () => changeTheme(themeButton))
    }
})

function changeTheme(themeButton){
    document.body.classList.toggle('darkTheme')
    const baseUrl = window.location.origin;  // Obtém a parte da URL antes do caminho
    var url 
    if (document.body.classList.contains('darkTheme')){
        themeButton.innerHTML = `<img src="../../static/icons/moon.svg" alt="moon" class="icon_moon">`
        url = `${baseUrl}/alterar_tema/1`;  // Concatena o caminho desejado à URL base
    } else{
        themeButton.innerHTML = `<img src="../../static/icons/sun.svg" alt="sun" class="icon_sun">`
        url = `${baseUrl}/alterar_tema/0`;  // Concatena o caminho desejado à URL base
    }
    fetch(url)
    if (window.location.pathname === '/' && isPc == "True"){
        attGrafico()
    }
}

function attGrafico(){
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

    window.myChart.options = options;
    // Atualize o gráfico
    myChart.update();
}