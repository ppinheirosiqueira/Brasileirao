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

from .models import User, Time, Partida, Palpite_Partida
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
    anosAux = list(Partida.objects.all().dates("dia","year").distinct()) 
    rodadas = list(Partida.objects.all().values_list("rodada",flat=True).distinct())
    usuariosAux = list(Palpite_Partida.objects.all().values_list("usuario",flat=True).distinct()) 
    anos = []
    usuarios = []
    for ano in anosAux:
        anos.append(ano.year)
    for usuario in usuariosAux:
        usuarios.append(User.objects.get(id=usuario).username)

    paginator = Paginator(Partida.objects.all(), 10)  # Divida as partidas em páginas de 10 partidas cada
    page_number = request.GET.get('page', paginator.num_pages)  # Obtenha o número da página atual dos parâmetros da URL
    page = paginator.get_page(page_number)
    return render(request, "palpites/home.html", {
        "title": "Palpites",
        "page": page,
        "ranking": funcoes.ranking(0,0),
        "anos": anos,
        "rodadas": rodadas,
        "usuarios": usuarios,
    })

def get_partidas(request, pagina):
    paginator = Paginator(Partida.objects.all(), 10)
    page_number = request.GET.get('page', pagina)
    page = paginator.get_page(page_number)
    
    partidas = page.object_list
    serialized_partidas = serializers.serialize('json', partidas)
    serialized_times = serializers.serialize('json', Time.objects.all())
    
    data = {
        'partidas': serialized_partidas,
        'total': page.paginator.num_pages,
        'times': serialized_times,
    }
    
    return JsonResponse(data)

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
        user.cor = funcoes.gerar_cor_clara()
        return HttpResponseRedirect(reverse("home"))
    else:
        return render(request, "palpites/register.html",{
            "title": "Register"
        })

# Views padrões
def register_result(request):
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
    timezone_offset = -3.0 
    tzinfo = timezone(timedelta(hours=timezone_offset))
    faltantes = Partida.objects.filter(dia__gt=datetime.now(tzinfo))
    feitas = Palpite_Partida.objects.filter(usuario=request.user.id,partida__dia__gt=datetime.now(tzinfo))
    #faltantes = Partida.objects.all()
    #feitas = Palpite_Partida.objects.filter(usuario=request.user.id)
    for palpite in feitas:
        if palpite.partida in faltantes:
            faltantes = faltantes.exclude(id=palpite.partida.id)
    return render(request, "palpites/register_result.html", {
                "title": "Registrar Resultado",
                "partidas_feitas": feitas,
                "partidas_faltantes": faltantes
    })

def show_match(request,id):
    partida = Partida.objects.get(id=id)
    partidas = list(Partida.objects.all())
    indice = partidas.index(partida)
    anterior = partidas[indice-1].id
    if anterior > id:
        anterior = None
    try:
        proximo = partidas[indice+1].id
    except:
        proximo = None

    palpites = Palpite_Partida.objects.filter(partida=partida).order_by("usuario__username")
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
    })

def userView(request,id):
    try: 
        form = ProfileUpdateForm(instance=request.user)
        form2 = TimeFavoritoForm()
    except:
        form = ""
        form2 = ""
    usuario = User.objects.get(id=id)
    aGm, aGv, aR = funcoes.accuracy_user(id)

    return render(request, "palpites/show_user.html", {
        "title": f"Perfil do Usuário - {usuario.username}",
        "usuario": usuario,
        "average_points_pepe": funcoes.average_pepe(id),
        "average_points_shroud": funcoes.average_shroud(id),
        "total_predictions": len(Palpite_Partida.objects.filter(usuario=id)),
        "accuracy_goals_mandante": aGm,
        "accuracy_goals_visitante": aGv,
        "accuracy_result": aR,
        "form": form,
        "form2": form2,
    })

def show_teams(request):
    return render(request, "palpites/times.html",{
        "title": "Times",
        "times": Time.objects.all(),
    })

def show_team(request,id):
    time = Time.objects.get(id=id)
    fas = User.objects.filter(favorite_team=id)
    jogos = Partida.objects.filter(Mandante=id) | Partida.objects.filter(Visitante=id)
    jogos = jogos.order_by("rodada")
    palpites = Palpite_Partida.objects.filter(partida__in=jogos)
    usuariosAux = list(set(palpites.values_list("usuario", flat=True)))
    usuarios = User.objects.filter(id__in=usuariosAux)
    porcentagem = []
    for usuario in usuarios:
        pontos = funcoes.check_pontuacao_pepe(palpites.filter(usuario=usuario))
        total = 3*palpites.filter(usuario=usuario).count()
        porcentagem.append(100*pontos/total)

    acertos = zip(usuarios,porcentagem)
    acertos = sorted(acertos, key=lambda x: x[1], reverse=True)

    return render(request, "palpites/time.html", {
        "time": time,
        "fas": fas,
        "jogos": jogos,
        "acertos": acertos,
    })

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

def alterar_cor(request,id):
    if request.method == 'POST':
        cor = request.POST["cor"]
        if len(cor) == 7:
            user = request.user
            user.cor = cor
            user.save()
    url = reverse('userView', args=(id,))
    return redirect(url)

# Views de Administração
def register_team(request):
    if request.method == "POST":
        nome = request.POST["time"]
        escudo = request.POST["escudo"]
        aux = Time(Nome=nome,escudo=escudo)
        aux.save()
    return render(request, "palpites/register_team.html", {
                "title": "Registrar Time",
                "times": Time.objects.all()
    })

def register_match(request):
    message = ""
    if request.method == "POST":
        date = request.POST["date"]
        rodada = request.POST["rodada"]
        mandante = request.POST["mandante"]
        visitante = request.POST["visitante"]
        lista_partidas = Partida.objects.filter(rodada=rodada)
        auxNome = True
        if mandante == visitante:
            auxNome = False
            message = "<h3>Não tem como um time jogar contra ele mesmo</h3>"
        if auxNome:
            for partida in lista_partidas:
                if mandante == partida.Mandante.Nome or mandante == partida.Visitante.Nome or visitante == partida.Mandante.Nome or visitante == partida.Visitante.Nome:
                    message = "<h3>Não tem como um time fazer dois jogos na mesma rodada</h3>"
                    auxNome = False
                    break
        if auxNome:
            aux = Partida(dia=date,rodada=rodada,Mandante=Time.objects.get(Nome=mandante),Visitante=Time.objects.get(Nome=visitante))
            aux.save()
            message = "<h3>Jogo Salvo com Sucesso</h3>"
    return render(request, "palpites/register_match.html", {
                "message": message,
                "title": "Registrar Partida",
                "partidas": Partida.objects.all(),
                "times": Time.objects.all()
    })

def change_match(request):
    limite_data = datetime.now() - timedelta(days=3)
    message = ""
    if request.method == "POST":
        gMan = request.POST["gMan"]
        gVis = request.POST["gVis"]
        partida = int(request.POST["partida"])
        aux = Partida.objects.get(id=partida)
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
                "partidas": Partida.objects.filter(dia__gt=limite_data),
                "times": Time.objects.all()
    })

# Views de Banco de Dados
def ranking(request, ano, rodada):

    rankingPreenchido = funcoes.ranking(ano, rodada)
    data_list = [dict(zip(('posicao', 'usernames', 'ids', 'pontosP', 'pontosS'), values)) for values in rankingPreenchido]
    json_string = json.dumps(data_list)
    json_data = json.loads(json_string)

    return JsonResponse(json_data, safe=False)

def userResult(request,usuarios,rod_Ini,rod_Fin):
    usernames = []
    if usuarios == "todos":
        palpites = Palpite_Partida.objects.filter(partida__rodada__gte=rod_Ini, partida__rodada__lte=rod_Fin)
        usernames = palpites.values_list("usuario__username",flat=True).distinct()
    elif usuarios == "voce":
        usernames.append(request.user.username)
        if usernames[0] == '':
            usernames[0]= Palpite_Partida.objects.all().order_by('?').first().usuario.username 
    else:
        usernames = usuarios.split("+")

    rodadas = list(range(rod_Ini, rod_Fin + 1))

    grafico = {
        "labels": rodadas,
        "datasets":[]
    }

    for username in usernames:
        pontosP = []
        for rodada in rodadas:
            pontosP.append(funcoes.check_pontuacao_pepe(Palpite_Partida.objects.filter(partida__rodada=rodada,usuario__username=username)))
        aux = {
            "label": username,
            "data": pontosP,
            "borderColor": User.objects.get(username=username).cor if User.objects.get(username=username).cor else funcoes.gerar_cor_clara(),
            "fill":False,
        }
        grafico['datasets'].append(aux)
 
    json_string = json.dumps(grafico)
    json_data = json.loads(json_string)

    # Retorne os dados em formato JSON
    return JsonResponse(json_data, safe=False)
