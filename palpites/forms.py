from django import forms
from .models import User, Time

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_image']

class TimeFavoritoForm(forms.Form):
    time_favorito = forms.ModelChoiceField(queryset=Time.objects.all(), empty_label="Selecione um time")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TimeFavoritoForm, self).__init__(*args, **kwargs)
        self.fields['time_favorito'].empty_label = "Selecione um time"
        if user:
            self.fields['time_favorito'].initial = user.favorite_team
