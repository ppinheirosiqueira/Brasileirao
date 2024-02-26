import requests
from bs4 import BeautifulSoup
import re
import json

times = {
    'AME': "América-MG",
    'ATH': "Athletico",
    'ATL': "Atlético-MG/Atlético-GO",
    'BAH': "Bahia",
    'BOT': "Botafogo",
    'RED': "Bragantino",
    'COR': "Corinthians/Coritiba",
    'CRI': "Criciumá",
    'CRU': "Cruzeiro",
    'CUI': "Cuiabá",
    'FLA': "Flamengo",
    'FLU': "Fluminense",
    'FOR': "Fortaleza",
    'GOI': "Goiás",
    'GRE': "Grêmio",
    'INT': "Internacional",
    'JUV': "Juventude",
    'PAL': "Palmeiras",
    'SAO': "São Paulo",
    'SAN': "Santos",
    'VAS': "Vasco",
    'VIT': "Vitória",
}

campeonato = input("Qual campeonato vai recolher?")
edicaoCampeonato = input("Qual a edição desse campeonato?")
rodada = input("Qual rodada deseja recolher?")

url = 'https://www.cbf.com.br/futebol-brasileiro/competicoes/campeonato-brasileiro-serie-a?csrt=8969359475780767906'
response = requests.get(url)
if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        todosJogos = soup.find('div', {'class': 'swiper-wrapper'})
        rodadaEscolhida = todosJogos.find('div', {'data-slide-index' : str(int(rodada)-1)})
        jogos = []
        for li in rodadaEscolhida.find_all('li'):
            dado = li.find('span', {'class': 'partida-desc'}).text
            padrao = r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2})'
            correspondencias = re.search(padrao, dado)
            siglaMandante = li.find('div', {'class': 'time pull-left'}).find('span', {'class':'time-sigla'}).text
            siglaVisitante = li.find('div', {'class': 'time pull-right'}).find('span', {'class':'time-sigla'}).text
            aux = {
                'data': correspondencias.group(1),
                'mandante': times[siglaMandante],
                'visitante':  times[siglaVisitante],
            }
            jogos.append(aux)

with open(f'auxiliares/arquivosJson/{campeonato + "_" +  rodada}.json', 'w', encoding='utf-8') as json_file:
    json.dump({
        'campeonato': campeonato,
        'edicao_campeonato': edicaoCampeonato,
        'rodada': rodada,
        'jogos': jogos,
    }, json_file, ensure_ascii=False, indent=2)  # ensure_ascii=False para permitir caracteres especiais
