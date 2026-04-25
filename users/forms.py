from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, PreferenceTag
from househelp.models import SkillTag


class UserSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True,
                                 widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, required=True,
                                widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-control'}))
    email = forms.EmailField(required=True,
                             widget=forms.EmailInput(attrs={'placeholder': 'Email Address', 'class': 'form-control'}))

    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=True,
        widget=forms.RadioSelect(attrs={'class': 'role-selector'})
    )

    gender = forms.ChoiceField(
        choices=User.GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Phone Number', 'class': 'form-control'})
    )

    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    contact_link = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'placeholder': 'e.g. LinkedIn or Portfolio URL', 'class': 'form-control'})
    )

    # Role-Specific Master Lists (Handled in Step 3)
    preferences = forms.ModelMultipleChoiceField(
        queryset=PreferenceTag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    skills = forms.ModelMultipleChoiceField(
        queryset=SkillTag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    expected_salary = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter expected salary (e.g. 8000)', 'class': 'form-control'})
    )

    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Dhaka', 'class': 'form-control'})
    )

    area = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Gulshan', 'class': 'form-control'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "email", "role", "gender", "username", "phone", "profile_image",
                  "contact_link")


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "profile_image", "contact_link", "gender")
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_link': forms.URLInput(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
        }

from users.models import LifestylePreference

class LifestylePreferenceForm(forms.ModelForm):
    class Meta:
        model = LifestylePreference
        fields = ['educational_institution', 'workplace', 'bio', 'preferences']
        widgets = {
            'preferences': forms.CheckboxSelectMultiple(),
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'educational_institution': forms.TextInput(attrs={'class': 'form-control'}),
            'workplace': forms.TextInput(attrs={'class': 'form-control'}),
        }
