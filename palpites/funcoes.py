from .models import User, Time, Partida, Palpite_Partida

def ranking():
    usuarios = list(User.objects.all()) # Pego todos os Usuarios 
    for usuario in usuarios: 
        if len(Palpite_Partida.objects.filter(usuario=usuario.id)) == 0:
            usuarios.remove(usuario) # Retiro os sem palpites
    
    usernames = []
    pontosP = []
    pontosS = []
    auxPontosP = 0
    auxPontosS = 0
    for usuario in usuarios:
        palpites = list(Palpite_Partida.objects.filter(usuario=usuario.id))
        for palpite in palpites:
            auxPontosP = auxPontosP + check_pontuacao_pepe(usuario.id,palpite.partida.id)
            auxPontosS = auxPontosS + check_pontuacao_shroud(usuario.id,palpite.partida.id)
        usernames.append(usuario.username)
        pontosP.append(auxPontosP)
        pontosS.append(auxPontosS)

    return zip(usernames,pontosP,pontosS)

def check_pontuacao_pepe(id_usuario,id_partida):
    pontuacao = 0
    auxPartida = Partida.objects.get(id=id_partida)
    auxPalpite = Palpite_Partida.objects.get(usuario=id_usuario,partida=id_partida)
    if auxPartida.golsMandante == auxPalpite.golsMandante: pontuacao = pontuacao + 1
    if auxPartida.golsVisitante == auxPalpite.golsVisitante: pontuacao = pontuacao + 1
    if auxPartida.vencedor == auxPalpite.vencedor: pontuacao = pontuacao + 1
    return pontuacao

def check_pontuacao_shroud(id_usuario,id_partida):
    pontuacao = 0
    auxPartida = Partida.objects.get(id=id_partida)
    auxPalpite = Palpite_Partida.objects.get(usuario=id_usuario,partida=id_partida)
    if auxPartida.vencedor == auxPalpite.vencedor: 
        pontuacao = pontuacao + 1
        if auxPartida.golsMandante == auxPalpite.golsMandante: pontuacao = pontuacao + 1
        if auxPartida.golsVisitante == auxPalpite.golsVisitante: pontuacao = pontuacao + 1
    return pontuacao