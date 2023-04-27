from .models import User, Time, Partida, Palpite_Partida
import matplotlib
import matplotlib.pyplot as plt
import random
from datetime import datetime, timezone, timedelta

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

def historico_recent_user(id_jogador):
    x = []
    y = []

    aux_palpites = Palpite_Partida.objects.filter(usuario=id_jogador).order_by('partida__rodada')
    max_rodada = aux_palpites.last().partida.rodada
    min_rodada = max_rodada - 10
    if min_rodada <= 0:
        min_rodada = 1
    for i in range(min_rodada,max_rodada+1):
        x.append(i)
        auxPontos = pontos_rodada(filtrar_rodada(aux_palpites,i),id_jogador)
        y.append(auxPontos)

    return x, y

def usuario_aleatorio():

    usuarios = list(User.objects.all())
    for aux_usuario in reversed(usuarios):
        if len(Palpite_Partida.objects.filter(usuario=aux_usuario)) == 0:
            usuarios.remove(aux_usuario)

    usuario = random.choice(usuarios)
    return usuario.id

def grafico_padrao(request):

    matplotlib.use('agg')

    if request.user.is_authenticated is False:
        usuario = usuario_aleatorio()
    else:
        if len(Palpite_Partida.objects.filter(usuario=request.user.id)) > 0:
            usuario = request.user.id
        else:
            usuario = usuario_aleatorio()

    x, y = historico_recent_user(usuario)

    plt.bar(x,y) # Definindo que quero em Barras
    plt.xlabel("Rodada")
    plt.ylabel("Pontos")
    plt.title(f"Pontos Por Rodada de {User.objects.get(id=usuario).username}")
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

def ultimos_jogos():
    timezone_offset = -3.0 
    tzinfo = timezone(timedelta(hours=timezone_offset))
    partidas = list(Partida.objects.filter(dia__lt=datetime.now(tzinfo))) # __lt = less than https://docs.djangoproject.com/en/3.1/ref/models/querysets/#lt
    return partidas[len(partidas)-4:len(partidas)-1]

def proximos_jogos():
    timezone_offset = -3.0 
    tzinfo = timezone(timedelta(hours=timezone_offset))
    partidas = list(Partida.objects.filter(dia__gt=datetime.now(tzinfo))) # __gt = Greater than https://docs.djangoproject.com/en/3.1/ref/models/querysets/#gt
    return partidas[0:3]