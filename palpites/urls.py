from django.urls import path
from . import views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from brasileirao.settings import STATIC_URL
from django.contrib.auth.views import PasswordChangeView

urlpatterns = [
    path('', views.index, name="index"),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('icons/favicon.ico'))),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("user/<int:id>", views.userView, name="userView"),
    path("change_password", PasswordChangeView.as_view(), name="change_password"),
    path("register_team", views.register_team, name="register_team"),
    path("register_match", views.register_match, name="register_match"),
    path("change_match", views.change_match, name="change_match"),
    path("register_result", views.register_result, name="register_result"),
    path("match/<int:id>", views.show_match, name="show_match"),
    path("user_result/<str:usuarios>/<int:rod_Ini>/<int:rod_Fin>",views.userResult, name="user_result"),
    path("ranking/<int:ano>/<int:rodada>", views.ranking, name="ranking"),
    path("alterar_time_favorito/<int:id>", views.alterar_time_favorito, name="alterar_time_favorito"),
    path("alterar_cor/<int:id>", views.alterar_cor, name="alterar_cor"),
    path("profile/<int:id>", views.profile, name="profile"),
    path('accounts/password_change_done/', RedirectView.as_view(pattern_name='index'), name='password_change_done'),
]