from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import JoinQuizForm, QuestionForm, QuizForm, answer_formset
from .models import Attempt, Question, Quiz, SubmittedAnswer


def can_manage(user, quiz):
    return user.is_staff or user.is_admin_role


def is_quiz_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_admin_role)


def quiz_list(request):
    query = request.GET.get("q", "").strip()
    quizzes = Quiz.objects.filter(is_published=True).select_related("author").annotate(answer_count=Count("attempts")).order_by("-created_at", "-id")
    if query:
        quizzes = quizzes.filter(Q(title__icontains=query) | Q(description__icontains=query))
    return render(request, "quizzes/list.html", {"quizzes": quizzes, "query": query})


def home(request):
    quizzes = Quiz.objects.filter(is_published=True).select_related("author").order_by("-created_at", "-id")[:3]
    return render(request, "home.html", {"quizzes": quizzes})


def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz.objects.select_related("author"), pk=pk)
    if not quiz.is_published and not (request.user.is_authenticated and can_manage(request.user, quiz)):
        raise PermissionDenied
    return render(request, "quizzes/detail.html", {"quiz": quiz, "can_manage": is_quiz_admin(request.user)})


@login_required
def quiz_create(request):
    if not is_quiz_admin(request.user):
        raise PermissionDenied
    form = QuizForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        quiz = form.save(commit=False)
        quiz.author = request.user
        quiz.save()
        messages.success(request, "Вікторину створено. Додайте перше запитання.")
        return redirect("question_create", quiz_pk=quiz.pk)
    return render(request, "quizzes/quiz_form.html", {"form": form, "heading": "Нова вікторина"})


@login_required
def quiz_edit(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    if not can_manage(request.user, quiz):
        raise PermissionDenied
    form = QuizForm(request.POST or None, instance=quiz)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Вікторину оновлено.")
        return redirect("quiz_detail", pk=quiz.pk)
    return render(request, "quizzes/quiz_form.html", {"form": form, "heading": "Редагувати вікторину", "quiz": quiz})


@login_required
def quiz_delete(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    if not can_manage(request.user, quiz):
        raise PermissionDenied
    if request.method == "POST":
        quiz.delete()
        messages.success(request, "Вікторину видалено.")
        return redirect("quiz_list")
    return render(request, "quizzes/quiz_confirm_delete.html", {"quiz": quiz})


@login_required
def question_create(request, quiz_pk):
    quiz = get_object_or_404(Quiz, pk=quiz_pk)
    if not can_manage(request.user, quiz):
        raise PermissionDenied
    question_form = QuestionForm(request.POST or None, request.FILES or None)
    formset = answer_formset(data=request.POST or None, instance=Question(quiz=quiz), extra=quiz.answer_option_count)
    if request.method == "POST" and question_form.is_valid() and formset.is_valid():
        answers = [form for form in formset if form.cleaned_data and not form.cleaned_data.get("DELETE")]
        if len(answers) < 2 or not any(form.cleaned_data.get("is_correct") for form in answers):
            messages.error(request, "Додайте щонайменше дві відповіді та позначте правильну.")
        else:
            question = question_form.save(commit=False)
            question.quiz = quiz
            question.save()
            formset.instance = question
            formset.save()
            messages.success(request, "Запитання додано.")
            return redirect("quiz_detail", pk=quiz.pk)
    return render(request, "quizzes/question_form.html", {"quiz": quiz, "question_form": question_form, "formset": formset})


@login_required
def join_quiz(request):
    form = JoinQuizForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        quiz = Quiz.objects.filter(invite_code__iexact=form.cleaned_data["invite_code"], is_published=True).first()
        if quiz:
            return redirect("quiz_start", pk=quiz.pk)
        form.add_error("invite_code", "Вікторину з таким кодом не знайдено.")
    return render(request, "quizzes/join.html", {"form": form})


@login_required
def quiz_start(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, is_published=True)
    now = timezone.now()
    if quiz.timing_mode == Quiz.TimingMode.SCHEDULED:
        if now < quiz.available_from:
            messages.error(request, f"Вікторина буде доступна {timezone.localtime(quiz.available_from):%d.%m.%Y о %H:%M}.")
            return redirect("quiz_detail", pk=quiz.pk)
        if now >= quiz.available_until:
            messages.error(request, "Період проходження цієї вікторини завершився.")
            return redirect("quiz_detail", pk=quiz.pk)
    if not quiz.questions.exists():
        messages.error(request, "У цій вікторині ще немає запитань.")
        return redirect("quiz_detail", pk=quiz.pk)
    attempt = Attempt.objects.filter(quiz=quiz, participant=request.user, finished_at__isnull=True).first()
    if attempt is None:
        attempt = Attempt.objects.create(quiz=quiz, participant=request.user)
    return redirect("attempt_question", attempt_pk=attempt.pk, number=1)


@login_required
def attempt_question(request, attempt_pk, number):
    attempt = get_object_or_404(Attempt.objects.select_related("quiz"), pk=attempt_pk, participant=request.user)
    if attempt.is_finished:
        return redirect("attempt_results", attempt_pk=attempt.pk)
    if attempt.quiz.timing_mode == Quiz.TimingMode.SCHEDULED:
        deadline = attempt.quiz.available_until
    else:
        deadline = attempt.started_at + timedelta(minutes=attempt.quiz.duration_minutes)
    now = timezone.now()
    if now >= deadline:
        attempt.finished_at = deadline
        attempt.save(update_fields=["finished_at"])
        return redirect("attempt_results", attempt_pk=attempt.pk)
    questions = list(attempt.quiz.questions.prefetch_related("answers"))
    if number > len(questions):
        attempt.finished_at = timezone.now()
        attempt.save(update_fields=["finished_at"])
        return redirect("attempt_results", attempt_pk=attempt.pk)
    question = questions[number - 1]
    existing = SubmittedAnswer.objects.filter(attempt=attempt, question=question).first()
    if existing:
        return redirect("attempt_question", attempt_pk=attempt.pk, number=number + 1)
    if request.method == "POST":
        if timezone.now() >= deadline:
            attempt.finished_at = deadline
            attempt.save(update_fields=["finished_at"])
            return redirect("attempt_results", attempt_pk=attempt.pk)
        chosen = question.answers.filter(pk=request.POST.get("answer")).first()
        correct = bool(chosen and chosen.is_correct)
        SubmittedAnswer.objects.create(attempt=attempt, question=question, answer=chosen, is_correct=correct)
        if correct:
            attempt.score += 1
            attempt.save(update_fields=["score"])
        return redirect("attempt_question", attempt_pk=attempt.pk, number=number + 1)
    seconds_left = max(0, int((deadline - now).total_seconds()))
    return render(request, "quizzes/play.html", {"attempt": attempt, "question": question, "number": number, "total": len(questions), "seconds_left": seconds_left})


@login_required
def attempt_results(request, attempt_pk):
    attempt = get_object_or_404(Attempt.objects.select_related("quiz"), pk=attempt_pk, participant=request.user)
    if not attempt.finished_at:
        return redirect("attempt_question", attempt_pk=attempt.pk, number=attempt.submitted_answers.count() + 1)
    ranking = Attempt.objects.filter(quiz=attempt.quiz, finished_at__isnull=False).select_related("participant").order_by("-score", "finished_at")
    return render(request, "quizzes/results.html", {"attempt": attempt, "ranking": ranking})


@login_required
def result_history(request):
    attempts = Attempt.objects.filter(participant=request.user, finished_at__isnull=False).select_related("quiz")
    return render(request, "quizzes/history.html", {"attempts": attempts})
