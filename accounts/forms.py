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


    # Override the default widgets for password fields
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
        fields = ['username', 'email', 'phone_number']  # Fields the user can edit
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


from django import forms
from django_select2.forms import Select2MultipleWidget
from .models import Evidence, Case
from django.contrib.auth import get_user_model

User = get_user_model()

class EvidenceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # ✅ Accept `request`
        super().__init__(*args, **kwargs)

        # Filter viewers if needed
        if 'case' in self.data:
            try:
                case_id = int(self.data.get('case'))
                case = Case.objects.get(id=case_id)
                self.fields['viewers'].queryset = case.team.members.all()
            except (ValueError, Case.DoesNotExist):
                self.fields['viewers'].queryset = User.objects.none()
        else:
            self.fields['viewers'].queryset = User.objects.all()

    class Meta:
        model = Evidence
        fields = ['case', 'file', 'type', 'description', 'viewers']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'viewers': Select2MultipleWidget(attrs={'class': 'form-select'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'case': forms.Select(attrs={'class': 'form-select'}),
        }


from django import forms
from .models import MatchResult

class MatchInputForm(forms.ModelForm):
    class Meta:
        model = MatchResult
        fields = ['uploaded_face', 'uploaded_voice']
        widgets = {
            'uploaded_face': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'uploaded_voice': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
