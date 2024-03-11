from django import forms
from .models import User

class ProfileImageUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_image']