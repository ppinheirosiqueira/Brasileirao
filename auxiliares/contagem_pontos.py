resultados_2023 = [
    [51, 1, 0],
    [49, 1, 1],
    [38, 2, 1],
    [32, 2, 0],
    [30, 0, 0],
    [28, 0, 1],
    [26, 1, 2],
    [19, 0, 2],
    [17, 3, 0],
    [15, 2, 2],
    [15, 3, 1],
    [12, 0, 3],
    [7, 3, 2],
    [5, 2, 3],
    [5, 4, 1],
    [4, 3, 4],
    [4, 4, 0],
    [3, 3, 3],
    [3, 4, 2],
    [2, 0, 4],
    [2, 1, 4],
    [2, 2, 4],
    [2, 5, 1],
    [1, 0, 5],
    [1, 1, 3],
    [1, 1, 5],
    [1, 4, 3],
    [1, 4, 4],
    [1, 4, 6],
    [1, 5, 0],
    [1, 5, 3],
    [1, 7, 1],
]

resultados_2024= [
    [51, 1, 1],
    [50, 2, 1],
    [47, 1, 0],
    [32, 2, 0],
    [31, 1, 2],
    [30, 0, 1],
    [26, 0, 0],
    [24, 2, 2],
    [16, 3, 0],
    [15, 3, 1],
    [14, 0, 2],
    [7, 1, 3],
    [7, 0, 3],
    [6, 3, 2],
    [6, 4, 1],
    [3, 5, 0],
    [2, 0, 4],
    [2, 4, 2],
    [2, 2, 3],
    [2, 2, 4],
    [1, 1, 4],
    [1, 1, 6],
    [1, 2, 5],
    [1, 3, 5],
    [1, 4, 0],
    [1, 5, 1],
    [1, 5, 2],
]


def check_vencedor(mandante,visitante):
    if mandante > visitante:
        return "Mandante"
    if visitante > mandante:
        return "Visitante"
    return "Empate"

def contagem_pontos(mandante, visitante):
    aux_vitorioso = check_vencedor(mandante,visitante)
    pontuacao = 0
    for resultado in resultados_2023:
        if mandante == resultado[1]:
            pontuacao += resultado[0]
        if visitante == resultado[2]:
            pontuacao += resultado[0]
        if aux_vitorioso == check_vencedor(resultado[1],resultado[2]):
            pontuacao += resultado[0]
    return pontuacao

for man in [0,1,2]:
    for vis in [0,1,2]:
        print(f"Mandante {man} x {vis} Visitante --> {contagem_pontos(man,vis)} pontos")