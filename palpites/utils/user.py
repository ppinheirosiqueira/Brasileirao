from ..models import Palpite_Partida, Time
from .score import check_pontuacao_pepe, check_diferenca_gols
from django.db.models import F, Q

def get_tema(user):
    if user.is_authenticated:
        return user.colors()
    else:
        return None

def accuracy_user(id_usuario):
    palpites = Palpite_Partida.objects.filter(usuario=id_usuario).exclude(partida__golsMandante=-1, partida__golsVisitante=-1)
    if len(palpites) == 0:
        return 0, 0, 0, 0
    aGm = 100*palpites.filter(golsMandante=F('partida__golsMandante')).count()/len(palpites)
    aGv = 100*palpites.filter(golsVisitante=F('partida__golsVisitante')).count()/len(palpites)
    aR = 100*palpites.filter(vencedor=F('partida__vencedor')).count()/len(palpites)
    aT = 100 * palpites.filter(
        golsMandante=F('partida__golsMandante'),
        golsVisitante=F('partida__golsVisitante'),
        vencedor=F('partida__vencedor')
    ).count() / len(palpites)    
    return aGm, aGv, aR, aT

def average_pepe(id_usuario):
    palpites = Palpite_Partida.objects.filter(usuario=id_usuario).exclude(partida__golsMandante=-1, partida__golsVisitante=-1)
    if len(palpites) == 0:
        return 0
    soma = check_pontuacao_pepe(palpites)
    return soma/(len(palpites))

def rankingTimesNoPerfil(id:int,edicao:int):
    if edicao == 0:
        palpites = Palpite_Partida.objects.filter(usuario=id).exclude(partida__golsMandante=-1, partida__golsVisitante=-1)
    else:
        palpites = Palpite_Partida.objects.filter(usuario=id,partida__Rodada__edicao_campeonato=edicao).exclude(partida__golsMandante=-1, partida__golsVisitante=-1)
    if not palpites:
        return None
    times = Time.objects.filter(id__in=(list(palpites.values_list('partida__Mandante', flat=True).distinct().order_by("partida__Mandante__Nome")) + list(palpites.values_list('partida__Visitante', flat=True).distinct().order_by("partida__Visitante__Nome"))))
    porcentagemP = []
    difGols = []
    numJogos = []

    for time in times:
        palpites_time = palpites.filter(
            Q(partida__Mandante=time) | Q(partida__Visitante=time)
        )
        pontuacaoP = check_pontuacao_pepe(palpites_time)
        total = 3*palpites_time.count()
        porcentagemP.append(100*pontuacaoP/total)
        difGols.append(check_diferenca_gols(palpites_time)/palpites_time.count())
        numJogos.append(palpites_time.count())

    imagem = [time.escudo for time in times]
    ids = [time.id for time in times]

    return sorted(zip(imagem,ids,porcentagemP,difGols,numJogos), key=lambda x: (-x[2], x[3]))