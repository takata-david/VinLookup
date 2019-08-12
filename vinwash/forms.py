from django import forms

from . models import vinfile


class vinfileForm(forms.ModelForm):
    class Meta:
        model = vinfile
        fields = ['filename', 'date', 'user', 'notes', 'business']