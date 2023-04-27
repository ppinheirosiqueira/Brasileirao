from django.shortcuts import render
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from .models import User, Time, Partida, Palpite_Partida
from . import funcoes

# Visão Principal
def index(request):
    return render(request, "palpites\index.html", {
        "title": "Palpites",
        "lastJogos": funcoes.ultimos_jogos(),
        "proxJogos": funcoes.proximos_jogos(),
        "ranking": funcoes.ranking(),
        "grafico": funcoes.grafico_padrao(request),
    })

# Views de Administração de Usuario
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        print(user)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
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
    return HttpResponseRedirect(reverse("index"))

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
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "palpites/register.html",{
            "title": "Register"
        })

# Views de Usuário
def register_result(request):
    if request.method == "POST":
        for key, value in request.POST.items():
            if value != '':
                if key.startswith('man_'):
                    team_id, partida_id = key.split('_')
                    aux = Palpite_Partida(usuario=request.user,partida=Partida.objects.get(id=int(partida_id)),golsMandante=value)
                if key.startswith('vis_'):
                    team_id, partida_id = key.split('_')
                    aux.golsVisitante = value
                    if aux.golsMandante == aux.golsVisitante:
                        aux.vencedor = 0
                    elif aux.golsMandante > aux.golsVisitante:
                        aux.vencedor = 1
                    else:
                        aux.vencedor = 2
                    aux.save()
    faltantes = Partida.objects.all()
    feitas = Palpite_Partida.objects.filter(usuario=request.user.id)
    for palpite in feitas:
        if palpite.partida in faltantes:
            faltantes = faltantes.exclude(id=palpite.partida.id)
    return render(request, "palpites/register_result.html", {
                "title": "Registrar Resultado",
                "partidas_feitas": feitas,
                "partidas_faltantes": faltantes
    })

def show_match(request,id):
    pass

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
        lista_partidas = Partida.objects.filter(rodada=rodada,dia=date)
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
                "partidas": Partida.objects.all(),
                "times": Time.objects.all()
    })
