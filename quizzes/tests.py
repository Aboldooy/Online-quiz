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

    def test_home_shows_quizzes_and_search(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Столиці")
        self.assertContains(response, "Усі вікторини")

    def test_home_shows_only_three_newest_quizzes(self):
        Quiz.objects.create(title="Друга", author=self.user)
        Quiz.objects.create(title="Третя", author=self.user)
        Quiz.objects.create(title="Четверта", author=self.user)
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Четверта")
        self.assertNotContains(response, "Столиці")

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
        response = self.client.post(reverse("quiz_create"), {"title": "Недоступна вікторина"})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Quiz.objects.filter(title="Недоступна вікторина").exists())

    def test_admin_can_create_quiz(self):
        self.user.role = "admin"
        self.user.save(update_fields=["role"])
        self.client.login(username="player", password="safe-password-123")
        self.assertEqual(self.client.get(reverse("quiz_create")).status_code, 200)

    def test_quiz_uses_selected_answer_option_count(self):
        self.user.role = "admin"
        self.user.save(update_fields=["role"])
        quiz = Quiz.objects.create(title="П'ять варіантів", author=self.user, answer_option_count=5)
        self.client.login(username="player", password="safe-password-123")
        response = self.client.get(reverse("question_create", args=[quiz.pk]))
        self.assertEqual(len(response.context["formset"].forms), 5)
        self.assertContains(response, "Додати варіант відповіді")
