from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Time(models.Model):
    id = models.AutoField(primary_key=True)
    Nome = models.CharField(max_length=30,unique=True)
    escudo = models.CharField(max_length=50,unique=True) # terá o endereço para a imagem

    def __str__(self):
        return self.Nome

class User(AbstractUser):
    favorite_team = models.ForeignKey(Time, on_delete=models.SET_NULL, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images', default='caminho/para/imagem_inexistente.jpg')

    def __str__(self):
        return self.username

class Partida(models.Model):
    id = models.AutoField(primary_key=True)
    dia = models.DateTimeField()
    rodada = models.IntegerField()
    Mandante = models.ForeignKey("Time",on_delete=models.CASCADE, related_name='mandante')
    Visitante = models.ForeignKey("Time",on_delete=models.CASCADE, related_name='visitante')
    golsMandante = models.IntegerField(default=-1)
    golsVisitante = models.IntegerField(default=-1)
    vencedor = models.IntegerField(default=-1)

    def __str__(self):
        return f"{self.rodada}ª rodada - {self.Mandante.Nome} x {self.Visitante.Nome}"

class Palpite_Partida(models.Model):
    usuario = models.ForeignKey("User",on_delete=models.CASCADE)
    partida = models.ForeignKey("Partida",on_delete=models.CASCADE)
    golsMandante = models.IntegerField()
    golsVisitante = models.IntegerField()
    vencedor = models.IntegerField()
    
    def __str__(self):
        return f"{self.usuario.username} - {self.partida.Mandante.Nome} x {self.partida.Visitante.Nome}"