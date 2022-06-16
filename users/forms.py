from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


FORM_FIELD_STYLES = (
    'form-control border-8 mb-4 py-3 px-5 border-0 fs_24 '
    'SelfStorage__bg_lightgrey'
)


class CustomUserCreationForm(UserCreationForm):
    email = forms.CharField(
        widget=forms.EmailInput(
            attrs={'class': FORM_FIELD_STYLES, 'placeholder': 'E-mail'}
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': FORM_FIELD_STYLES, 'placeholder': 'Пароль'}
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': FORM_FIELD_STYLES, 'placeholder': 'Пароль'}
        )
    )
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            User.objects.get(email=email)
        except Exception:
            return email
        raise forms.ValidationError(f'E-mail {email} уже существует.')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("email",)


class LoginForm(forms.Form):
    email = forms.CharField(
        widget=forms.EmailInput(
            attrs={'class': FORM_FIELD_STYLES, 'placeholder': 'E-mail'}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': FORM_FIELD_STYLES, 'placeholder': 'Пароль'}
        )
    )