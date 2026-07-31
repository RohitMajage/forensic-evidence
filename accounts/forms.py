from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import *


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your username',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
        })


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
        })
    )


class CustomUserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your username',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number',
            }),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name',
                'maxlength': '100'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your message here...',
                'rows': 5
            }),
        }


from django_select2.forms import Select2MultipleWidget
from .models import Evidence, Case
from django.contrib.auth import get_user_model

User = get_user_model()


class EvidenceForm(forms.ModelForm):
    viewers = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=Select2MultipleWidget,
        required=False,
    )

    class Meta:
        model = Evidence
        fields = ['case', 'file', 'type', 'description', 'viewers']
        widgets = {
            'case': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)


class MatchInputForm(forms.Form):
    uploaded_face = forms.ImageField(required=False, label="Upload Face Image")
    uploaded_voice = forms.FileField(required=False, label="Upload Voice File")


class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ['case_name', 'case_number']
        widgets = {
            'case_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Cyber Crime Investigation'}),
            'case_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CASE-2026-01'}),
        }

