# from ..models import Palpite_Partida, User
from ..models import Palpite_Partida
from usuarios.models import User
from .score import check_pontuacao_pepe, check_diferenca_gols

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