from django import forms

from . models import vinfile


class vinfileForm(forms.ModelForm):
    class Meta:
        model = vinfile
        fields = ['filename', 'date', 'user', 'notes', 'business']


class VinForm(forms.Form):
    your_vin = forms.CharField(label='Please Enter Your Vin', max_length=100)