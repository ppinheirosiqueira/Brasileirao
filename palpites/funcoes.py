from .models import User, Time, Partida, Palpite_Partida
from django.db.models import F
from datetime import datetime, timezone, timedelta

import random
import colorsys

def check_pontuacao_pepe(palpites):
    mandante = palpites.filter(golsMandante=F('partida__golsMandante')).count()
    visitante = palpites.filter(golsVisitante=F('partida__golsVisitante')).count()
    vencedor = palpites.filter(vencedor=F('partida__vencedor')).count()
    return mandante+visitante+vencedor

def check_pontuacao_shroud(palpites):
    mandante = palpites.filter(golsMandante=F('partida__golsMandante'),vencedor=F('partida__vencedor')).count()
    visitante = palpites.filter(golsVisitante=F('partida__golsVisitante'),vencedor=F('partida__vencedor')).count()
    vencedor = palpites.filter(vencedor=F('partida__vencedor')).count()
    return mandante+visitante+vencedor

def pontos_rodadas_pepe(id,rodada):
    palpites = Palpite_Partida.objects.filter(usuario=id,partida__rodada=rodada)
    pontos = 0
    for palpite in palpites:
        pontos += check_pontuacao_pepe(id,palpite.partida.id)
    return pontos

# Função de ranking
def ranking(ano, rodada):
    if ano == 0 and rodada == 0:
        palpites = Palpite_Partida.objects.all() # Pega o ranking de tudo
    elif ano != 0 and rodada == 0:
        palpites = Palpite_Partida.objects.filter(partida__dia__year=ano) # Pega o ranking de um ano específico
    elif ano == 0 and rodada != 0:
        palpites = Palpite_Partida.objects.filter(partida__rodada=rodada) # Pega o ranking de uma rodada específica
    else:
        palpites = Palpite_Partida.objects.filter(partida__dia__year=ano,partida__rodada=rodada) # Pega o ranking de uma rodada específica de um ano específico   

    pessoas = list(palpites.values_list("usuario",flat=True).distinct())
    usernames = list(User.objects.filter(id__in=pessoas).values_list("username", flat=True))
    pontosP = []
    pontosS = []

    for pessoa in pessoas:
        palpites_pessoas = palpites.filter(usuario=pessoa)
        pontosP.append(check_pontuacao_pepe(palpites_pessoas))
        pontosS.append(check_pontuacao_shroud(palpites_pessoas))

    tuplas = zip(usernames,pessoas,pontosP,pontosS)
    tuplas_ordenadas = sorted(tuplas, key=lambda x: (x[2], x[3]), reverse=True)

    usernames, ids, pontosP, pontosS = zip(*tuplas_ordenadas)
    posicao = []
    for i, _ in enumerate(usernames, start=1):
        if i < len(usernames) and (pontosP[i] == pontosP[i - 1] and pontosS[i] == pontosS[i - 1]):
            posicao.append("-")
        else:
            posicao.append(i)

    return zip(posicao,usernames,ids,pontosP,pontosS)

# Função % acertos do jogador
def accuracy_user(id_usuario):
    palpites = Palpite_Partida.objects.filter(usuario=id_usuario)
    if len(palpites) == 0:
        return 0, 0, 0
    aGm = 100*palpites.filter(golsMandante=F('partida__golsMandante')).count()/len(palpites)
    aGv = 100*palpites.filter(golsVisitante=F('partida__golsVisitante')).count()/len(palpites)
    aR = 100*palpites.filter(vencedor=F('partida__vencedor')).count()/len(palpites)
    return aGm, aGv, aR

# Função Média de Pontos Pepe
def average_pepe(id_usuario):
    palpites = Palpite_Partida.objects.filter(usuario=id_usuario)
    if len(palpites) == 0:
        return 0
    soma = check_pontuacao_pepe(palpites)
    return soma/(len(palpites))

# Função Média de Pontos Shroud
def average_shroud(id_usuario):
    palpites = Palpite_Partida.objects.filter(usuario=id_usuario)
    if len(palpites) == 0:
        return 0
    soma = check_pontuacao_shroud(palpites)
    return soma/(len(palpites))

# Função dos jogos na tela inicial
def ultimos_jogos():
    timezone_offset = -3.0 
    tzinfo = timezone(timedelta(hours=timezone_offset))
    partidas = list(Partida.objects.filter(dia__lt=datetime.now(tzinfo))) # __lt = less than https://docs.djangoproject.com/en/3.1/ref/models/querysets/#lt
    return partidas[len(partidas)-3:len(partidas)]

def proximos_jogos():
    timezone_offset = -3.0 
    tzinfo = timezone(timedelta(hours=timezone_offset))
    partidas = list(Partida.objects.filter(dia__gt=datetime.now(tzinfo))) # __gt = Greater than https://docs.djangoproject.com/en/3.1/ref/models/querysets/#gt
    return partidas[0:3]

# Sem um bom nome no momento
def usuario_aleatorio():

    usuarios = list(User.objects.all())
    for aux_usuario in reversed(usuarios):
        if len(Palpite_Partida.objects.filter(usuario=aux_usuario)) == 0:
            usuarios.remove(aux_usuario)

    usuario = random.choice(usuarios)
    return usuario.id

def gerar_cor_clara():
    # Gerar um valor de cor aleatório em tons claros
    # Você pode ajustar os valores de mínimo e máximo para controlar a gama de cores claras geradas
    h = random.uniform(0.0, 1.0)  # Matiz
    s = random.uniform(0.3, 0.7)  # Saturação
    v = random.uniform(0.7, 1.0)  # Valor

    # Converter a cor de HSV para RGB
    r, g, b = colorsys.hsv_to_rgb(h, s, v)

    # Converter os valores de RGB para hexadecimal
    cor_hex = "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))

    return cor_hex

def clores_claras():
    cores = []
    for i in range(User.objects.all().count()-1):
        cores.append(gerar_cor_clara())

    return cores

cores = clores_claras()