from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "you@example.com"}))

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email", "password1", "password2")
        widgets = {"username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ваш нікнейм"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("password1", "password2"):
            self.fields[name].widget.attrs.update({"class": "form-control", "placeholder": "Не менше 8 символів"})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.role = CustomUser.Role.USER
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("avatar", "first_name", "last_name", "email")
        labels = {"first_name": "Ім'я", "last_name": "Прізвище", "email": "Email"}
        widgets = {
            "avatar": forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ваше ім'я"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ваше прізвище"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "you@example.com"}),
        }

