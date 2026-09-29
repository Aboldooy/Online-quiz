from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone

from .models import Answer, Question, Quiz


class QuizForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("available_from", "available_until"):
            value = self.initial.get(name)
            if value:
                if timezone.is_aware(value):
                    value = timezone.localtime(value)
                self.initial[name] = value.strftime("%Y-%m-%dT%H:%M")

    def clean(self):
        cleaned = super().clean()
        duration = cleaned.get("duration_minutes")
        if duration is not None and not 1 <= duration <= 1440:
            self.add_error("duration_minutes", "Час має бути від 1 хвилини до 24 годин.")
        if cleaned.get("timing_mode") == Quiz.TimingMode.SCHEDULED:
            start, end = cleaned.get("available_from"), cleaned.get("available_until")
            if not start:
                self.add_error("available_from", "Вкажіть початок періоду.")
            if not end:
                self.add_error("available_until", "Вкажіть кінець періоду.")
            if start and end and end <= start:
                self.add_error("available_until", "Кінець періоду має бути пізніше за початок.")
        return cleaned

    class Meta:
        model = Quiz
        fields = ("title", "description", "answer_option_count", "timing_mode", "duration_minutes", "available_from", "available_until", "is_published")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Введіть назву вікторини"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Введіть опис вікторини"}),
            "answer_option_count": forms.Select(attrs={"class": "form-select"}, choices=[(number, str(number)) for number in range(2, 9)]),
            "timing_mode": forms.Select(attrs={"class": "form-select", "id": "id_timing_mode"}),
            "duration_minutes": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 1440}),
            "available_from": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "available_until": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "is_published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ("text", "kind", "image", "video", "media_url", "time_limit", "position")
        widgets = {
            "text": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Введіть запитання"}),
            "kind": forms.Select(attrs={"class": "form-select"}),
            "media_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "Введіть посилання на медіа"}),
            "image": forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "video": forms.FileInput(attrs={"class": "form-control", "accept": "video/*"}),
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


def answer_formset(*, data=None, instance=None, extra=4):
    formset_class = inlineformset_factory(
        Question, Answer, form=AnswerForm, extra=extra, max_num=8, validate_max=True, can_delete=True
    )
    return formset_class(data=data, instance=instance, prefix="answers")


class JoinQuizForm(forms.Form):
    invite_code = forms.CharField(label="Код запрошення", max_length=8, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Введіть код запрошення"}))
