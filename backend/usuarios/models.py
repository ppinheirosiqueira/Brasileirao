from django.db import models
from .utils import gerar_cor_clara
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    favorite_team = models.ForeignKey('futebol_manager.Time', on_delete=models.SET_NULL, null=True, blank=True)
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
    
    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'palpites_user'

class Grupo(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=30)
    dono = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="grupos_dono", null=True, blank=True)
    edicao = models.ForeignKey('futebol_manager.EdicaoCampeonato', on_delete=models.CASCADE, null=True)
    usuarios = models.ManyToManyField(User, related_name="grupos", blank=True)
    
    def __str__(self):
        return f"{self.nome} - {self.edicao}"
    
    class Meta:
        db_table = 'palpites_grupo'

class RodadaModificada(models.Model):
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    rodada = models.ForeignKey('futebol_manager.Rodada', on_delete=models.CASCADE) # Mude para string
    modificador = models.DecimalField(default=1, max_digits=5, decimal_places=2, null=False)
    
    class Meta:
        unique_together = ('grupo', 'rodada')
        db_table = 'palpites_rodadamodificada'
    