from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
import json
from datetime import datetime, timezone, timedelta
from django.core.paginator import Paginator
from django.core import serializers
from django.db.models import Q, Max, Count
from collections import defaultdict
from django.db.models.functions import Lower
from unidecode import unidecode
from django.utils import timezone

from .models import User, Time, Partida, Palpite_Partida, Campeonato, EdicaoCampeonato, Rodada, Grupo, Palpite_Campeonato
from . import funcoes

from django import forms

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_image']

class TimeFavoritoForm(forms.Form):
    time_favorito = forms.ModelChoiceField(queryset=Time.objects.all(), empty_label="Selecione um time")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TimeFavoritoForm, self).__init__(*args, **kwargs)
        self.fields['time_favorito'].empty_label = "Selecione um time"
        if user:
            self.fields['time_favorito'].initial = user.favorite_team

# Visão Principal
def home(request):
    edicoes = list(EdicaoCampeonato.objects.annotate(num_partidas=Count('rodada__partida')).filter(num_partidas__gt=0).order_by('-id'))
    rodadas = list(Rodada.objects.filter(edicao_campeonato=edicoes[0]).order_by('num'))
    usuariosAux = list(Palpite_Partida.objects.all().values_list("usuario",flat=True).distinct()) 
    usuarios = [User.objects.get(id=usuario).username for usuario in usuariosAux]
    paginator = Paginator(Partida.objects.filter(dia__gt=timezone.now() - timedelta(days=3)).order_by('dia'), 10)
    primeiro_jogo_nao_ocorrido = Partida.objects.filter(golsMandante=-1).order_by('dia').first()
    if primeiro_jogo_nao_ocorrido:
        jogos_antes = Partida.objects.filter(dia__gt=timezone.now() - timedelta(days=3), dia__lt=primeiro_jogo_nao_ocorrido.dia).count()
        pagina_atual = jogos_antes // 10 + 1
    else:
        pagina_atual = paginator.num_pages
    page = paginator.get_page(pagina_atual)
    return render(request, "palpites/home.html", {
        "title": "Pepe League",
        "page": page,
        "ranking": funcoes.ranking(edicoes[0].id,0),
        "edicoes": edicoes,
        "rodadas": rodadas,
        "usuarios": usuarios,
    })

# Views de Administração de Usuario
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("home"))
        else:
            return render(request, "palpites/login.html", {
                "title": "Login",
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "palpites/login.html", {
            "title": "Login"
        })

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("home"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "palpites/register.html", {
                "title": "Register",
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "palpites/register.html", {
                "title": "Register",
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("home"))
    else:
        return render(request, "palpites/register.html",{
            "title": "Register"
        })

# Views padrões
def palpitar(request):
    if request.method == "POST":
        for key, value in request.POST.items():
            if value != '':
                if key.startswith('man_'):
                    team_id, partida_id = key.split('_')
                    if (len(Palpite_Partida.objects.filter(usuario=request.user,partida=partida_id))==1):
                        aux = Palpite_Partida.objects.get(usuario=request.user,partida=partida_id) # Se o usuário já palpitou, não vou criar outro palpite para ele
                        aux.golsMandante = int(value)
                    else:
                        aux = Palpite_Partida(usuario=request.user,partida=Partida.objects.get(id=int(partida_id)),golsMandante=int(value))
                if key.startswith('vis_'):
                    team_id, partida_id = key.split('_')
                    aux.golsVisitante = int(value)
                    if aux.golsMandante == aux.golsVisitante:
                        aux.vencedor = 0
                    elif aux.golsMandante > aux.golsVisitante:
                        aux.vencedor = 1
                    else:
                        aux.vencedor = 2
                    aux.save()
    faltantes = Partida.objects.filter(dia__gt=timezone.now())
    feitas = Palpite_Partida.objects.filter(usuario=request.user.id, partida__dia__gt=timezone.now())
    for palpite in feitas:
        if palpite.partida in faltantes:
            faltantes = faltantes.exclude(id=palpite.partida.id)
    return render(request, "palpites/palpitar.html", {
                "title": "Registrar Resultado",
                "partidas_feitas": feitas,
                "partidas_faltantes": faltantes
    })

def show_match(request,id,time=None):
    partida = Partida.objects.get(id=id)
    if not time:
        partidas = list(Partida.objects.all())
    else:
        partidas = list(Partida.objects.filter(Q(Mandante__Nome=time) | Q(Visitante__Nome=time)).order_by('id'))

    indice = partidas.index(partida)
    anterior = partidas[indice - 1].id if indice - 1 >= 0 else None
    proximo = partidas[indice + 1].id if indice + 1 < len(partidas) else None

    palpites = Palpite_Partida.objects.filter(partida=partida).order_by(Lower("usuario__username"))
    resultados = []
    for palpite in palpites:
        resultados.append(funcoes.check_pontuacao_pepe_jogo(palpite))
    
    zipado = zip(palpites,resultados)
    
    return render(request, "palpites/show_match.html", {
                "title": partida,
                "partida": partida,
                "palpites": zipado,
                "anterior": anterior,
                "proxima": proximo,
                "tamanho_palpites": len(palpites),
                "time": time,
    })

def userView(request,id):
    usuario = User.objects.get(id=id)
    aGm, aGv, aR, aT = funcoes.accuracy_user(id)
    media = funcoes.rankingTimesNoPerfil(id)

    return render(request, "palpites/show_user.html", {
        "title": f"Perfil do Usuário - {usuario.username}",
        "usuario": usuario,
        "average_points_pepe": funcoes.average_pepe(id),
        "total_predictions": len(Palpite_Partida.objects.filter(usuario=id)),
        "accuracy_goals_mandante": aGm,
        "accuracy_goals_visitante": aGv,
        "accuracy_result": aR,
        "accuracy_total": aT,
        "media": media,
    })

def editUserView(request,id):
    if request.user.id != id:
        return HttpResponseRedirect(reverse("home"))

    form = ProfileUpdateForm(instance=request.user if request.user.is_authenticated else None)
    form2 = TimeFavoritoForm(user=request.user if request.user.is_authenticated else None)
    usuario = User.objects.get(id=id)

    return render(request, "palpites/edit_user.html", {
        "title": f"Editar perfil do Usuário - {usuario.username}",
        "usuario": usuario,
        "form": form,
        "form2": form2,
    })

def show_teams(request):
    times = Time.objects.all().order_by("Nome")
    return render(request, "palpites/times.html",{
        "title": "Times",
        "times": sorted(times, key=lambda time: unidecode(time.Nome)),
    })

def show_team(request,id):
    time = Time.objects.get(id=id)
    fas = User.objects.filter(favorite_team=id)
    jogos = Partida.objects.filter(Mandante=id) | Partida.objects.filter(Visitante=id)
    jogos = jogos.order_by("Rodada__edicao_campeonato", "Rodada__num")

    partidas_por_edicao_campeonato = defaultdict(list)

    for jogo in jogos:
        edicao_campeonato = jogo.Rodada.edicao_campeonato
        partidas_por_edicao_campeonato[edicao_campeonato].append(jogo)

    partidas_por_edicao_campeonato = dict(partidas_por_edicao_campeonato)

    if jogos and Palpite_Partida.objects.filter(partida__in=jogos).count() > 0:
        acertos = funcoes.rankingUsuariosNoTime(jogos)
    else:
        acertos = None

    return render(request, "palpites/time.html", {
        "time": time,
        "fas": fas,
        "temJogo": jogos.count() > 0,
        "temAcerto": jogos.exclude(golsMandante=-1).count() > 0,
        "jogos": partidas_por_edicao_campeonato,
        "acertos": acertos,
    })

def groups(request):

    

    return render(request, "palpites/grupo.html",{

    })

def about(request):
    return render(request, "palpites/about.html")

def campeonatos(request):
    edicoes = EdicaoCampeonato.objects.all()
    edicoes_por_campeonato = defaultdict(list)
    for edicao in edicoes:
        edicoes_por_campeonato[edicao.campeonato].append(edicao)

    edicoes_por_campeonato = dict(edicoes_por_campeonato)
    return render(request, "palpites/campeonatos.html", {
        'title': 'Campeonatos',
        'campeonatos': edicoes_por_campeonato,
    })

def campeonato(request,campeonato):
    return render(request, "palpites/campeonato.html", {
        'title': Campeonato.objects.get(id=campeonato).nome,
        'edicoes': EdicaoCampeonato.objects.filter(campeonato=campeonato),
    })

def edicao(request,campeonato,edicao):
    edicao = EdicaoCampeonato.objects.get(campeonato=campeonato,num_edicao=edicao)
    classificacao = funcoes.classificacao(edicao,1,38,0)
    ordem = list(range(1, 21))

    if edicao.campeonato.pontosCorridos:
        paginator = Paginator(Partida.objects.filter(Rodada__edicao_campeonato=edicao).order_by('Rodada'), 10)
        primeiro_jogo_nao_ocorrido = Partida.objects.filter(Rodada__edicao_campeonato=edicao).order_by('Rodada').first()
        if primeiro_jogo_nao_ocorrido:
            jogos_antes = Partida.objects.filter(Rodada__edicao_campeonato=edicao, dia__lt=primeiro_jogo_nao_ocorrido.dia).count()
            pagina_atual = jogos_antes // 10 + 1
        else:
            pagina_atual = paginator.num_pages
        page = paginator.get_page(pagina_atual)
    else:
        paginator = Paginator(Partida.objects.filter(Rodada__edicao_campeonato=edicao).order_by('dia'), 10)
        primeiro_jogo_nao_ocorrido = Partida.objects.filter(Rodada__edicao_campeonato=edicao).order_by('dia').first()
        if primeiro_jogo_nao_ocorrido:
            jogos_antes = Partida.objects.filter(Rodada__edicao_campeonato=edicao, dia__lt=primeiro_jogo_nao_ocorrido.dia).count()
            pagina_atual = jogos_antes // 10 + 1
        else:
            pagina_atual = paginator.num_pages
        page = paginator.get_page(pagina_atual)

    if edicao.terminou:
        ranking = funcoes.ranking(edicao.id,0)
        topPepe = [(id, pontosP) for _, _, id, pontosP, _ in list(funcoes.ranking(edicao.id,0))[:3]]
        campeaoPepe = [{'id': usuario[0],'imagem': User.objects.get(id=usuario[0]).profile_image, 'pontos': usuario[1]} for usuario in topPepe]
    else:
        ranking = None
        campeaoPepe = None

    edicoes = EdicaoCampeonato.objects.filter(campeonato=edicao.campeonato)

    palpites = Palpite_Campeonato.objects.filter(usuario=request.user, edicao_campeonato=edicao).order_by("posicao_prevista")
    if palpites.exists():
        classificacao = zip(palpites,ordem,classificacao)
        temPalpite = True
    else:
        classificacao = zip(ordem,classificacao)
        temPalpite = False

    return render(request, "palpites/edicao.html", {
        'edicao': edicao,
        'temPalpite': temPalpite,
        'classificacao': classificacao,
        'rodadas': Rodada.objects.filter(edicao_campeonato=edicao).order_by("num"),
        'campeaoPepe': campeaoPepe,
        'ranking': ranking,
        "page": page,
        "edicoes": edicoes,
    })

def palpitarEdicao(request,edicao):
    edicao = EdicaoCampeonato.objects.get(id=edicao)
    if not edicao.comecou:
        times = edicao.times.all()
        times_10_a_frente = list(times)[10:] + [None]*10
        return render(request, "palpites/palpitarEdicao.html", {
            'edicao': edicao,
            'times': list(zip(range(1, 11), times[:10], range(11, 21), times_10_a_frente)),
            'range': range(1,21),
        })
    return HttpResponseRedirect(reverse("home"))

def rodada(request,campeonato,edicao,rodada):
    edicao = EdicaoCampeonato.objects.get(campeonato=campeonato,num_edicao=edicao)
    rodadaAtual = Rodada.objects.get(edicao_campeonato=edicao,num=rodada)
    try:
        anterior = Rodada.objects.get(edicao_campeonato=edicao, num=rodada-1)
    except:
        anterior = None
    try:
        proxima = Rodada.objects.get(edicao_campeonato=edicao, num=rodada+1)
    except:
        proxima = None
    return render(request, "palpites/rodada.html", {
        'edicao': edicao,
        'anterior': anterior,
        'proxima': proxima,
        'partidas': Partida.objects.filter(Rodada=rodadaAtual).order_by('dia'),
        'rodada': rodadaAtual,
    })

# Views de Administração
def register_team(request):
    message = ""
    if request.method == "POST":
        nome = request.POST["time"]
        escudo = request.POST["escudo"]
        aux = Time(Nome=nome,escudo='media/Escudos/' + escudo)
        aux.save()
        message = f'{nome} registrado com sucesso'
    return render(request, "palpites/register_team.html", {
        "title": "Registrar Time",
        "message": message,
        "edicoes": EdicaoCampeonato.objects.filter(comecou=False),
        "times": Time.objects.all().order_by('Nome'),
    })

def register_tournament(request):
    message = ""
    if request.method == "POST":
        try: 
            pontosCorridos = request.POST["pontosCorridos"]
        except:
            pontosCorridos = False
        campeonato = Campeonato.objects.get_or_create(nome=request.POST["campeonato"],pontosCorridos=pontosCorridos)[0]
        maiorNum = EdicaoCampeonato.objects.filter(campeonato=campeonato).aggregate(Max('num_edicao'))['num_edicao__max']
        if maiorNum is None:
            maiorNum = 0
        edicao = EdicaoCampeonato.objects.get_or_create(campeonato=campeonato,edicao=request.POST["edicao"],num_edicao=maiorNum+1)[0]
        message = f"{campeonato.nome} - {edicao.edicao} criado com Sucesso"
    return render(request, "palpites/register_tournament.html",{
        "message": message,
        "title": "Registrar Torneio",
    })

@require_POST
def register_team_tournament(request):
    times = request.POST.getlist('times')
    for time in times:
        quebra = time.split('_')
        campeonato = Campeonato.objects.get(id=quebra[0])
        edicao = EdicaoCampeonato.objects.get(campeonato=campeonato,id=quebra[1])
        auxTime = Time.objects.get(id=quebra[2])
        edicao.times.add(auxTime)
    return HttpResponseRedirect(reverse("register_team"))

def register_match(request):
    message = ""
    if request.method == "POST":
        mandante = int(request.POST["mandante"])
        visitante = int(request.POST["visitante"])

        if mandante == visitante:
            message = "<h3>Não tem como um time jogar contra ele mesmo</h3>"
            return render(request, "palpites/register_match.html", {
                        "message": message,
                        "title": "Registrar Partida",
                        "campeonatos": EdicaoCampeonato.objects.filter(terminou=False),
            })
        
        rodada = request.POST["rodada"]

        if rodada != "0":
            rodada = Rodada.objects.get(id=rodada)
            lista_partidas = Partida.objects.filter(Rodada=rodada)

            for partida in lista_partidas:
                if mandante == partida.Mandante.id or mandante == partida.Visitante.id or visitante == partida.Mandante.id or visitante == partida.Visitante.id:
                    message = "<h3>Não tem como um time fazer dois jogos na mesma rodada</h3>"
                    return render(request, "palpites/register_match.html", {
                            "message": message,
                            "title": "Registrar Partida",
                            "campeonatos": EdicaoCampeonato.objects.filter(terminou=False),
                    })
        else:
            campeonato = int(request.POST["campeonato"])
            rodada = Rodada(num=request.POST["numRodada"],nome=request.POST["nomeRodada"],edicao_campeonato_id=campeonato)
            rodada.save()

        date = request.POST["date"]
        aux = Partida(dia=date,Rodada=rodada,Mandante=Time.objects.get(id=mandante),Visitante=Time.objects.get(id=visitante))
        aux.save()
        message = "<h3>Jogo Salvo com Sucesso</h3>"
    return render(request, "palpites/register_match.html", {
                "message": message,
                "title": "Registrar Partida",
                "campeonatos": EdicaoCampeonato.objects.filter(terminou=False),
    })

@require_POST
def registrar_rodada_feita(request):
    dados_json = json.loads(request.body)
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

def change_match(request):
    limite_data = datetime.now() - timedelta(days=3)
    message = ""
    if request.method == "POST":
        partida = int(request.POST["partida"])
        aux = Partida.objects.get(id=partida)
        data = request.POST["data"]
        if data != "":
            aux.dia = data
        else:
            gMan = request.POST["gMan"]
            gVis = request.POST["gVis"]
            aux.golsMandante = gMan
            aux.golsVisitante = gVis
            message = "<h3>Resultado salvo com Sucesso<br>"
            if gMan == gVis:
                aux.vencedor = 0
                message = message + "Empate</h3>"
            elif gMan > gVis:
                aux.vencedor = 1
                message = message + "Vencedor: Mandante</h3>"
            else:
                aux.vencedor = 2
                message = message + "Vencedor: Visitante</h3>"
        aux.save()
    return render(request, "palpites/change_match.html", {
                "message": message,
                "title": "Registrar Partida",
                "partidas": Partida.objects.filter(dia__gt=limite_data).order_by('dia'),
                "times": Time.objects.all()
    })

def register_matches(request):
    return render(request, "palpites/register_json.html")

# Views de Banco de Dados
def ranking(request, edicao, rodada):
    rankingPreenchido = funcoes.ranking(edicao, rodada)
    try:
        data_list = [dict(zip(('posicao', 'usernames', 'ids', 'pontosP', 'difGols'), values)) for values in rankingPreenchido]
        json_string = json.dumps(data_list)
        json_data = json.loads(json_string)

        return JsonResponse(json_data, safe=False)
    except:
        return JsonResponse({}, safe=False)

def att_rodadas(request,edicao):
    data = serializers.serialize('json', Rodada.objects.filter(edicao_campeonato__id=edicao).order_by('num'))
    return JsonResponse(data, safe=False)

def userResult(request,usuarios,campeonato,rod_Ini,rod_Fin):
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

    if not request.user.is_authenticated or request.user.dark == True: # Por pior que seja repetir o código, é melhor do que fazer essa comparação de fundo claro/escuro para cada usuário
        for username in usernames:
            pontosP = [funcoes.check_pontuacao_pepe(palpites.filter(partida__Rodada__num=rodada, usuario__username=username)) for rodada in rodadas]
            aux = {
                "label": username,
                "data": pontosP,
                "borderColor": User.objects.get(username=username).corClara,
                "fill":False,
            }
            grafico['datasets'].append(aux)
    else:
        for username in usernames:
            pontosP = [funcoes.check_pontuacao_pepe(palpites.filter(partida__Rodada__num=rodada, usuario__username=username)) for rodada in rodadas]
            aux = {
                "label": username,
                "data": pontosP,
                "borderColor": User.objects.get(username=username).corEscura,
                "fill":False,
            }
            grafico['datasets'].append(aux)

    json_string = json.dumps(grafico)
    json_data = json.loads(json_string)

    # Retorne os dados em formato JSON
    return JsonResponse(json_data, safe=False)

def profile(request,id):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
    url = reverse('userView', args=(id,))
    return redirect(url)

def alterar_time_favorito(request,id):
    if request.method == 'POST':
        form = TimeFavoritoForm(request.POST)
        if form.is_valid():
            user = request.user
            user.favorite_team = Time.objects.get(Nome=form.cleaned_data['time_favorito'])
            user.save()
    url = reverse('userView', args=(id,))
    return redirect(url)

def alterar_cor_clara(request,id):
    if request.method == 'POST':
        cor = request.POST["cor"]
        if len(cor) == 7:
            user = request.user
            user.corClara = cor
            user.save()
    url = reverse('userView', args=(id,))
    return redirect(url)

def alterar_cor_escura(request,id):
    if request.method == 'POST':
        cor = request.POST["cor"]
        if len(cor) == 7:
            user = request.user
            user.corEscura = cor
            user.save()
    url = reverse('userView', args=(id,))
    return redirect(url)

def alterar_tema(request,valor):
    if valor == 0:
        request.user.dark = False
    else:
        request.user.dark = True
    request.user.save()
    return JsonResponse({"sucesso": "sim"}, safe=False)

def get_partidas(request, pagina):
    paginator = Paginator(Partida.objects.filter(dia__gt=datetime.now() - timedelta(days=3)).order_by('dia'), 10)
    page_number = request.GET.get('page', pagina)
    page = paginator.get_page(page_number)
    
    partidas = page.object_list
    serialized_partidas = [funcoes.partida_to_json(partida) for partida in partidas]
    serialized_times = serializers.serialize('json', Time.objects.all())
    
    data = {
        'partidas': serialized_partidas,
        'total': page.paginator.num_pages,
        'times': serialized_times,
    }
    
    return JsonResponse(data)

def get_partidas_edicao(request, edicao, pagina):
    edicao = EdicaoCampeonato.objects.get(id=edicao)
    if edicao.campeonato.pontosCorridos:
        paginator = Paginator(Partida.objects.filter(Rodada__edicao_campeonato=edicao).order_by('Rodada'), 10)
        page = paginator.get_page(pagina)
    else:
        paginator = Paginator(Partida.objects.filter(Rodada__edicao_campeonato=edicao).order_by('dia'), 10)
        page = paginator.get_page(pagina)
    
    partidas = page.object_list
    serialized_partidas = [funcoes.partida_to_json(partida) for partida in partidas]
    serialized_times = serializers.serialize('json', Time.objects.all())
    
    data = {
        'partidas': serialized_partidas,
        'total': page.paginator.num_pages,
        'times': serialized_times,
    }
    
    return JsonResponse(data)

def classificacao(request, edicao, rodada_inicial, rodada_final, tipoClassificacao):
    classificacao = funcoes.classificacao(EdicaoCampeonato.objects.get(id=edicao), rodada_inicial, rodada_final, tipoClassificacao)
    try:
        json_string = json.dumps(classificacao)
        json_data = json.loads(json_string)

        return JsonResponse(json_data, safe=False)
    except:
        return JsonResponse({}, safe=False)
    
def timesCampeonato(request, edicao):
    try:
        campeonato = EdicaoCampeonato.objects.get(id=edicao)
        
        times = campeonato.times.all()
        times_data = [{'id': time.id, 'nome': time.Nome} for time in times]

        rodadas = Rodada.objects.filter(edicao_campeonato=campeonato)
        rodadas_data = [{'id': rodada.id, 'nome': rodada.nome} for rodada in rodadas]

        return JsonResponse({'times': times_data, 'rodadas': rodadas_data})
    except Time.DoesNotExist:
        return JsonResponse({'error': 'Times não encontrados para esta edição de campeonato'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def registroPalpiteEdicao(request, edicao, posicao, time, pc):
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
