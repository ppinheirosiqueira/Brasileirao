from django.db import models
from usuarios.models import User
from futebol_manager.models import Partida, Time, EdicaoCampeonato

class Palpite_Partida(models.Model):
    usuario = models.ForeignKey(User,on_delete=models.CASCADE)
    partida = models.ForeignKey(Partida,on_delete=models.CASCADE)
    golsMandante = models.IntegerField()
    golsVisitante = models.IntegerField()
    vencedor = models.IntegerField()
    
    def __str__(self):
        return f"{self.usuario.username} - {self.partida.Mandante.Nome} x {self.partida.Visitante.Nome}"
    
class Palpite_Campeonato(models.Model):
    usuario = models.ForeignKey(User,on_delete=models.CASCADE)
    time = models.ForeignKey(Time, on_delete=models.CASCADE)
    edicao_campeonato = models.ForeignKey(EdicaoCampeonato, on_delete=models.CASCADE)
    posicao_prevista = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.usuario.username} - {self.edicao_campeonato} - {self.time} em {self.posicao_prevista}"

    class Meta:
        unique_together = ('usuario', 'time', 'edicao_campeonato')
    
class Medal(models.Model):
    usuario = models.ForeignKey(User,on_delete=models.CASCADE)
    edicao_campeonato = models.ForeignKey(EdicaoCampeonato, on_delete=models.CASCADE)
    nivel = models.IntegerField()
    
    class Meta:
        unique_together = ('usuario', 'edicao_campeonato')

    def __str__(self):
        return f"{self.nivel}º - {self.usuario.username} - {self.edicao_campeonato}"
