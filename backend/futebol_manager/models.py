from django.db import models

# Create your models here.
class TipoTime(models.TextChoices):
    CLUBE = 'CL', 'Clube'
    SELECAO = 'SE', 'Seleção Nacional'
    AMBOS = 'AM', 'Ambos'

class EscopoCampeonato(models.TextChoices):
    NACIONAL = 'NAC', 'Nacional'
    CONTINENTAL = 'CON', 'Continental'
    MUNDIAL = 'MUN', 'Mundial'

class Continente(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nome

class Pais(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    continente = models.ForeignKey(Continente, on_delete=models.PROTECT, related_name='paises')
    bandeira = models.CharField(max_length=50, blank=True, null=True) # Endereço para a imagem da bandeira

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = "Países"

class Time(models.Model):
    id = models.AutoField(primary_key=True)
    Nome = models.CharField(max_length=30,unique=True)
    escudo = models.CharField(max_length=50,unique=True) # terá o endereço para a imagem
    tipo = models.CharField(max_length=2, choices=TipoTime.choices, default=TipoTime.CLUBE, null=True, blank=True)
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, related_name='times', null=True, blank=True)

    def __str__(self):
        return self.Nome
    
    class Meta:
        db_table = 'palpites_time'
    
class Campeonato(models.Model):
    nome = models.CharField(max_length=100)
    pontosCorridos = models.BooleanField(default=True)
    tipo_time_aceito = models.CharField(max_length=2,choices=TipoTime.choices,default=TipoTime.CLUBE, null=True, blank=True)
    escopo = models.CharField(max_length=3,choices=EscopoCampeonato.choices,default=EscopoCampeonato.NACIONAL)
    continente = models.ForeignKey(Continente,on_delete=models.PROTECT,null=True,blank=True,help_text="Relevante apenas se o escopo for Continental.")
    pais = models.ForeignKey(Pais,on_delete=models.PROTECT,null=True,blank=True,help_text="Relevante apenas se o escopo for Nacional.")

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'palpites_campeonato'

class EdicaoCampeonato(models.Model):
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE)
    edicao = models.CharField(max_length=10)
    num_edicao = models.IntegerField(null=True)
    times = models.ManyToManyField('Time', related_name='edicoes_campeonato')
    comecou = models.BooleanField(default=False)
    terminou = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.campeonato.nome + ' ' + self.edicao}"

    class Meta:
        db_table = 'palpites_edicaocampeonato'

class Rodada(models.Model):
    num = models.IntegerField()
    nome = models.CharField(max_length=100)
    edicao_campeonato = models.ForeignKey(EdicaoCampeonato, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.edicao_campeonato.campeonato.nome} - {self.edicao_campeonato.edicao} - {self.nome}"
    
    class Meta:
        db_table = 'palpites_rodada'

class Partida(models.Model):
    id = models.AutoField(primary_key=True)
    dia = models.DateTimeField()
    Rodada = models.ForeignKey(Rodada,null=True, blank=True, on_delete=models.SET_NULL)
    Mandante = models.ForeignKey(Time,on_delete=models.CASCADE, related_name='mandante')
    Visitante = models.ForeignKey(Time,on_delete=models.CASCADE, related_name='visitante')
    golsMandante = models.IntegerField(default=-1)
    golsVisitante = models.IntegerField(default=-1)
    vencedor = models.IntegerField(default=-1)

    def __str__(self):
        return f"{self.Rodada} - {self.Mandante.Nome} x {self.Visitante.Nome}"

    class Meta:
        db_table = 'palpites_partida'