var startX;
var startY;

document.addEventListener('touchstart', function(e) {
    startX = e.touches[0].clientX;
    startY = e.touches[0].clientY;
});

document.addEventListener('touchmove', function(e) {
    e.preventDefault(); // Impede o comportamento padrão de rolagem
});

document.addEventListener('touchend', function(e) {
    var endX = e.changedTouches[0].clientX;
    var endY = e.changedTouches[0].clientY;
    
    var diffX = endX - startX;
    var diffY = endY - startY;
    
    if (Math.abs(diffX) > Math.abs(diffY)) {
        if (diffX > 0) {
            if (anterior != "None"){
                if (time != "None"){
                    window.location.href = `../partida/${time}/${anterior}`
                }
                else{
                    window.location.href = `../partida/${anterior}`
                }
            }
        } else {
            if (proxima != "None"){
                if (time != "None"){
                    window.location.href = `../partida/${time}/${proxima}`
                }
                else{
                    window.location.href = `../partida/${proxima}`
                }
            }
        }
    }
});