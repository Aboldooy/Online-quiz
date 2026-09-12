import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone


def invitation_code():
    return secrets.token_urlsafe(6).upper()[:8]


class Quiz(models.Model):
    title = models.CharField("Назва", max_length=160)
    description = models.TextField("Опис", blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quizzes")
    invite_code = models.CharField("Код запрошення", max_length=8, unique=True, default=invitation_code, editable=False)
    is_published = models.BooleanField("Опублікована", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def question_count(self):
        return self.questions.count()


class Question(models.Model):
    class Kind(models.TextChoices):
        TEXT = "text", "Текст"
        IMAGE = "image", "Зображення"
        VIDEO = "video", "Відео"

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField("Запитання")
    kind = models.CharField("Тип", max_length=10, choices=Kind.choices, default=Kind.TEXT)
    media_url = models.URLField("Посилання на медіа", blank=True)
    time_limit = models.PositiveSmallIntegerField("Час на відповідь, сек.", default=30)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return self.text[:60]


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    text = models.CharField("Варіант відповіді", max_length=400)
    is_correct = models.BooleanField("Правильна відповідь", default=False)

    def __str__(self):
        return self.text


class Attempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    participant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quiz_attempts")
    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)
    score = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-score", "finished_at", "started_at"]

    @property
    def is_finished(self):
        return self.finished_at is not None


class SubmittedAnswer(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="submitted_answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.SET_NULL, null=True, blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["attempt", "question"], name="one_answer_per_question")]
