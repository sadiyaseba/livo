from django import forms
from .models import Househelp

class HousehelpProfileForm(forms.ModelForm):
    class Meta:
        model = Househelp
        fields = ['city', 'area', 'skills', 'availability', 'expected_salary']
        widgets = {
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Dhaka'}),
            'area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Gulshan'}),
            'skills': forms.CheckboxSelectMultiple(),
            'expected_salary': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 8000'}),
            'availability': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

