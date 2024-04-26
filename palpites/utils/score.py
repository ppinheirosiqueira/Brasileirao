from django.db.models import F, Func, Sum
from ..models import Rodada, RodadaModificada

def check_pontuacao_pepe(palpites):
    mandante = palpites.filter(golsMandante=F('partida__golsMandante')).count()
    visitante = palpites.filter(golsVisitante=F('partida__golsVisitante')).count()
    vencedor = palpites.filter(vencedor=F('partida__vencedor')).count()
    return mandante+visitante+vencedor

def check_pontuacao_pepe_grupo(palpites,grupo):
    rodadas_com_palpites = Rodada.objects.filter(partida__palpite_partida__in=palpites).distinct()
    soma = 0
    for rodada in rodadas_com_palpites:
        rodada_modificada = RodadaModificada.objects.filter(rodada=rodada, grupo=grupo).first()
        if rodada_modificada:
            soma += check_pontuacao_pepe(palpites.filter(partida__Rodada=rodada)) * rodada_modificada.modificador
        else:
            soma += check_pontuacao_pepe(palpites.filter(partida__Rodada=rodada))

    return soma

def check_pontuacao_pepe_jogo(palpite):
    mandante = 1 if palpite.golsMandante == palpite.partida.golsMandante else 0
    visitante = 1 if palpite.golsVisitante == palpite.partida.golsVisitante else 0
    vencedor = 1 if palpite.vencedor == palpite.partida.vencedor else 0
    return mandante + visitante + vencedor

def check_diferenca_gols(palpites):
    pontuacao_usuario = palpites.annotate(
        diferenca_mandante=F('golsMandante') - F('partida__golsMandante'),
        diferenca_visitante=F('golsVisitante') - F('partida__golsVisitante')
    ).annotate(
        diferenca_mandante_abs=Func(F('diferenca_mandante'), function='ABS'),
        diferenca_visitante_abs=Func(F('diferenca_visitante'), function='ABS')
    ).annotate(
        diferenca_total=F('diferenca_mandante_abs') + F('diferenca_visitante_abs')
    ).aggregate(
        pontuacao_total=Sum('diferenca_total')
    )['pontuacao_total']

    return pontuacao_usuario or 0