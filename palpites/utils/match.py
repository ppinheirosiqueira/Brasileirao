from ..models import Palpite_Partida, Partida
from django.db.models import Q
from django.db.models.functions import Lower
from .score import check_pontuacao_pepe_jogo

def palpite_da_partida(partida):
    palpites = Palpite_Partida.objects.filter(partida=partida).order_by(Lower("usuario__username"))
    resultados = []
    for palpite in palpites:
        resultados.append(check_pontuacao_pepe_jogo(palpite))
    
    return zip(palpites,resultados), len(palpites)

def get_anterior_proximo_partida(partida, time):
    if not time:
        partidas = list(Partida.objects.all().order_by('dia'))
    else:
        partidas = list(Partida.objects.filter(Q(Mandante__Nome=time) | Q(Visitante__Nome=time)).order_by('dia'))

    indice = partidas.index(partida)
    anterior = partidas[indice - 1].id if indice - 1 >= 0 else None
    proximo = partidas[indice + 1].id if indice + 1 < len(partidas) else None

    return anterior, proximo

