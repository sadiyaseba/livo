from django import forms
from .models import Post
from apartments.models import Apartment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['type', 'title', 'image', 'price', 'apartment', 'message_link', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your listing or offering...'}),
            'title': forms.TextInput(attrs={'placeholder': 'e.g., Luxury Master Bedroom in city center'}),
            'message_link': forms.TextInput(attrs={'placeholder': 't.me/username or https://wa.me/...'}),
            'price': forms.NumberInput(attrs={'placeholder': '0.00'}),
        }

    def clean_message_link(self):
        link = self.cleaned_data.get('message_link')
        if link:
            # Automatically prepend https:// if missing to avoid URLField validation errors
            if not link.startswith(('http://', 'https://')):
                link = 'https://' + link
        return link

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Change message_link label to be more user friendly
        self.fields['message_link'].label = "Contact Link (Telegram/WhatsApp)"
        self.fields['message_link'].help_text = "Tip: You can just type t.me/yourusername"

        if user:
            # 1. Filter Post Type and Labels based on Role
            if user.role in ['ROOMMATE', 'HOUSE_OWNER']:
                self.fields['type'].choices = [('ROOM', 'Room Listing')]
                self.fields['type'].initial = 'ROOM'

                # Dynamic Price Label for Rooms
                if user.role == 'ROOMMATE':
                    self.fields['price'].label = "Room Rent (Per Person)"
                else:
                    self.fields['price'].label = "Apartment Rent (Full)"

                # Filter Apartments logic
                if user.role == 'HOUSE_OWNER':
                    self.fields['apartment'].queryset = Apartment.objects.filter(owner=user)
                else:
                    self.fields['apartment'].queryset = Apartment.objects.filter(residents__resident=user,
                                                                                 residents__is_active=True).distinct()

            elif user.role == 'VENDOR':
                self.fields['type'].choices = [('FOOD', 'Food Post')]
                self.fields['type'].initial = 'FOOD'
                self.fields['price'].label = "Meal Price"
                self.fields['apartment'].widget = forms.HiddenInput()
                self.fields['apartment'].required = False

            elif user.role == 'HOUSE_HELP':
                self.fields['type'].choices = [('HELP', 'Househelp Post')]
                self.fields['type'].initial = 'HELP'
                self.fields['price'].label = "Expected Salary/Rate"
                self.fields['apartment'].widget = forms.HiddenInput()
                self.fields['apartment'].required = False

        self.fields['type'].label = "Post Category"
        if 'apartment' in self.fields:
            self.fields['apartment'].label = "Select Your Apartment"
            self.fields['apartment'].empty_label = "--- Choose an Apartment ---"
