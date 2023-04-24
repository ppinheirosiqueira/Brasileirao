from .models import User, Time, Partida, Palpite_Partida
import matplotlib
import matplotlib.pyplot as plt

import io
import urllib, base64

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

def grafico_padrao(request):

    matplotlib.use('agg')
    x = []
    y = []

    if request.user.is_authenticated is False:
        return None
    else:
        if len(Palpite_Partida.objects.filter(usuario=request.user.id)) > 0:
            aux_palpites = Palpite_Partida.objects.filter(usuario=request.user.id).order_by('partida__rodada')
            max_rodada = aux_palpites.last().partida.rodada
            min_rodada = max_rodada - 10
            if min_rodada <= 0:
                min_rodada = 1
            for i in range(min_rodada,max_rodada+1):
                x.append(i)
                auxPontos = pontos_rodada(filtrar_rodada(aux_palpites,i),request.user.id)
                y.append(auxPontos)
        else:
            return None

    plt.bar(x,y) # Definindo que quero em Barras
    plt.xlabel("Rodada")
    plt.ylabel("Pontos")
    plt.title(f"Pontos Por Rodada de {request.user}")
    plt.xticks(range(x[0],x[len(x)-1]+1))


    # Daqui para baixo não entendi nada, só aceitei que funciona
    fig = plt.gcf()

    buf = io.BytesIO() # acho que está criando um buffer
    fig.savefig(buf, format='png') # está salvando a imagem no buffer
    buf.seek(0) # não faço a mínima ideia do que está fazendo
    string = base64.b64encode(buf.read()) 

    uri = 'data:image/png;base64,' + urllib.parse.quote(string) # ur-image
    #html = '<img src = "%s"/>' % uri

    return uri

def pontos_rodada(palpites,id_usuario):
    pontos = 0
    for palpite in palpites:
        pontos += check_pontuacao_pepe(id_usuario,palpite.partida.id)
    return pontos

def filtrar_rodada(palpites,rodada):
    for palpite in palpites:
        if palpite.partida.rodada != rodada:
            palpites = palpites.exclude(partida=palpite.partida)
    return palpites