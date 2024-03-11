from django.urls import path
from . import views, api
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.contrib.auth.views import PasswordChangeView

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('icons/favicon.ico'))),

# =====================================================================================================================
# ========================================== URL de Views =============================================================
# =====================================================================================================================
    path('', views.home, name="home"),
    
    # ============== Usuario ==============
    path("login", views.verLogin, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("registrar", views.register, name="register"),
    path("usuario/<int:id>", views.verUsuario, name="userView"),
    path("usuario/tema", views.mudarTema, name="mudar_tema"),
    path("atualizar_senha", PasswordChangeView.as_view(), name="change_password"),
    path("usuario/edicao/<int:id>", views.editarUsuario, name="editUserView"),

    # ============== Campeonatos ==============
    path("campeonato", views.verCampeonatos, name="campeonatos"),
    path("campeonato/<int:campeonato>", views.verCampeonato, name="campeonato"),
    path("campeonato/<int:campeonato>/<int:edicao>", views.verEdicaoCampeonato, name="edicao"),    
    path("campeonato/<int:campeonato>/<int:edicao>/<int:rodada>", views.verRodada, name="rodada"),
    path("palpitarEdicao/<int:edicao>", views.verPalpitarEdicao, name="palpiteEdicao"),
    path("register_tournament", views.register_tournament, name="register_tournament"),
    path("register_team_tournament", views.register_team_tournament, name="register_team_tournament"),

    # ============== Times ==============
    path("times", views.verTimes, name="show_teams"),
    path("time/<int:id>", views.verTime, name="show_team"),
    path("registrar_time", views.register_team, name="register_team"),

    # ============== Partidas ==============
    path("partida/<int:id>", views.verPartida, name="partida"),
    path("partida/<str:time>/<int:id>", views.verPartida, name="partida_time"),
    path("registrar_partida", views.register_match, name="register_match"),
    path("atualizar_partida", views.editarPartida, name="change_match"),
    path("registrar_partidas", views.register_matches, name="register_matches"),
    
    # ============== Palpitar ==============
    path("registrar_resultado", views.verPagPalpitar, name="palpitar"),

    # ============== Grupos ==============
    path("grupos", views.verGrupos, name="groups"),

    # ============== Informaçõpes ==============
    path("info", views.verInfo, name="info"),

# =====================================================================================================================
# =============================================== URL de APIs =========================================================
# =====================================================================================================================
    path("alterar_tema/<int:valor>", api.alterar_tema, name="alterar_tema"),

    # ============== Home ==============
    path("attGrafico/<str:usuarios>/<int:campeonato>/<int:rod_Ini>/<int:rod_Fin>", api.attGrafico, name="attGrafico"),
    path("attRodadas/<int:edicao>", api.att_rodadas, name="att_rodadas"),
    path("ranking/<int:edicao>/<int:rodada>", api.get_ranking, name="ranking"),
    path("attPagina/<int:pagina>", api.get_partidas, name="att_paginas"),

    # ============== Usuario ==============
    path('accounts/password_change_done/', RedirectView.as_view(pattern_name='home'), name='password_change_done'),
    path("alterar_time_favorito", api.alterar_time_favorito, name="alterar_time_favorito"),
    path("alterar_cor_grafico/<int:id>", views.alterar_cor_grafico, name="alterar_cor_grafico"),
    path("profile/<int:id>", views.profile, name="profile"),
    path("alterar_tema", api.alterar_tema, name="alterar_tema"),

    # ============== Campeonatos ==============
    path("attPaginaEdicao/<int:edicao>/<int:pagina>", api.get_partidas_edicao, name="att_paginas_edicao"),
    path("classificacao/<int:edicao>/<int:rodada_inicial>/<int:rodada_final>/<int:tipoClassificacao>", api.classificacaoTimesEdicao, name="classificacao"),
    path("registroPalpiteEdicao/<int:edicao>/<int:posicao>/<path:time>/<str:pc>", api.registroPalpiteEdicao, name="registroPalpiteEdicao"),
    path("timesCampeonato/<int:idEdicao>", api.timesCampeonato, name="timesCampeonato"),
    path("estatistica/<int:idEdicao>/cravadas", api.estatisticaCravada, name="estatisticaCravada"),
    path("estatistica/<int:idEdicao>/avgPontos", api.estatisticaAvgPontos, name="estatisticaAvgPontos"),
    path("estatistica/<int:idEdicao>/modaResultados", api.estatisticaModaResultados, name="estatisticaModaResultados"),
    path("estatistica/<int:idEdicao>/modaPalpites", api.estatisticaModaPalpites, name="estatisticaModaPalpites"),
    path("estatistica/<int:idEdicao>/rankingClassicacao", api.estatisticaRankingClassicacao, name="estatisticaRankingClassicacao"),

    # ============== Partidas ==============
    path("registrar_rodada_feita", api.registrar_rodada_feita, name="registrar_rodada_feita"),
    path("attPalpite/<int:idPartida>/<int:golsMandante>/<int:golsVisitante>", api.attPalpite, name="attPalpite"),
    path("attResultado/<int:idPartida>/<int:golsMandante>/<int:golsVisitante>", api.attResultado, name="attResultado"),
    path("att_partida", api.att_partida, name="attPartida"),
    path("att_data_partida", api.att_data_partida, name="attDataPartida"),
]