# Palpites de futebol

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)](https://developer.mozilla.org/pt-BR/docs/Web/JavaScript)
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/pt-BR/docs/Web/HTML)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)](https://developer.mozilla.org/pt-BR/docs/Web/CSS)
[![requirement](https://img.shields.io/badge/Framework-Django-darkgreen)](https://www.djangoproject.com)


## Descrição

Este projeto consiste em uma aplicação web que permite que usuários possam palpitar em jogos do Brasileirão. Os palpites são comparados com os resultados reais dos jogos e pontuações são dadas aos usuários de acordo com seus acertos.

Existe um padrão de pontuação nessa implementação:

* Padrão Pepe
    * 1 ponto por acertar quem venceria/empate
    * 1 ponto por acertar gols do time mandante
    * 1 ponto por acertar gols do time visitante
  
Essa pontuação pode acabar levando a empates, para o critério de desempate é levado em consideração a diferença de gols do palpite em relação ao resultado real.

Vamos imaginar um jogo que acabe 4x2, onde o primeiro usuário palpitou 3x1 e o segundo usuário palpitou 2x0. Os dois usuários fizeram 1 único ponto no Padrão, pois ambos só acertaram quem venceu o jogo. No entanto, o primeiro usuário chegou muito mais próximo do resultado real que o segundo usuário. Por isso, a diferença de gols é utilizado como critério de desempate, onde quem tiver a menor diferença de gols ficará a frente dos demais.

Um ranking foi feito com tais pontuações e um gráfico de pontuação de usuários em diferentes rodadas de um campeonato.

Caso deseje ver o site em funcionamento, visite: https://pepepepi.pythonanywhere.com/

## Tecnologias Utilizadas

- Django: Um framework web em Python utilizado para o desenvolvimento do backend da aplicação.
- Chart.js: Uma biblioteca JavaScript utilizada para a criação do gráfico interativo na página web.
- HTML: Linguagem de marcação utilizada para estruturar a página web.
- CSS: Linguagem de estilização utilizada para definir o visual da página web.

## Funcionalidades

- Palpitar nos jogos.
- Exibição de um ranking da pontuação dos usuários em diferentes rodadas do campeonato.
- Filtro de qual rodada deseja ver o ranking.
- Exibição do gráfico de pontuação de usuários em diferentes rodadas do campeonato.
- Filtros para selecionar quais usuários e quais rodadas deseja visualizar no gráfico.

## Instruções de Uso

1. Faça o clone deste repositório para o seu ambiente de desenvolvimento.
2. Execute o servidor Django com o comando `python manage.py runserver`.
3. Acesse a aplicação no navegador utilizando o endereço `http://localhost:8000`.
4. Divirta-se, recomendo que elimine o banco de dados caso vá usar, mas caso queira utilizar este para ver como funciona, o adm tem login e senha: admin

## Estrutura do Projeto

O projeto não está dos mais bem estruturados dado que fiz para me divertir com meus amigos enquanto treinava algumas técnicas.

- `brasileirao/`: Diretório principal do projeto Django e suas configurações.
- `media/`: Diretório onde ficam guardados os escudos dos times e as imagens de perfis dos usuários
- `palpites`: O único aplicativo Django do projeto. Tudo está ocorrendo nele.
  - `models.py`: Arquivo onde ficam descritos os modelos do banco de dados utilizado
  - `templates/`: Diretório contendo os templates HTML utilizados pela aplicação.
  - `static/`: Diretório contendo os arquivos estáticos da aplicação, como scripts JavaScript e arquivos de estilo CSS.
  - `views.py`: Arquivo contendo as views (controladores) do Django que definem o comportamento da aplicação.

## Melhorias Futuras

- Melhoria do banco de dados. Por querer utilizar um serviço gratuito na internet, não queria deixar o banco de dados ficar pesado, graças a isso, alguns elementos que poderiam ser uteis no futuro foram neglicenciados. Como, por exemplo:
  - Criação do campo edição na partida, contando assim a edição do campeonato em que este jogo ocorre, os filtros atuais utilizam o dia, sendo assim ruins/impossível para campeonatos europeus
  - Melhorar os times, colocando uma sigla, o nome completo, etc
- Criar mais aplicativos e deixar assim o código mais modular:
  - Melhorar muito a parte de Usuário do sistema, as páginas de registro/modificação de senha foram basicamente deixadas as padrões do django;
  - Melhorar a parte de administração do sistema, criando um aplicativo somente para os administradores;
- Caso crie múltiplos campeonatos:
  - Seria bom que o Usuário pudesse filtrar os campeonatos favoritos, para que assim, na página principal e na aba de Palpitar aparecessem os jogos/rankings/gráficos destes campeonatos
- Criação de grupos de Usuários:
  - Caso o projeto se tornasse grande, um gráfico com todos os usuários se tornaria inviável, sendo de bom gosto criar um grupo para que cada usuário se compare com seus amigos;
- Criação de códigos automatizados para criação dos jogos e coleta dos resultados de cada campeonato.

- Diversas outras melhorias que podem surgir enquanto eu e meus amigos vamos usando o site.

## Contribuição

Sinta-se à vontade para contribuir com este projeto abrindo issues ou enviando pull requests. Toda contribuição é bem-vinda!
