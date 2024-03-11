from ..models import Palpite_Partida, User
from .score import check_diferenca_gols, check_pontuacao_pepe

def ranking(edicao, rodada):
    
    if edicao == 0 and rodada == 0:
        palpites = Palpite_Partida.objects.all() # Pega o ranking de tudo
    elif edicao != 0 and rodada == 0:
        palpites = Palpite_Partida.objects.filter(partida__Rodada__edicao_campeonato__id=edicao)
    elif edicao != 0 and rodada != 0:
        palpites = Palpite_Partida.objects.filter(partida__Rodada__edicao_campeonato__id=edicao,partida__Rodada__num=rodada)

    pessoas = list(User.objects.order_by('id').filter(id__in=palpites.values_list("usuario", flat=True).distinct()))
    usernames = [pessoa.username for pessoa in pessoas]
    ids = [pessoa.id for pessoa in pessoas]
    pontosP = [check_pontuacao_pepe(palpites.filter(usuario=pessoa)) for pessoa in ids]
    difGols = [check_diferenca_gols(palpites.filter(usuario=pessoa).exclude(partida__golsMandante=-1, partida__golsVisitante=-1)) for pessoa in ids]

    if (len(usernames) == 0):
        return None
    tuplas = zip(usernames,ids,pontosP,difGols)
    tuplas_ordenadas = sorted(tuplas, key=lambda x: (-x[2], x[3]))

    usernames, ids, pontosP, difGols = zip(*tuplas_ordenadas)
    posicao = []
    for i, _ in enumerate(usernames, start=1):
        if i < len(usernames) and (pontosP[i] == pontosP[i - 1] and difGols[i] == difGols[i - 1]):
            posicao.append("-")
        else:
            posicao.append(i)

    return zip(posicao,usernames,ids,pontosP,difGols)

def definirVencedor(golsMandante, golsVisitante):
    if golsMandante > golsVisitante:
        return 1
    elif golsMandante < golsVisitante:
        return 2
    return 0