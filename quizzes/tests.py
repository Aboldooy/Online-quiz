from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Answer, Attempt, Question, Quiz


class QuizFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="player", password="safe-password-123")
        self.quiz = Quiz.objects.create(title="Столиці", author=self.user)
        self.question = Question.objects.create(quiz=self.quiz, text="Столиця України?", time_limit=30)
        self.correct = Answer.objects.create(question=self.question, text="Київ", is_correct=True)
        Answer.objects.create(question=self.question, text="Львів")

    def test_search_finds_quiz(self):
        self.assertContains(self.client.get(reverse("quiz_list"), {"q": "Столиці"}), "Столиці")

    def test_correct_answer_adds_point_and_finishes(self):
        self.client.login(username="player", password="safe-password-123")
        self.client.get(reverse("quiz_start", args=[self.quiz.pk]))
        attempt = Attempt.objects.get(participant=self.user, quiz=self.quiz)
        response = self.client.post(reverse("attempt_question", args=[attempt.pk, 1]), {"answer": self.correct.pk})
        self.assertEqual(response.url, reverse("attempt_question", args=[attempt.pk, 2]))
        self.client.get(reverse("attempt_question", args=[attempt.pk, 2]))
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, 1)
        self.assertIsNotNone(attempt.finished_at)

    def test_non_author_cannot_edit(self):
        other = get_user_model().objects.create_user(username="other", password="safe-password-123")
        self.client.login(username=other.username, password="safe-password-123")
        self.assertEqual(self.client.get(reverse("quiz_edit", args=[self.quiz.pk])).status_code, 403)

    def test_regular_user_cannot_create_quiz(self):
        self.client.login(username="player", password="safe-password-123")
        self.assertEqual(self.client.get(reverse("quiz_create")).status_code, 403)

    def test_admin_can_create_quiz(self):
        self.user.role = "admin"
        self.user.save(update_fields=["role"])
        self.client.login(username="player", password="safe-password-123")
        self.assertEqual(self.client.get(reverse("quiz_create")).status_code, 200)
