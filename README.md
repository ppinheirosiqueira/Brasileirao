# Palpites de futebol

## Descrição

Este projeto consiste em uma aplicação web que permite que usuários possam palpitar em jogos do Brasileirão. Os palpites são comparados com os resultados reais dos jogos e pontuações são dadas aos usuários de acordo com seus acertos.

Existem dois padrões de pontuação nessa implementação:

* Padrão Pepe
    * 1 ponto por acertar quem venceria/empate
    * 1 ponto por acertar gols do time mandante
    * 1 ponto por acertar gols do time visitante
* Padrão Shroud
    * 1 ponto por acertar quem venceria/empate
      * Caso acertasse quem venceu/empatou:
        * 1 ponto por acertar gols do time mandante
        * 1 ponto por acertar gols do time visitante

Um ranking foi feito com tais pontuações e um gráfico de pontuação de usuários em diferentes rodadas de um campeonato.

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
4. Na página inicial, utilize os filtros disponíveis para personalizar a visualização do gráfico de pontuação.

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

- Criar mais aplicativos e deixar assim o código mais modular:
  - Melhorar muito a parte de Usuário do sistema, as páginas de registro/modificação de senha foram basicamente deixadas as padrões do django;
  - Melhorar a parte de administração do sistema, criando um aplicativo somente para os administradores;
- Adicionar suporte para múltiplos campeonatos:
  - Para isso o modelo teria que ser atualizado, onde cada partida teria que ser linkada a um campeonato e provavelmente adicionar ao campeonato a edição dele, para que seja possível filtrar as partidas pela edição e não pelo ano (permitindo assim a existência de campeonatos europeus)
  - Com a adição de novos campeonatos, seria bom que o Usuário pudesse filtrar os jogos na aba de Palpitar, para que mostre os campeonatos que ele deseja
- Criação de grupos de Usuários:
  - Caso o projeto se tornasse grande, um gráfico com todos os usuários se tornaria inviável, sendo de bom gosto criar um grupo para que cada usuário se compare com seus amigos;
- Adição de mais cores no gráfico:
  - O gráfico onde se mostra todos os usuários possui uma limitação de 7 usuários porque o site foi feito para minha pessoa e seus amigos, a melhor solução seria ver uma forma de randomizar cores em um espectro (cores vibrantes ou claras) dado que o fundo do site foi definido como uma cor mais escura; 
- Adição de um tema claro e que seja salvo no perfil do usuário a preferência dele, afinal, não é porque a pessoa é maluca que devemos obrigá-la a usar o tema escuro.

- Diversas outras melhorias que podem surgir enquanto eu e meus amigos vamos usando o site. Inclusive, caso deseje ver o site em funcionamento, acesse o link: 

## Contribuição

Sinta-se à vontade para contribuir com este projeto abrindo issues ou enviando pull requests. Toda contribuição é bem-vinda!