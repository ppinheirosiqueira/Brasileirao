from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
import json
from datetime import datetime, timezone, timedelta

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
def index(request):
    anosAux = list(Partida.objects.all().dates("dia","year").distinct()) 
    rodadas = list(Partida.objects.all().values_list("rodada",flat=True).distinct())
    usuariosAux = list(Palpite_Partida.objects.all().values_list("usuario",flat=True).distinct()) 
    anos = []
    usuarios = []
    for ano in anosAux:
        anos.append(ano.year)
    for usuario in usuariosAux:
        usuarios.append(User.objects.get(id=usuario).username)
    return render(request, "palpites/index.html", {
        "title": "Palpites",
        "teste": Partida.objects.all(),
        "lastJogos": funcoes.ultimos_jogos(),
        "proxJogos": funcoes.proximos_jogos(),
        "ranking": funcoes.ranking(0,0),
        "anos": anos,
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
    return render(request, "palpites/show_match.html", {
                "title": partida,
                "partida": partida,
                "palpites": list(Palpite_Partida.objects.filter(partida=partida)),
                "anterior": anterior,
                "proxima": proximo,
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

# Views de Banco de Dados
def ranking(request, ano, rodada):

    rankingPreenchido = funcoes.ranking(ano, rodada)
    data_list = [dict(zip(('posicao', 'usernames', 'ids', 'pontosP', 'pontosS'), values)) for values in rankingPreenchido]
    json_string = json.dumps(data_list)
    json_data = json.loads(json_string)

    return JsonResponse(json_data, safe=False)

def userResult(request,usuarios,rod_Ini,rod_Fin):
    #FF6384 (Rosa)  #36A2EB (Azul)  #FFCE56 (Amarelo)   #4BC0C0 (Turquesa)  #9966FF (Roxo)  #FF9F40 (Laranja)   #00E676 (Verde)
    #cores = ["#FF6384","#36A2EB","#FFCE56","#4BC0C0","#9966FF","#FF9F40","#00E676"]

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

    i = 0
    for username in usernames:
        pontosP = []
        for rodada in rodadas:
            pontosP.append(funcoes.check_pontuacao_pepe(Palpite_Partida.objects.filter(partida__rodada=rodada,usuario__username=username)))
        aux = {
            "label": username,
            "data": pontosP,
            "borderColor": funcoes.cores[i],
            "fill":False,
        }
        i += 1
        grafico['datasets'].append(aux)
 
    json_string = json.dumps(grafico)
    json_data = json.loads(json_string)

    # Retorne os dados em formato JSON
    return JsonResponse(json_data, safe=False)
