def partida_to_json(partida):
    return {
        'pk': partida.pk,
        'Mandante': partida.Mandante.id,
        'Visitante': partida.Visitante.id,
        'golsMandante': partida.golsMandante,
        'golsVisitante': partida.golsVisitante,
        'Rodada': f'{partida.Rodada.edicao_campeonato.campeonato} - {partida.Rodada.nome}',
    }

def palpites_campeonato_to_json(palpites,palpitador):    
    return {
        'nome': palpitador,
        'palpites': [palpite_campeonato_to_json(palpite) for palpite in palpites[palpitador]]
    }
    

def palpite_campeonato_to_json(palpite):
    return {
        'time': palpite.time.id,
        'posicao': palpite.posicao_prevista,
    }
    
def modificador_to_json(modificador):
    return {
        'id': modificador.id,
        'nome': modificador.rodada.nome,
        'modificador': modificador.modificador,
    }
    
def titulo_mensagem_to_json(mensagem):
    return {
        'idMensagem': mensagem.id,
        'titulo': mensagem.titulo,
        'lida': mensagem.lida,
        'idFrom': mensagem.from_user.id,
        'from': mensagem.from_user.username
    }
    
def mensagem_to_json(mensagem):
    return {
        'idMensagem': mensagem.id,
        'titulo': mensagem.titulo,
        'idFrom': mensagem.from_user.id,
        'from': mensagem.from_user.username,
        'texto': mensagem.conteudo
    }