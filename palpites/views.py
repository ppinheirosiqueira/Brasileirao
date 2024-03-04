from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpRequest, HttpResponse
from datetime import timedelta
from django.core.paginator import Paginator
from django.db.models import Max
from collections import defaultdict
from unidecode import unidecode
from django.utils import timezone
from user_agents import parse

from .models import User, Time, Partida, Palpite_Partida, Campeonato, EdicaoCampeonato, Rodada, Grupo, Palpite_Campeonato
from .forms import ProfileImageUpdateForm, TimeFavoritoForm
from . import funcoes

# Visão Principal
def home(request : HttpRequest) -> HttpResponse:
    edicoes = funcoes.get_edicoes()
    rodadas = list(Rodada.objects.filter(edicao_campeonato=edicoes[0]).order_by('num'))        

    paginator = Paginator(Partida.objects.filter(dia__gt=timezone.now() - timedelta(days=3)).order_by('dia'), 10)
    primeiro_jogo_nao_ocorrido = Partida.objects.filter(golsMandante=-1).order_by('dia').first()
    if primeiro_jogo_nao_ocorrido:
        jogos_antes = Partida.objects.filter(dia__gt=timezone.now() - timedelta(days=3), dia__lt=primeiro_jogo_nao_ocorrido.dia).count()
        pagina_atual = jogos_antes // 10 + 1
    else:
        pagina_atual = paginator.num_pages
    page = paginator.get_page(pagina_atual)

    user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))

    if (user_agent.is_pc):
        usuariosAux = list(Palpite_Partida.objects.all().values_list("usuario",flat=True).distinct()) 
        usuarios = [User.objects.get(id=usuario).username for usuario in usuariosAux]
        return render(request, "palpites/home.html", {
            "title": "Pepe League",
            "page": page,
            "ranking": funcoes.ranking(edicoes[0].id,0),
            "edicoes": edicoes,
            "rodadas": rodadas,
            "usuarios": usuarios,
        })
    else:
        return render(request, "palpites/home.html", {
            "title": "Pepe League",
            "page": page,
            "ranking": funcoes.ranking(edicoes[0].id,0),
            "edicoes": edicoes,
            "rodadas": rodadas,
        })

# Views de Administração de Usuario
def verLogin(request : HttpRequest) -> HttpResponse:
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

def logout_view(request : HttpRequest) -> HttpResponse:
    logout(request)
    return HttpResponseRedirect(reverse("home"))

def register(request : HttpRequest) -> HttpResponse:
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
def verPagPalpitar(request : HttpRequest) -> HttpResponse:
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
                    aux.vencedor = funcoes.definirVencedor(aux.golsMandante,aux.golsVisitante)
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

def verPartida(request : HttpRequest, id : int, time: str = None) -> HttpResponse:
    partida = Partida.objects.get(id=id)
    anterior, proximo = funcoes.get_anterior_proximo_partida(partida, time)
    palpites, tam_palpites = funcoes.palpite_da_partida(partida)
    
    return render(request, "palpites/partida.html", {
                "title": partida,
                "partida": partida,
                "palpites": palpites,
                "anterior": anterior,
                "proxima": proximo,
                "tamanho_palpites": tam_palpites,
                "time": time,
                "jogoComecou": timezone.now() >= partida.dia,
    })

def verUsuario(request : HttpRequest, id : int) -> HttpResponse:
    usuario = User.objects.get(id=id)
    aGm, aGv, aR, aT = funcoes.accuracy_user(id)
    media = funcoes.rankingTimesNoPerfil(id)

    return render(request, "palpites/usuario.html", {
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

def editarUsuario(request : HttpRequest, id : int) -> HttpResponse:
    if request.user.id != id:
        return HttpResponseRedirect(reverse("home"))

    formImage = ProfileImageUpdateForm(instance=request.user if request.user.is_authenticated else None)
    formTime = TimeFavoritoForm(user=request.user if request.user.is_authenticated else None)
    usuario = User.objects.get(id=id)

    return render(request, "palpites/usuario_editar.html", {
        "title": f"Editar perfil do Usuário - {usuario.username}",
        "usuario": usuario,
        "form": formImage,
        "form2": formTime,
    })

def verTimes(request : HttpRequest) -> HttpResponse:
    times = Time.objects.all().order_by("Nome")
    return render(request, "palpites/times.html",{
        "title": "Times",
        "times": sorted(times, key=lambda time: unidecode(time.Nome)),
    })

def verTime(request : HttpRequest, id : int) -> HttpResponse:
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

def verGrupos(request : HttpRequest) -> HttpResponse:

    

    return render(request, "palpites/grupo.html",{

    })

def verInfo(request : HttpRequest) -> HttpResponse:
    return render(request, "palpites/info.html")

def verCampeonatos(request : HttpRequest) -> HttpResponse:
    edicoes = EdicaoCampeonato.objects.all()
    edicoes_por_campeonato = defaultdict(list)
    for edicao in edicoes:
        edicoes_por_campeonato[edicao.campeonato].append(edicao)

    edicoes_por_campeonato = dict(edicoes_por_campeonato)
    return render(request, "palpites/campeonatos.html", {
        'title': 'Campeonatos',
        'campeonatos': edicoes_por_campeonato,
    })

def verCampeonato(request : HttpRequest, campeonato : int) -> HttpResponse:
    return render(request, "palpites/campeonato.html", {
        'title': Campeonato.objects.get(id=campeonato).nome,
        'edicoes': EdicaoCampeonato.objects.filter(campeonato=campeonato),
    })

def verEdicaoCampeonato(request : HttpRequest, campeonato : int, edicao : int) -> HttpResponse:

    edicao = EdicaoCampeonato.objects.get(campeonato=campeonato,num_edicao=edicao)
    ordem = list(range(1, 21))

    if edicao.campeonato.pontosCorridos:
        # Pegar classificação se for Pontos Corridos
        classificacao = funcoes.classificacao(edicao,1,38,0)
        classificacao = zip(ordem,classificacao)
        # Os jogos serão pegos por rodada
        paginator = Paginator(Partida.objects.filter(Rodada__edicao_campeonato=edicao).order_by('Rodada'), 10)
        primeiro_jogo_nao_ocorrido = Partida.objects.filter(Rodada__edicao_campeonato=edicao).order_by('Rodada').first()
        if primeiro_jogo_nao_ocorrido:
            jogos_antes = Partida.objects.filter(Rodada__edicao_campeonato=edicao, dia__lt=primeiro_jogo_nao_ocorrido.dia).count()
            pagina_atual = jogos_antes // 10 + 1
        else:
            pagina_atual = paginator.num_pages
        page = paginator.get_page(pagina_atual)

        # Checando se existem palpites
        palpites = Palpite_Campeonato.objects.filter(edicao_campeonato=edicao).order_by("usuario", "posicao_prevista")

        # Agrupando os palpites por usuário
        palpites_agrupados = {}
        for palpite in palpites:
            if palpite.usuario.username not in palpites_agrupados:
                palpites_agrupados[palpite.usuario.username] = []
            palpites_agrupados[palpite.usuario.username].append(palpite)
        temPalpite = palpites.exists()
    else:
        # Os jogos serão pegos pelo dia
        paginator = Paginator(Partida.objects.filter(Rodada__edicao_campeonato=edicao).order_by('dia'), 10)
        primeiro_jogo_nao_ocorrido = Partida.objects.filter(Rodada__edicao_campeonato=edicao).order_by('dia').first()
        if primeiro_jogo_nao_ocorrido:
            jogos_antes = Partida.objects.filter(Rodada__edicao_campeonato=edicao, dia__lt=primeiro_jogo_nao_ocorrido.dia).count()
            pagina_atual = jogos_antes // 10 + 1
        else:
            pagina_atual = paginator.num_pages
        page = paginator.get_page(pagina_atual)

    # Independente do tipo, se acabou, ver quem venceu nos palpites
    if edicao.terminou:
        topPepe = [(id, pontosP) for _, _, id, pontosP, _ in list(funcoes.ranking(edicao.id,0))[:3]]
        campeaoPepe = [{'id': usuario[0],'imagem': User.objects.get(id=usuario[0]).profile_image, 'pontos': usuario[1]} for usuario in topPepe]
    else:
        ranking = None
        campeaoPepe = None

    # Independente do tipo, se já começou, mostrar o ranking
    if edicao.comecou:
        ranking = funcoes.ranking(edicao.id,0)

    edicoes = EdicaoCampeonato.objects.filter(campeonato=edicao.campeonato)
    cravadas = funcoes.cravadas(edicao.id)

    if edicao.campeonato.pontosCorridos:
        return render(request, "palpites/campeonato_edicao.html", {
            'edicao': edicao,
            'temPalpite': temPalpite,
            'palpites': palpites_agrupados,
            'ordem': ordem,
            'classificacao': classificacao,
            'rodadas': Rodada.objects.filter(edicao_campeonato=edicao).order_by("num"),
            'campeaoPepe': campeaoPepe,
            'ranking': ranking,
            "page": page,
            "edicoes": edicoes,
            "cravadas": cravadas,
        })
    else:
        return render(request, "palpites/campeonato_edicao.html", {
            'edicao': edicao,
            'temPalpite': False,
            'rodadas': Rodada.objects.filter(edicao_campeonato=edicao).order_by("num"),
            'campeaoPepe': campeaoPepe,
            'ranking': ranking,
            "page": page,
            "edicoes": edicoes,
            "cravadas": cravadas,
        })

def verPalpitarEdicao(request : HttpRequest, edicao : int) -> HttpResponse:
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

def verRodada(request : HttpRequest, campeonato : int, edicao : int, rodada : int) -> HttpResponse:
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
def register_team(request : HttpRequest) -> HttpResponse:
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
        "edicoes": EdicaoCampeonato.objects.filter(terminou=False),
        "times": Time.objects.all().order_by('Nome'),
    })

def register_tournament(request : HttpRequest) -> HttpResponse:
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
def register_team_tournament(request : HttpRequest) -> HttpResponseRedirect:
    times = request.POST.getlist('times')
    for time in times:
        quebra = time.split('_')
        campeonato = Campeonato.objects.get(id=quebra[0])
        edicao = EdicaoCampeonato.objects.get(campeonato=campeonato,id=quebra[1])
        auxTime = Time.objects.get(id=quebra[2])
        edicao.times.add(auxTime)
    return HttpResponseRedirect(reverse("register_team"))

def register_match(request : HttpRequest) -> HttpResponse:
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

def editarPartida(request : HttpRequest) -> HttpResponse:
    return render(request, "palpites/partida_editar.html", {
                "title": "Registrar Partida",
                "partidas": Partida.objects.filter(dia__gt=(timezone.now() - timedelta(days=3))).order_by('dia'),
                "times": Time.objects.all()
    })

def register_matches(request : HttpRequest) -> HttpResponse:
    return render(request, "palpites/register_json.html")

def profile(request : HttpRequest, id : int) -> redirect:
    if request.method == 'POST':
        form = ProfileImageUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
    url = reverse('userView', args=(id,))
    return redirect(url)

def alterar_time_favorito(request : HttpRequest, id : int) -> redirect:
    if request.method == 'POST':
        form = TimeFavoritoForm(request.POST)
        if form.is_valid():
            user = request.user
            user.favorite_team = Time.objects.get(Nome=form.cleaned_data['time_favorito'])
            user.save()
    url = reverse('userView', args=(id,))
    return redirect(url)

def alterar_cor_clara(request : HttpRequest, id : int) -> redirect:
    if request.method == 'POST':
        cor = request.POST["cor"]
        if len(cor) == 7:
            user = request.user
            user.corClara = cor
            user.save()
    url = reverse('userView', args=(id,))
    return redirect(url)

def alterar_cor_escura(request : HttpRequest, id : int) -> redirect:
    if request.method == 'POST':
        cor = request.POST["cor"]
        if len(cor) == 7:
            user = request.user
            user.corEscura = cor
            user.save()
    url = reverse('userView', args=(id,))
    return redirect(url)

# Visões de Erro
def pagina_404(request : HttpRequest, exception ) -> HttpResponse:
    return render(request, 'palpites/404.html', status=404)

def pagina_500(request : HttpRequest) -> HttpResponse:
    return render(request, 'palpites/500.html', status=500)