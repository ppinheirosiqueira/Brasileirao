from .models import User, Time, Partida, Palpite_Partida
import random
from datetime import datetime, timezone, timedelta

class Pessoa:
    def __init__(self, username):
        self.nome = username
        self.pontosP = 0
        self.pontosS = 0
    def incrementoPontosP(self, valor):
        self.pontosP += valor
    def incrementoPontosS(self, valor):
        self.pontosS += valor

# Calculo de pontuação
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

    pessoas = {}  # Cria um dicionário vazio
    for palpite in palpites:
        if palpite.usuario.username not in pessoas:
            pessoa = Pessoa(palpite.usuario.username) # crio a pessoa
            pessoas[pessoa.nome] = pessoa # coloco ela no dicionário
            pessoa.incrementoPontosP(check_pontuacao_pepe(palpite.usuario.id,palpite.partida.id))
            pessoa.incrementoPontosS(check_pontuacao_shroud(palpite.usuario.id,palpite.partida.id))
        else:
            pessoas[palpite.usuario.username].incrementoPontosP(check_pontuacao_pepe(palpite.usuario.id,palpite.partida.id))
            pessoas[palpite.usuario.username].incrementoPontosS(check_pontuacao_shroud(palpite.usuario.id,palpite.partida.id))

    pessoas = list(pessoas.items())
    pessoas_ordenadas = sorted(pessoas, key=lambda x: x[1].pontosP, reverse=True)
    usernames = []
    ids = []
    pontosP = []
    pontosS = []
    posicao = []
    i = 1
    for pessoa in pessoas_ordenadas:
        posicao.append(i)
        usernames.append(pessoa[1].nome)
        ids.append(User.objects.get(username=pessoa[1].nome).id)
        pontosP.append(pessoa[1].pontosP)
        pontosS.append(pessoa[1].pontosS)
        i+=1
    return zip(posicao,usernames,ids,pontosP,pontosS)

# Função % acertos do jogador
def accuracy_user(id_usuario):
    palpites = list(Palpite_Partida.objects.filter(usuario=id_usuario))
    if len(palpites) == 0:
        return 0, 0, 0
    aGm = aGv = aR = 0
    for palpite in palpites:
        if palpite.golsMandante == palpite.partida.golsMandante:
            aGm += 1
        if palpite.golsVisitante == palpite.partida.golsVisitante:
            aGv += 1
        if palpite.vencedor == palpite.partida.vencedor:
            aR += 1
    aGm = 100*aGm/len(palpites)
    aGv = 100*aGv/len(palpites)
    aR = 100*aR/len(palpites)
    return aGm, aGv, aR

# Função Média de Pontos Pepe
def average_pepe(id_usuario):
    palpites = list(Palpite_Partida.objects.filter(usuario=id_usuario))
    if len(palpites) == 0:
        return 0
    soma = 0
    for palpite in palpites:
        soma = soma + check_pontuacao_pepe(id_usuario,palpite.partida.id)
    return soma/(len(palpites))

# Função Média de Pontos Shroud
def average_shroud(id_usuario):
    palpites = list(Palpite_Partida.objects.filter(usuario=id_usuario))
    if len(palpites) == 0:
        return 0
    soma = 0
    for palpite in palpites:
        soma = soma + check_pontuacao_shroud(id_usuario,palpite.partida.id)
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


