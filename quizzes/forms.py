from django import forms
from django.forms import inlineformset_factory

from .models import Answer, Question, Quiz


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ("title", "description", "is_published")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Наприклад, Географія світу"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Коротко опишіть тему та правила"}),
            "is_published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ("text", "kind", "media_url", "time_limit", "position")
        widgets = {
            "text": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Введіть запитання"}),
            "kind": forms.Select(attrs={"class": "form-select"}),
            "media_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://..."}),
            "time_limit": forms.NumberInput(attrs={"class": "form-control", "min": 5, "max": 600}),
            "position": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ("text", "is_correct")
        widgets = {
            "text": forms.TextInput(attrs={"class": "form-control", "placeholder": "Варіант відповіді"}),
            "is_correct": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


AnswerFormSet = inlineformset_factory(Question, Answer, form=AnswerForm, extra=4, max_num=8, validate_max=True, can_delete=True)


class JoinQuizForm(forms.Form):
    invite_code = forms.CharField(label="Код запрошення", max_length=8, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Наприклад, AB12CD34"}))
