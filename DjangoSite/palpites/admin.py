from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Time)
admin.site.register(Partida)
admin.site.register(Palpite_Partida)
admin.site.register(Campeonato)
admin.site.register(EdicaoCampeonato)
admin.site.register(Rodada)
admin.site.register(RodadaModificada)
admin.site.register(Grupo)
admin.site.register(Palpite_Campeonato)
admin.site.register(Mensagem)