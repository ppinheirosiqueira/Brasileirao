from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Time)
admin.site.register(Partida)
admin.site.register(Palpite_Partida)