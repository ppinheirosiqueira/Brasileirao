from django.urls import path
from . import views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.contrib.auth.views import PasswordChangeView

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('icons/favicon.ico'))),

    # Página Principal e funções que a atualizam
    path('', views.home, name="home"),    
    path("user_result/<str:usuarios>/<int:campeonato>/<int:rod_Ini>/<int:rod_Fin>",views.userResult, name="user_result"),
    path("ranking/<int:edicao>/<int:rodada>", views.ranking, name="ranking"),
    path("attPagina/<int:pagina>", views.get_partidas, name="att_paginas"),
    path("attRodadas/<int:edicao>", views.att_rodadas, name="att_rodadas"),
    
    # Envolvem a adminstração do usuário
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("registrar", views.register, name="register"),
    path("atualizar_senha", PasswordChangeView.as_view(), name="change_password"),
    path('accounts/password_change_done/', RedirectView.as_view(pattern_name='home'), name='password_change_done'),
    path("alterar_time_favorito/<int:id>", views.alterar_time_favorito, name="alterar_time_favorito"),
    path("alterar_cor_clara/<int:id>", views.alterar_cor_clara, name="alterar_cor_clara"),
    path("alterar_cor_escura/<int:id>", views.alterar_cor_escura, name="alterar_cor_escura"),
    path("profile/<int:id>", views.profile, name="profile"),
    path("usuario/edicao/<int:id>", views.editUserView, name="editUserView"),
    path("alterar_tema/<int:valor>", views.alterar_tema, name="alterar_tema"),

    # Envolvem ver o usuário em si
    path("usuario/<int:id>", views.userView, name="userView"),

    # Envolvem o campeonato
    path("campeonato", views.campeonatos, name="campeonatos"),
    path("campeonato/<int:campeonato>", views.campeonato, name="campeonato"),
    path("campeonato/<int:campeonato>/<int:edicao>", views.edicao, name="edicao"),    
    path("campeonato/<int:campeonato>/<int:edicao>/<int:rodada>", views.rodada, name="rodada"),
    path("attPaginaEdicao/<int:edicao>/<int:pagina>", views.get_partidas_edicao, name="att_paginas_edicao"),
    path("classificacao/<int:edicao>/<int:rodada_inicial>/<int:rodada_final>/<int:tipoClassificacao>", views.classificacao, name="classificacao"),
    path("palpitarEdicao/<int:edicao>", views.palpitarEdicao, name="palpiteEdicao"),
    path("registroPalpiteEdicao/<int:edicao>/<int:posicao>/<path:time>/<str:pc>", views.registroPalpiteEdicao, name="registroPalpiteEdicao"),
    path("timesCampeonato/<int:edicao>", views.timesCampeonato, name="timesCampeonato"),

    # Envolvem as partidas
    path("registrar_partida", views.register_match, name="register_match"),
    path("atualizar_partida", views.change_match, name="change_match"),
    path("registrar_resultado", views.palpitar, name="palpitar"),
    path("partida/<int:id>", views.show_match, name="show_match"),
    path("partida/<str:time>/<int:id>", views.show_match, name="show_match_time"),
    path("registrar_partidas", views.register_matches, name="register_matches"),
    path("registrar_rodada_feita", views.registrar_rodada_feita, name="registrar_rodada_feita"),
    
    # Envolvem os times
    path("registrar_time", views.register_team, name="register_team"),
    path("times", views.show_teams, name="show_teams"),
    path("time/<int:id>", views.show_team, name="show_team"),

    # Envolvem os campeonatos
    path("register_tournament", views.register_tournament, name="register_tournament"),
    path("register_team_tournament", views.register_team_tournament, name="register_team_tournament"),
    
    # Envolvem os grupos
    path("grupos", views.groups, name="groups"),

    # Envolvem o funcionamento do site
    path("about", views.about, name="about"),
]