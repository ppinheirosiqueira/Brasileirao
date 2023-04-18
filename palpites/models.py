from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    pass

class Time(models.Model):
    id = models.IntegerField(primary_key=True)
    Nome = models.CharField(max_length=30,unique=True)
    escudo = models.CharField(max_length=50,unique=True) # terá o endereço para a imagem

class Partida(models.Model):
    id = models.IntegerField(primary_key=True)
    dia = models.DateField()
    rodada = models.IntegerField()
    ano = models.IntegerField()
    Mandante = models.ForeignKey("Time",on_delete=models.CASCADE, related_name='mandante')
    Visitante = models.ForeignKey("Time",on_delete=models.CASCADE, related_name='visitante')
    golsMandante = models.IntegerField(default=0)
    golsVisitante = models.IntegerField(default=0)
    vencedor = models.IntegerField()

class Palpite_Partida(models.Model):
    usuario = models.ForeignKey("User",on_delete=models.CASCADE)
    partida = models.ForeignKey("Partida",on_delete=models.CASCADE)
    golsMandante = models.IntegerField(default=0)
    golsVisitante = models.IntegerField(default=0)
    vencedor = models.IntegerField()
