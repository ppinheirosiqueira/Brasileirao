from django.urls import path
from . import views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from brasileirao.settings import STATIC_URL

urlpatterns = [
    path('', views.index, name="index"),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('icons/favicon.ico'))),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("register_team", views.register_team, name="register_team"),
    path("register_match", views.register_match, name="register_match"),
    path("change_match", views.change_match, name="change_match"),
    path("register_result", views.register_result, name="register_result"),
    path("match/<int:id>", views.show_match, name="show_match"),
]