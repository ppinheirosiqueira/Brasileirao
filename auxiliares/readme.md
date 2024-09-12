Pasta que conterá funções python auxiliares a serem executadas fora do site

Essa pasta só é necessária aqui e não como uma view do site porque onde hospedo o site gratuitamente não deixa fazer requisição para outros sites, como o da CBF, onde pego as informações da rodada.

Exemplo do Json:

```{
  "campeonato": "Campeonato Brasileiro",
  "edicao_campeonato": "2024",
  "rodada": "25ª",
  "jogos": [
    {
      "mandante": "Cuiabá",
      "visitante": "Criciúma",
      "data": "31/08/2024 18:30"
    },
    {
      "mandante": "Botafogo",
      "visitante": "Fortaleza",
      "data": "31/08/2024 21:00"
    },
    {
      "mandante": "Grêmio",
      "visitante": "Atlético-MG",
      "data": "01/09/2024 11:00"
    },
    {
      "mandante": "Cruzeiro",
      "visitante": "Atlético-GO",
      "data": "01/09/2024 11:00"
    },
    {
      "mandante": "Corinthians",
      "visitante": "Flamengo",
      "data": "01/09/2024 16:00"
    },
    {
      "mandante": "Vitória",
      "visitante": "Vasco",
      "data": "01/09/2024 18:30"
    },
    {
      "mandante": "Fluminense",
      "visitante": "São Paulo",
      "data": "01/09/2024 18:30"
    },
    {
      "mandante": "Bragantino",
      "visitante": "Bahia",
      "data": "01/09/2024 18:30"
    },
    {
      "mandante": "Athletico",
      "visitante": "Palmeiras",
      "data": "01/09/2024 18:30"
    },
    {
      "mandante": "Juventude",
      "visitante": "Internacional",
      "data": "01/09/2024 18:30"
    }
  ]  
}
```