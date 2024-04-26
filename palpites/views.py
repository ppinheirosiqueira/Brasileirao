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
import json

from .models import User, Time, Partida, Palpite_Partida, Campeonato, EdicaoCampeonato, Rodada, Grupo, Palpite_Campeonato, RodadaModificada, Mensagem
from .forms import ProfileImageUpdateForm
from .utils import rankingGrupo, cravadas, get_edicoes, get_edicoes_usuario, ranking, definirVencedor, get_anterior_proximo_partida, accuracy_user, average_pepe, rankingUsuariosNoTime, palpite_da_partida, rankingTimesNoPerfil, classificacao

# Visão Principal
def home(request : HttpRequest) -> HttpResponse:
    edicoes = get_edicoes()
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
        usuariosAux = list(Palpite_Partida.objects.filter(partida__Rodada__edicao_campeonato=edicoes[0].id).values_list("usuario",flat=True).distinct()) 
        usuarios = [User.objects.get(id=usuario).username for usuario in usuariosAux]
        grupos = Grupo.objects.filter(edicao=edicoes[0],usuarios=request.user)
        return render(request, "palpites/home.html", {
            "title": "Pepe League",
            "page": page,
            "ranking": ranking(edicoes[0].id,0),
            "edicoes": edicoes,
            "grupos": grupos,
            "rodadas": rodadas,
            "usuarios": usuarios,
        })
    else:
        return render(request, "palpites/home.html", {
            "title": "Pepe League",
            "page": page,
            "ranking": ranking(edicoes[0].id,0),
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
                    aux.vencedor = definirVencedor(aux.golsMandante,aux.golsVisitante)
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
    anterior, proximo = get_anterior_proximo_partida(partida, time)
    palpites, tam_palpites = palpite_da_partida(partida)
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
    aGm, aGv, aR, aT = accuracy_user(id)
    edicoes = get_edicoes_usuario(id)
    if len(edicoes) > 0:
        media = rankingTimesNoPerfil(id,edicoes[0].id)
    else:
        media = None

    if request.user.id == id:
        formImage = ProfileImageUpdateForm(instance=request.user if request.user.is_authenticated else None)

        return render(request, "palpites/usuario.html", {
            "title": f"Perfil do Usuário - {usuario.username}",
            "usuario": usuario,
            "average_points_pepe": average_pepe(id),
            "total_predictions": len(Palpite_Partida.objects.filter(usuario=id)),
            "accuracy_goals_mandante": aGm,
            "accuracy_goals_visitante": aGv,
            "accuracy_result": aR,
            "accuracy_total": aT,
            "media": media,
            "formImage": formImage,
            "times": sorted(Time.objects.all(), key=lambda time: unidecode(time.Nome)),
            "edicoes": edicoes,
        })
    else:
        return render(request, "palpites/usuario.html", {
            "title": f"Perfil do Usuário - {usuario.username}",
            "usuario": usuario,
            "average_points_pepe": average_pepe(id),
            "total_predictions": len(Palpite_Partida.objects.filter(usuario=id)),
            "accuracy_goals_mandante": aGm,
            "accuracy_goals_visitante": aGv,
            "accuracy_result": aR,
            "accuracy_total": aT,
            "media": media,
            "edicoes": edicoes,
        })

def editarUsuario(request : HttpRequest, id : int) -> HttpResponse:
    if request.user.id != id:
        return HttpResponseRedirect(reverse("home"))

    formImage = ProfileImageUpdateForm(instance=request.user if request.user.is_authenticated else None)
    usuario = User.objects.get(id=id)

    return render(request, "palpites/usuario_editar.html", {
        "title": f"Editar perfil do Usuário - {usuario.username}",
        "usuario": usuario,
        "form": formImage,
        "times": sorted(Time.objects.all(), key=lambda time: unidecode(time.Nome)),
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
        acertos = rankingUsuariosNoTime(jogos)
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
    return render(request, "palpites/grupos.html",{
        'grupos': Grupo.objects.filter(usuarios=request.user.id),
        'edicoes': EdicaoCampeonato.objects.filter(terminou=False),
    })

def verGrupo(request: HttpRequest, id:int) -> HttpResponse:
    grupo = Grupo.objects.get(id=id)
    
    if not request.user.is_authenticated or not Grupo.objects.filter(usuarios=request.user).filter(id=grupo.id).exists():
        return HttpResponseRedirect(reverse("home"))
    
    if  grupo.edicao.comecou:
        rankingJogadores = rankingGrupo(grupo.id)
        if rankingJogadores is not None:
            rankingJogadores = list(rankingJogadores)
    else:
        rankingJogadores = None

    if grupo.edicao.terminou:
        topPepe = [(id, pontosP) for _, _, id, pontosP, _ in list(rankingJogadores)[:3]]
        campeaoPepe = [{'id': usuario[0],'imagem': User.objects.get(id=usuario[0]).profile_image, 'pontos': usuario[1]} for usuario in topPepe]
    else:
        campeaoPepe = None

    temPalpite = False
    
    for usuario in grupo.usuarios.all():
        if len(Palpite_Campeonato.objects.filter(edicao_campeonato=grupo.edicao,usuario=usuario)) > 0:
            temPalpite = True
            break
    
    cravadasJogadores = cravadas(grupo.edicao.id,grupo.id)
    rodadas = Rodada.objects.filter(edicao_campeonato=grupo.edicao)
    return render(request, "palpites/grupo.html",{
        'grupo': grupo,
        'dono': grupo.dono == request.user,
        'ranking': rankingJogadores,
        'temPalpite': temPalpite,
        'cravadas': cravadasJogadores,
        'campeaoPepe': campeaoPepe,
        'rodadas': rodadas,
        'rodadasModificadas': RodadaModificada.objects.filter(rodada__in=rodadas),
        'userList': json.dumps(list(User.objects.all().exclude(id__in=grupo.usuarios.all()).values_list("username",flat=True))),
    })

def sairGrupo(request: HttpRequest, idGrupo:int) -> HttpResponse:
    grupo = Grupo.objects.get(id=idGrupo)
    grupo.usuarios.remove(request.user)

    if len(grupo.usuarios.all()) == 0:
        grupo.delete()
        return HttpResponseRedirect(reverse("groups"))
    
    if grupo.dono == request.user:
        grupo.dono = grupo.usuarios.all().order_by('?').first()
    
    grupo.save()

    return HttpResponseRedirect(reverse("groups"))

def mensagens(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("home"))

    return render(request, "palpites/mensagens.html",{
        'mensagens': Mensagem.objects.filter(to_user=request.user).order_by('-id')
    })

def mensagemAberta(request: HttpRequest, idMensagem:int) -> HttpResponse:
    return render(request, "palpites/mensagem.html",{
        'mensagem': Mensagem.objects.get(id=idMensagem)
    })

def mensagemGlobal(request: HttpRequest) -> HttpResponse:
    return render(request, "palpites/mensagemGlobal.html",{
    })

def processarMensagemGlobal(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        conteudo = request.POST.get('conteudo')

        for user in User.objects.all():
            mensagem = Mensagem(to_user=user,from_user=request.user,titulo=titulo,conteudo=conteudo)
            mensagem.save()
            
    return HttpResponseRedirect(reverse("mensagemGlobal"))

def verInfo(request : HttpRequest) -> HttpResponse:
    return render(request, "palpites/info.html", {})

def verCampeonatos(request : HttpRequest) -> HttpResponse:
    edicoes = EdicaoCampeonato.objects.all()
    edicoes_por_campeonato = defaultdict(list)
    for edicao in edicoes:
        edicoes_por_campeonato[edicao.campeonato].append(edicao)

    edicoes_por_campeonato = dict(edicoes_por_campeonato)
    return render(request, "palpites/campeonatos.html", {
        'title': 'Campeonatos',
        'campeonatos': edicoes_por_campeonato    
    })

def verCampeonato(request : HttpRequest, campeonato : int) -> HttpResponse:
    return render(request, "palpites/campeonato.html", {
        'title': Campeonato.objects.get(id=campeonato).nome,
        'edicoes': EdicaoCampeonato.objects.filter(campeonato=campeonato),
    })

def verEdicaoCampeonato(request : HttpRequest, campeonato : int, edicao : int) -> HttpResponse:
    edicao = EdicaoCampeonato.objects.get(campeonato=campeonato,num_edicao=edicao)
    ordem = list(range(1, 21))
    temPalpite = False
    if edicao.campeonato.pontosCorridos:
        # Pegar classificação se for Pontos Corridos
        classificacaoCampeonato = classificacao(edicao,1,38,0)
        classificacaoCampeonato = zip(ordem,classificacaoCampeonato)
        # Os jogos serão pegos por rodada
        paginator = Paginator(Partida.objects.filter(Rodada__edicao_campeonato=edicao).order_by('Rodada'), 10)
        primeiro_jogo_nao_ocorrido = Partida.objects.filter(Rodada__edicao_campeonato=edicao).order_by('Rodada').first()
        if len(Palpite_Campeonato.objects.filter(edicao_campeonato=edicao)) > 0:
            temPalpite = True
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

    # Independente do tipo, se já começou, mostrar o ranking
    if edicao.comecou:
        rankingJogadores = ranking(edicao.id,0)
        if rankingJogadores is not None:
            rankingJogadores = list(rankingJogadores)
    else:
        rankingJogadores = None

    # Independente do tipo, se acabou, ver quem venceu nos palpites
    if edicao.terminou:
        topPepe = [(id, pontosP) for _, _, id, pontosP, _ in list(rankingJogadores)[:3]]
        campeaoPepe = [{'id': usuario[0],'imagem': User.objects.get(id=usuario[0]).profile_image, 'pontos': usuario[1]} for usuario in topPepe]
    else:
        campeaoPepe = None

    edicoes = EdicaoCampeonato.objects.filter(campeonato=edicao.campeonato)
    cravadasJogadores = cravadas(edicao.id,None)

    if edicao.campeonato.pontosCorridos:
        return render(request, "palpites/campeonato_edicao.html", {
            'edicao': edicao,
            'temPalpite': temPalpite,
            'ordem': ordem,
            'classificacao': classificacaoCampeonato,
            'rodadas': Rodada.objects.filter(edicao_campeonato=edicao).order_by("num"),
            'campeaoPepe': campeaoPepe,
            'ranking': rankingJogadores,
            "page": page,
            "edicoes": edicoes,
            "cravadas": cravadasJogadores,
        })
    else:
        return render(request, "palpites/campeonato_edicao.html", {
            'edicao': edicao,
            'temPalpite': temPalpite,
            'rodadas': Rodada.objects.filter(edicao_campeonato=edicao).order_by("num"),
            'campeaoPepe': campeaoPepe,
            'ranking': rankingJogadores,
            "page": page,
            "edicoes": edicoes,
            "cravadas": cravadasJogadores,
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
                "times": Time.objects.all(),
    })

def register_matches(request : HttpRequest) -> HttpResponse:
    return render(request, "palpites/register_json.html", {})

def profile(request : HttpRequest, id : int) -> redirect:
    if request.method == 'POST':
        form = ProfileImageUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
    url = reverse('userView', args=(id,))
    return redirect(url)

def alterar_cor_grafico(request : HttpRequest, id : int) -> redirect:
    if request.method == 'POST':
        cor = request.POST["cor"]
        if len(cor) == 7:
            user = request.user
            user.corGrafico = cor
            user.save()
    url = reverse('userView', args=(id,))
    return redirect(url)

# Visões de Erro
def pagina_404(request : HttpRequest, exception ) -> HttpResponse:
    return render(request, 'palpites/404.html', {} , status=404)

def pagina_500(request : HttpRequest) -> HttpResponse:
    return render(request, 'palpites/500.html', {} , status=500)

def mudarTema(request : HttpRequest) -> HttpResponse:
    user = request.user
    
    if not user.is_authenticated:
        return HttpResponseRedirect(reverse("home"))

    return render(request, "palpites/mudar_tema.html", {
        "title": "Mudar Tema",
    })

def aceitarGrupo(request : HttpRequest, idGrupo:int, idUsuario:int, idMensagem:int) -> HttpResponse:
    grupo = Grupo.objects.get(id=idGrupo)
    usuario = User.objects.get(id=idUsuario)
    grupo.usuarios.add(usuario)
    grupo.save()

    mensagem = Mensagem.objects.get(id=idMensagem)
    mensagem.delete()

    url = reverse('grupo', args=(grupo.id,))
    return redirect(url)

def recusarGrupo(request : HttpRequest, idGrupo:int, idUsuario:int, idMensagem:int) -> HttpResponse:
    grupo = Grupo.objects.get(id=idGrupo)
    usuario = User.objects.get(id=idUsuario)

    mensagem = Mensagem.objects.get(id=idMensagem)
    mensagem.delete()

    return redirect(reverse('mensagens'))
    