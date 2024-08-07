from django.db import models
from django.contrib.auth.models import AbstractUser

import random
import colorsys
def gerar_cor_clara():
    # Gerar um valor de cor aleatório em tons claros
    # Você pode ajustar os valores de mínimo e máximo para controlar a gama de cores claras geradas
    h = random.uniform(0.0, 1.0)  # Matiz
    s = random.uniform(0.3, 0.7)  # Saturação
    v = random.uniform(0.7, 1.0)  # Valor

    # Converter a cor de HSV para RGB
    r, g, b = colorsys.hsv_to_rgb(h, s, v)

    # Converter os valores de RGB para hexadecimal
    cor_hex = "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))

    return cor_hex

# Create your models here.
class Time(models.Model):
    id = models.AutoField(primary_key=True)
    Nome = models.CharField(max_length=30,unique=True)
    escudo = models.CharField(max_length=50,unique=True) # terá o endereço para a imagem

    def __str__(self):
        return self.Nome
    
class Campeonato(models.Model):
    nome = models.CharField(max_length=100)
    pontosCorridos = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

class EdicaoCampeonato(models.Model):
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE)
    edicao = models.CharField(max_length=10)
    num_edicao = models.IntegerField(null=True)
    times = models.ManyToManyField('Time', related_name='edicoes_campeonato')
    comecou = models.BooleanField(default=False)
    terminou = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.campeonato.nome + ' ' + self.edicao}"

class Rodada(models.Model):
    num = models.IntegerField()
    nome = models.CharField(max_length=100)
    edicao_campeonato = models.ForeignKey(EdicaoCampeonato, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.edicao_campeonato.campeonato.nome} - {self.edicao_campeonato.edicao} - {self.nome}"

class User(AbstractUser):
    favorite_team = models.ForeignKey(Time, on_delete=models.SET_NULL, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images', default='profile_images/imagem_inexistente.png')
    corGrafico = models.CharField(max_length=7, default=gerar_cor_clara())
    corPersonalizada = models.BooleanField(default=False)
    corFundo = models.CharField(max_length=7, null=True, blank=True)
    corFonte = models.CharField(max_length=7, null=True, blank=True)
    corHover = models.CharField(max_length=7, null=True, blank=True)
    corBorda = models.CharField(max_length=7, null=True, blank=True)
    corSelecionado = models.CharField(max_length=7, null=True, blank=True)
    corPontos0 = models.CharField(max_length=7, null=True, blank=True)
    corPontos1 = models.CharField(max_length=7, null=True, blank=True)
    corPontos2 = models.CharField(max_length=7, null=True, blank=True)
    corPontos3 = models.CharField(max_length=7, null=True, blank=True)
    corFiltro = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return self.username
    
    def colors(self):
        return {
            "--bg": self.corFundo,
            "--fc": self.corFonte,
            "--hover": self.corHover,
            "--filter": self.corFiltro,
            "--border": self.corBorda,
            "--selecionado": self.corSelecionado,
            "--pontos-0": self.corPontos0,
            "--pontos-1": self.corPontos1,
            "--pontos-2": self.corPontos2,
            "--pontos-3": self.corPontos3,
        }
    
class Grupo(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=30)
    dono = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="grupos_dono", null=True, blank=True)
    edicao = models.ForeignKey(EdicaoCampeonato, on_delete=models.CASCADE, null=True)
    usuarios = models.ManyToManyField(User, related_name="grupos", blank=True)
    
    def __str__(self):
        return f"{self.nome} - {self.edicao}"

class Partida(models.Model):
    id = models.AutoField(primary_key=True)
    dia = models.DateTimeField()
    Rodada = models.ForeignKey("Rodada",null=True, blank=True, on_delete=models.SET_NULL)
    Mandante = models.ForeignKey("Time",on_delete=models.CASCADE, related_name='mandante')
    Visitante = models.ForeignKey("Time",on_delete=models.CASCADE, related_name='visitante')
    golsMandante = models.IntegerField(default=-1)
    golsVisitante = models.IntegerField(default=-1)
    vencedor = models.IntegerField(default=-1)

    def __str__(self):
        return f"{self.Rodada} - {self.Mandante.Nome} x {self.Visitante.Nome}"

class Palpite_Partida(models.Model):
    usuario = models.ForeignKey("User",on_delete=models.CASCADE)
    partida = models.ForeignKey("Partida",on_delete=models.CASCADE)
    golsMandante = models.IntegerField()
    golsVisitante = models.IntegerField()
    vencedor = models.IntegerField()
    
    def __str__(self):
        return f"{self.usuario.username} - {self.partida.Mandante.Nome} x {self.partida.Visitante.Nome}"
    
class Palpite_Campeonato(models.Model):
    usuario = models.ForeignKey("User",on_delete=models.CASCADE)
    time = models.ForeignKey("Time", on_delete=models.CASCADE)
    edicao_campeonato = models.ForeignKey("EdicaoCampeonato", on_delete=models.CASCADE)
    posicao_prevista = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.usuario.username} - {self.edicao_campeonato} - {self.time} em {self.posicao_prevista}"

    class Meta:
        unique_together = ('usuario', 'time', 'edicao_campeonato')
        
class RodadaModificada(models.Model):
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    rodada = models.ForeignKey(Rodada, on_delete=models.CASCADE)
    modificador = models.DecimalField(default=1, max_digits=5, decimal_places=2, null=False)
    
    class Meta:
        unique_together = ('grupo', 'rodada')
        
class Mensagem(models.Model):
    to_user = models.ForeignKey("User", related_name="receptor", on_delete=models.CASCADE)
    from_user = models.ForeignKey("User", related_name="remetente", on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    conteudo = models.TextField(null=True,blank=True)
    lida = models.BooleanField(default=False)
    
class Medal(models.Model):
    usuario = models.ForeignKey("User",on_delete=models.CASCADE)
    edicao_campeonato = models.ForeignKey(EdicaoCampeonato, on_delete=models.CASCADE)
    nivel = models.IntegerField()
    
    class Meta:
        unique_together = ('usuario', 'edicao_campeonato')

    def __str__(self):
        return f"{self.nivel}º - {self.usuario.username} - {self.edicao_campeonato}"
