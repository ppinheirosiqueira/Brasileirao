from django import forms
from usuarios.models import User

class ProfileImageUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_image']