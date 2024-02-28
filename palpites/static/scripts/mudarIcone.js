function mudarIcone(palavra,value){
    aux1 = 'abrir' + palavra
    aux2 = 'fechar' + palavra
    if (value){
        document.getElementsByClassName(aux1)[0].style.display = 'none'
        document.getElementsByClassName(aux2)[0].style.display = 'block'
    }
    else{
        document.getElementsByClassName(aux1)[0].style.display = 'block'
        document.getElementsByClassName(aux2)[0].style.display = 'none'
    }
} 