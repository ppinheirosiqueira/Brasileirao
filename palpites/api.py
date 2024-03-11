from django.http import JsonResponse
from django.utils import timezone
from django.http import HttpRequest
from django.views.decorators.http import require_POST
from json import dumps, loads
from datetime import datetime, timedelta
from django.db.models import Max
from django.core import serializers
from django.core.paginator import Paginator
import os
import importlib.util

from .utils import get_tema, cravadas, avgPontos, modaPalpites, modaResultados, ranking, rankingClassicacao, obter_dados_campeonato, definirVencedor, classificacao, partida_to_json, check_pontuacao_pepe
from .models import Partida, Palpite_Partida, Campeonato, EdicaoCampeonato, Rodada, Time, Palpite_Campeonato, User

def tema(request):
    return {'tema': get_tema(request.user)}

def timesCampeonato(request : HttpRequest, idEdicao : int) -> JsonResponse:
    try:
        times_data, rodadas_data = obter_dados_campeonato(idEdicao)
        return JsonResponse({'times': times_data, 'rodadas': rodadas_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)

def estatisticaCravada(request : HttpRequest, idEdicao : int) -> JsonResponse:
    dados_cravadas = cravadas(idEdicao)
    return JsonResponse(dados_cravadas, safe=False)

def estatisticaAvgPontos(request : HttpRequest, idEdicao : int) -> JsonResponse:
    dados_avgPontos = avgPontos(idEdicao)
    return JsonResponse(dados_avgPontos, safe=False)

def estatisticaModaPalpites(request : HttpRequest, idEdicao : int) -> JsonResponse:
    dados_modaPalpites = modaPalpites(idEdicao)
    return JsonResponse(dados_modaPalpites, safe=False)

def estatisticaModaResultados(request : HttpRequest, idEdicao : int) -> JsonResponse:
    dados_modaResultados = modaResultados(idEdicao)
    return JsonResponse(dados_modaResultados, safe=False)

def estatisticaRankingClassicacao(request : HttpRequest, idEdicao : int) -> JsonResponse:
    dados_rankingClassicacao = rankingClassicacao(idEdicao)
    return JsonResponse(dados_rankingClassicacao, safe=False)

def attResultado(request : HttpRequest, idPartida : int, golsMandante : int, golsVisitante : int) -> JsonResponse:
    partida = Partida.objects.get(id=idPartida)
    if timezone.now() > partida.dia:
        user = request.user
        if user.is_superuser:
            partida.golsMandante = golsMandante
            partida.golsVisitante = golsVisitante
            partida.vencedor = definirVencedor(golsMandante,golsVisitante)
            partida.save()
            return JsonResponse({'mensagem': "Resultado Atualizado"})

    return JsonResponse({'mensagem': "Resultado Não Atualizado"})

def attPalpite(request : HttpRequest, idPartida : int, golsMandante : int, golsVisitante : int) -> JsonResponse:

    partida = Partida.objects.get(id=idPartida)
    if timezone.now() < partida.dia:
        user = request.user

        palpite, criado = Palpite_Partida.objects.get_or_create(usuario=user, 
                                                                partida=partida,
                                                                defaults={
                                                                    'golsMandante': golsMandante, 
                                                                    'golsVisitante': golsVisitante,
                                                                    'vencedor': definirVencedor(golsMandante,golsVisitante)
                                                                })

        if not criado:
            palpite.golsMandante = golsMandante
            palpite.golsVisitante = golsVisitante
            palpite.save()
            sucesso = "Sucesso - Palpite Alterado"
        else:
            sucesso = "Sucesso - Novo palpite criado"

        return JsonResponse({'mensagem': sucesso})

    return JsonResponse({'mensagem': "Falha ao Palpitar"})

def registroPalpiteEdicao(request : HttpRequest, edicao : int, posicao : int, time : str, pc : str) -> JsonResponse:
    campeonato = EdicaoCampeonato.objects.get(id=edicao)

    if pc == "pc":
        equipe = Time.objects.get(escudo__contains = time)
    else:
        equipe = Time.objects.get(Nome = time)


    if request.user.is_authenticated:
        user = request.user

    try:
        palpite, criado = Palpite_Campeonato.objects.get_or_create(
            usuario=user,
            time=equipe,
            edicao_campeonato=campeonato,
            defaults={'posicao_prevista': posicao}
        )

        if not criado:
            palpite.posicao_prevista = posicao
            palpite.save()
            sucesso = "Sucesso - Palpite Alterado"
        else:
            sucesso = "Sucesso - Novo palpite criado"
    except Exception as e:
        print(f"Falhou: {e}")
        sucesso = "Falhou"

    return JsonResponse({'mensagem': sucesso})

def classificacaoTimesEdicao(request : HttpRequest, edicao : int, rodada_inicial : int, rodada_final : int, tipoClassificacao : int) -> JsonResponse:
    dados = classificacao(EdicaoCampeonato.objects.get(id=edicao), rodada_inicial, rodada_final, tipoClassificacao)
    try:
        json_string = dumps(dados)
        json_data = loads(json_string)

        return JsonResponse(json_data, safe=False)
    except:
        return JsonResponse({}, safe=False)

def get_partidas(request : HttpRequest, pagina : int) -> JsonResponse:
    paginator = Paginator(Partida.objects.filter(dia__gt=datetime.now() - timedelta(days=3)).order_by('dia'), 10)
    page_number = request.GET.get('page', pagina)
    page = paginator.get_page(page_number)
    
    partidas = page.object_list
    serialized_partidas = [partida_to_json(partida) for partida in partidas]
    serialized_times = serializers.serialize('json', Time.objects.all())
    
    data = {
        'partidas': serialized_partidas,
        'total': page.paginator.num_pages,
        'times': serialized_times,
    }
    
    return JsonResponse(data)

def get_partidas_edicao(request : HttpRequest, edicao : int, pagina : int) -> JsonResponse:
    edicao = EdicaoCampeonato.objects.get(id=edicao)
    if edicao.campeonato.pontosCorridos:
        paginator = Paginator(Partida.objects.filter(Rodada__edicao_campeonato=edicao).order_by('Rodada'), 10)
        page = paginator.get_page(pagina)
    else:
        paginator = Paginator(Partida.objects.filter(Rodada__edicao_campeonato=edicao).order_by('dia'), 10)
        page = paginator.get_page(pagina)
    
    partidas = page.object_list
    serialized_partidas = [partida_to_json(partida) for partida in partidas]
    serialized_times = serializers.serialize('json', Time.objects.all())
    
    data = {
        'partidas': serialized_partidas,
        'total': page.paginator.num_pages,
        'times': serialized_times,
    }
    
    return JsonResponse(data)

def att_rodadas(request : HttpRequest, edicao : int) -> JsonResponse:
    data = serializers.serialize('json', Rodada.objects.filter(edicao_campeonato__id=edicao).order_by('num'))
    return JsonResponse(data, safe=False)

def get_ranking(request : HttpRequest, edicao : int, rodada : int) -> JsonResponse:
    rankingPreenchido = ranking(edicao, rodada)
    try:
        data_list = [dict(zip(('posicao', 'usernames', 'ids', 'pontosP', 'difGols'), values)) for values in rankingPreenchido]
        json_string = dumps(data_list)
        json_data = loads(json_string)

        return JsonResponse(json_data, safe=False)
    except:
        return JsonResponse({}, safe=False)

def attGrafico(request : HttpRequest, usuarios : str, campeonato : int, rod_Ini : int, rod_Fin : int) -> JsonResponse:
    palpites = Palpite_Partida.objects.filter(partida__Rodada__edicao_campeonato=campeonato,partida__Rodada__num__gte=rod_Ini, partida__Rodada__num__lte=rod_Fin)
    usernames = []
    if usuarios == "todos":
        usernames = palpites.values_list("usuario__username",flat=True).distinct()
    elif usuarios == "voce":
        usernames.append(request.user.username)
        if usernames[0] == '':
            usernames[0]= palpites.order_by('?').first().usuario.username
    elif usuarios[0:5] == "grupo":
        valor = int(usuarios.split("+")[1])
        usernames[0]= User.objects.filter(grupo=valor).values_list("user__username",flat=True)
    else:
        usernames = usuarios.split("+")

    rodadas = list(range(rod_Ini, rod_Fin + 1))

    grafico = {
        "labels": rodadas,
        "datasets":[]
    }

    for username in usernames:
        pontosP = [check_pontuacao_pepe(palpites.filter(partida__Rodada__num=rodada, usuario__username=username)) for rodada in rodadas]
        aux = {
            "label": username,
            "data": pontosP,
            "borderColor": User.objects.get(username=username).corGrafico,
            "fill":False,
        }
        grafico['datasets'].append(aux)

    json_string = dumps(grafico)
    json_data = loads(json_string)

    return JsonResponse(json_data, safe=False)

@require_POST
def registrar_rodada_feita(request : HttpRequest) -> JsonResponse:
    dados_json = loads(request.body)
    campeonato = Campeonato.objects.get(nome=dados_json.get('campeonato'))
    edicao_campeonato = EdicaoCampeonato.objects.get(campeonato=campeonato, edicao=dados_json.get('edicao_campeonato'))
    
    rodada = dados_json['rodada']
    rodada_existente = Rodada.objects.filter(edicao_campeonato=edicao_campeonato,nome=rodada).exists()
    if rodada_existente:
        resposta = {'texto': 'Rodada já registrada'}
        return JsonResponse(resposta, safe=False)
    else:
        maior_rodada = edicao_campeonato.rodada_set.aggregate(Max('num'))['num__max']
        if maior_rodada is not None:
            rodada = Rodada.objects.create(nome=rodada,edicao_campeonato=edicao_campeonato,num=maior_rodada+1)
        else:
            rodada = Rodada.objects.create(nome=rodada,edicao_campeonato=edicao_campeonato,num=1)

    jogos = dados_json['jogos']
    formato_original = "%d/%m/%Y %H:%M"
    for jogo in jogos:
        data_convertida = datetime.strptime(jogo['data'], formato_original).strftime("%Y-%m-%d %H:%M:%S")
        aux = Partida(dia=data_convertida,Rodada=rodada,Mandante=Time.objects.get(Nome=jogo['mandante']),Visitante=Time.objects.get(Nome=jogo['visitante']))
        aux.save()

    resposta = {'texto': 'Rodada registrada com sucesso'}
    return JsonResponse(resposta, safe=False)

@require_POST
def att_partida(request):
    if request.user.is_superuser:
        partida = int(request.POST["idPartida"])
        aux = Partida.objects.get(id=partida)
        gMan = request.POST["gMan"]
        gVis = request.POST["gVis"]
        aux.golsMandante = gMan
        aux.golsVisitante = gVis
        message = "Resultado salvo com Sucesso - "
        if gMan == gVis:
            aux.vencedor = 0
            message = message + "Empate"
        elif gMan > gVis:
            aux.vencedor = 1
            message = message + "Vencedor: Mandante"
        else:
            aux.vencedor = 2
            message = message + "Vencedor: Visitante"
        aux.save()
        return JsonResponse({'mensagem': message}, safe=False)
    else:
        return JsonResponse({'mensagem': "How did you make this request?"}, safe=False)

@require_POST
def att_data_partida(request):
    if request.user.is_superuser:
        partida = int(request.POST["idPartida"])
        aux = Partida.objects.get(id=partida)
        data = request.POST["data"]
        aux.dia = data
        aux.save()
        return JsonResponse({'mensagem': "Data Atualizada com Sucesso"}, safe=False)
    else:
        return JsonResponse({'mensagem': "How did you make this request?"}, safe=False)

@require_POST
def alterar_time_favorito(request : HttpRequest) -> JsonResponse:
    user = request.user
    user.favorite_team = Time.objects.get(id=request.POST["idTime"])
    user.save()
    return JsonResponse({'mensagem': "Time Favorito Atualizado"}, safe=False)

@require_POST
def alterar_tema(request : HttpRequest) -> JsonResponse:
    user = request.user
    if request.POST["tema"] == "default":
        user.corPersonalizada = False    
        user.save()
        return JsonResponse({'mensagem': "Cor atualizada"}, safe=False)

    if request.POST["tema"] == "customizado":
        user.corPersonalizada = True
        user.corFundo = request.POST["fundo"]
        user.corFonte = request.POST["fonte"]
        user.corHover = request.POST["hover"]
        user.corBorda = request.POST["borda"]
        user.corSelecionado = request.POST["selecionado"]
        user.corPontos0 = request.POST["0pontos"]
        user.corPontos1 = request.POST["1pontos"]
        user.corPontos2 = request.POST["2pontos"]
        user.corPontos3 = request.POST["3pontos"]
        user.corFiltro = request.POST["filtro"]
        user.corPersonalizada = True    
        user.save()
        return JsonResponse({'mensagem': "Cor atualizada"}, safe=False)
    
    current_dir = os.path.dirname(os.path.realpath(__file__))
    padroes_path = os.path.join(current_dir, "padroes.py")
    spec = importlib.util.spec_from_file_location("padroes", padroes_path)
    padroes = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(padroes)
    tema = getattr(padroes, request.POST["tema"])
    user.corPersonalizada = True
    user.corFundo = tema['bg-color']
    user.corFonte = tema['font-color']
    user.corHover = tema['hover-color']
    user.corBorda = tema['border-color']
    user.corSelecionado = tema['selecionado-color']
    user.corPontos0 = tema['pontos-0-color']
    user.corPontos1 = tema['pontos-1-color']
    user.corPontos2 = tema['pontos-2-color']
    user.corPontos3 = tema['pontos-3-color']
    user.corFiltro = tema['filter-color']
    user.save()
    return JsonResponse({'mensagem': "Cor atualizada"}, safe=False)
