from django.urls import path
from . import views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.contrib.auth.views import PasswordChangeView

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('icons/favicon.ico'))),

    # Página Principal e funções que a atualizam
    path('', views.home, name="home"),    
    path("user_result/<str:usuarios>/<int:rod_Ini>/<int:rod_Fin>",views.userResult, name="user_result"),
    path("ranking/<int:ano>/<int:rodada>", views.ranking, name="ranking"),
    path("attPagina/<int:pagina>", views.get_partidas, name="att_paginas"),
    
    # Envolvem a adminstração do usuário
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("registrar", views.register, name="register"),
    path("atualizar_senha", PasswordChangeView.as_view(), name="change_password"),
    path('accounts/password_change_done/', RedirectView.as_view(pattern_name='home'), name='password_change_done'),
    path("alterar_time_favorito/<int:id>", views.alterar_time_favorito, name="alterar_time_favorito"),
    path("alterar_cor/<int:id>", views.alterar_cor, name="alterar_cor"),
    path("profile/<int:id>", views.profile, name="profile"),

    # Envolvem ver o usuário em si
    path("usuario/<int:id>", views.userView, name="userView"),

    # Envolvem as partidas
    path("registrar_partida", views.register_match, name="register_match"),
    path("atualizar_partida", views.change_match, name="change_match"),
    path("registrar_resultado", views.register_result, name="register_result"),
    path("partida/<int:id>", views.show_match, name="show_match"),

    # Envolvem os times
    path("registrar_time", views.register_team, name="register_team"),
    path("times", views.show_teams, name="show_teams"),
    path("time/<int:id>", views.show_team, name="show_team"),
]