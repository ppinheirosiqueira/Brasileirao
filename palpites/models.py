from django.db import models

# Create your models here.

class Time(models.Model):
    id = models.IntegerField(primary_key=True)
    Nome = models.CharField(max_length=30,unique=True)
    escudo = models.FileField(upload_to='documents')

class Partida(models.Model):
    id = models.IntegerField(primary_key=True)
    dia = models.DateField()
    rodada = models.IntegerField()
    ano = models.IntegerField()
    Mandante = models.ForeignKey("Time",on_delete=models.CASCADE)
    Visitante = models.ForeignKey("Time",on_delete=models.CASCADE)
    golsMandante = models.IntegerField(default=0)
    golsVisitante = models.IntegerField(default=0)
    vencedor = models.IntegerField()

class Usuario(models.Model):
    id = models.IntegerField(primary_key=True)
    usuario = models.CharField(unique=True)
    password = models.CharField()
