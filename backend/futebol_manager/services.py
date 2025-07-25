from django.db.models import Q
from .models import Campeonato, Time, EscopoCampeonato, TipoTime, Pais

def get_times_elegiveis_para_campeonato(campeonato: Campeonato):
    """
    Recebe um objeto Campeonato e retorna um QuerySet de times elegíveis.
    """
    # Filtro base por tipo de time
    filtros = Q()
    if campeonato.tipo_time_aceito != TipoTime.AMBOS:
        filtros &= Q(tipo=campeonato.tipo_time_aceito)
    
    # Filtros de Escopo Geográfico
    if campeonato.escopo == EscopoCampeonato.NACIONAL:
        filtros &= Q(pais=campeonato.pais)
        
    elif campeonato.escopo == EscopoCampeonato.CONTINENTAL:
        filtros &= Q(pais__continente=campeonato.continente)
        
    return Time.objects.filter(filtros)