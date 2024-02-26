from .models import User, Time, Partida, Palpite_Partida
from django.db.models import F, Q, Sum, Count, Value, Func
from datetime import datetime, timezone, timedelta
from django.db.models.functions import Coalesce

def check_pontuacao_pepe(palpites):
    mandante = palpites.filter(golsMandante=F('partida__golsMandante')).count()
    visitante = palpites.filter(golsVisitante=F('partida__golsVisitante')).count()
    vencedor = palpites.filter(vencedor=F('partida__vencedor')).count()
    return mandante+visitante+vencedor

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

# Função de ranking
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
    for i, _ in enumerate(usernames, start=0):
        if i < len(usernames) and (pontosP[i] == pontosP[i - 1] and difGols[i] == difGols[i - 1]):
            posicao.append("-")
        else:
            posicao.append(i+1)

    return zip(posicao,usernames,ids,pontosP,difGols)

def rankingUsuariosNoTime(jogos):
    palpites = Palpite_Partida.objects.filter(partida__in=jogos).exclude(partida__golsMandante=-1, partida__golsVisitante=-1)
    usuariosAux = list(set(palpites.values_list("usuario", flat=True)))
    usuarios = User.objects.filter(id__in=usuariosAux)
    porcentagemP = [100*check_pontuacao_pepe(palpites.filter(usuario=usuario))/(3*palpites.filter(usuario=usuario).count()) for usuario in usuarios]
    difGols = [check_diferenca_gols(palpites.filter(usuario=usuario).exclude(partida__golsMandante=-1, partida__golsVisitante=-1))/palpites.filter(usuario=usuario).exclude(partida__golsMandante=-1, partida__golsVisitante=-1).count() for usuario in usuarios]
    usernames = [usuario.username for usuario in usuarios]
    ids = [usuario.id for usuario in usuarios]
    numJogos = [palpites.filter(usuario=usuario).count() for usuario in usuarios]

    return sorted(zip(usernames,ids,porcentagemP,difGols, numJogos), key=lambda x: (-x[2],x[3]))

def rankingTimesNoPerfil(id):
    palpites = Palpite_Partida.objects.filter(usuario=id).exclude(partida__golsMandante=-1, partida__golsVisitante=-1)
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

def campeaoPalpite(edicao):
    rankingPepe = ranking(edicao.id,0)
    rankingCravadas = cravadas(edicao)

    listaPepe = list(rankingPepe)
    topPepe = (
        listaPepe[0][:5],
        listaPepe[1][:5],
        listaPepe[2][:5],
    )

    listaCravadas = list(rankingCravadas)[0:3]
    return topPepe, listaCravadas

def cravadas(edicao):
    palpites = Palpite_Partida.objects.filter(partida__Rodada__edicao_campeonato=edicao)
    palpites_cravados = palpites.filter(
        golsMandante=F('partida__golsMandante'),
        golsVisitante=F('partida__golsVisitante'),
        vencedor=F('partida__vencedor')
    )

    cravadas_por_usuario = palpites_cravados.values('usuario__username').annotate(cravadas=Count('id')).order_by('-cravadas')

    return cravadas_por_usuario

# Função % acertos do jogador
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

# Função Média de Pontos Pepe
def average_pepe(id_usuario):
    palpites = Palpite_Partida.objects.filter(usuario=id_usuario).exclude(partida__golsMandante=-1, partida__golsVisitante=-1)
    if len(palpites) == 0:
        return 0
    soma = check_pontuacao_pepe(palpites)
    return soma/(len(palpites))

# Função Classificação Pontos Corridos
def classificacao(edicao, rodada_inicial, rodada_final, tipoClassificacao):
    timezone_offset = -3.0 
    tzinfo = timezone(timedelta(hours=timezone_offset))
    partidas = Partida.objects.filter(
        Rodada__edicao_campeonato=edicao,
        Rodada__num__gte=rodada_inicial,
        Rodada__num__lte=rodada_final,
        dia__lt=datetime.now(tzinfo)
    )

    times = edicao.times.all()

    times_mandante = times
    times_visitante = times

    # Calcule as estatísticas para as partidas em casa
    if tipoClassificacao == 0 or tipoClassificacao == 1:
        times_mandante = times.annotate(
            jogos_mandante=Count('mandante', filter=Q(mandante__in=partidas)),
            vitorias_mandante=Count('mandante', filter=Q(mandante__in=partidas, mandante__vencedor=1)),
            empates_mandante=Count('mandante', filter=Q(mandante__in=partidas, mandante__vencedor=0)),
            gols_pro_mandante=Coalesce(Sum('mandante__golsMandante', filter=Q(mandante__in=partidas)), Value(0)),
            gols_contra_mandante=Coalesce(Sum('mandante__golsVisitante', filter=Q(mandante__in=partidas)), Value(0)),
        )

    # Calcule as estatísticas para as partidas fora de casa
    if tipoClassificacao == 0 or tipoClassificacao == 2:
        times_visitante = times.annotate(
            jogos_visitante=Count('visitante', filter=Q(visitante__in=partidas)),
            vitorias_visitante=Count('visitante', filter=Q(visitante__in=partidas, visitante__vencedor=2)),
            empates_visitante=Count('visitante', filter=Q(visitante__in=partidas, visitante__vencedor=0)),
            gols_pro_visitante=Coalesce(Sum('visitante__golsVisitante', filter=Q(visitante__in=partidas)), Value(0)),
            gols_contra_visitante=Coalesce(Sum('visitante__golsMandante', filter=Q(visitante__in=partidas)), Value(0)),
        )

    estatisticas_times = []

    for time in times:
        if tipoClassificacao == 0:
            time_mandante = times_mandante.get(id=time.id)
            time_visitante = times_visitante.get(id=time.id)

            jogos = time_mandante.jogos_mandante + time_visitante.jogos_visitante
            vitorias = time_mandante.vitorias_mandante + time_visitante.vitorias_visitante
            empates = time_mandante.empates_mandante + time_visitante.empates_visitante
            gols_pro = time_mandante.gols_pro_mandante + time_visitante.gols_pro_visitante
            gols_contra = time_mandante.gols_contra_mandante + time_visitante.gols_contra_visitante
        elif tipoClassificacao == 1:
            time_mandante = times_mandante.get(id=time.id)
            jogos = time_mandante.jogos_mandante
            vitorias = time_mandante.vitorias_mandante
            empates = time_mandante.empates_mandante
            gols_pro = time_mandante.gols_pro_mandante
            gols_contra = time_mandante.gols_contra_mandante
        else:
            time_visitante = times_visitante.get(id=time.id)
            jogos = time_visitante.jogos_visitante
            vitorias = time_visitante.vitorias_visitante
            empates = time_visitante.empates_visitante
            gols_pro = time_visitante.gols_pro_visitante
            gols_contra = time_visitante.gols_contra_visitante

        saldo_gols = gols_pro - gols_contra
        pontos = vitorias * 3 + empates
        aproveitamento = (pontos / (jogos * 3)) * 100 if jogos > 0 else 0
        derrotas = jogos - vitorias - empates

        estatisticas_time = {
            'time': time.Nome,
            'pontos': pontos,
            'jogos': jogos,
            'vitorias': vitorias,
            'empates': empates,
            'derrotas': derrotas,
            'gols_pro': gols_pro,
            'gols_contra': gols_contra,
            'saldo_gols': saldo_gols,
            'aproveitamento': aproveitamento,
        }

        estatisticas_times.append(estatisticas_time)

    # Ordenar a lista de dicionários com base nos pontos, vitórias, saldo de gols e gols pró
    estatisticas_times.sort(key=lambda x: (-x['pontos'], -x['vitorias'], -x['saldo_gols'], -x['gols_pro']))

    return estatisticas_times

def partida_to_json(partida):
    return {
        'pk': partida.pk,
        'Mandante': partida.Mandante.id,
        'Visitante': partida.Visitante.id,
        'golsMandante': partida.golsMandante,
        'golsVisitante': partida.golsVisitante,
        'Rodada': f'{partida.Rodada.edicao_campeonato.campeonato} - {partida.Rodada.nome}',
    }