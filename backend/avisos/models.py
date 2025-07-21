from django.db import models
from usuarios.models import User

class Mensagem(models.Model):
    to_user = models.ForeignKey(User, related_name="receptor", on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, related_name="remetente", on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    conteudo = models.TextField(null=True,blank=True)
    lida = models.BooleanField(default=False)

    class Meta:
        db_table = 'palpites_mensagem'