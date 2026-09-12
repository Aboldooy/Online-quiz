from django.urls import path

from . import views

urlpatterns = [
    path("", views.quiz_list, name="quiz_list"),
    path("new/", views.quiz_create, name="quiz_create"),
    path("join/", views.join_quiz, name="join_quiz"),
    path("history/", views.result_history, name="result_history"),
    path("<int:pk>/", views.quiz_detail, name="quiz_detail"),
    path("<int:pk>/edit/", views.quiz_edit, name="quiz_edit"),
    path("<int:pk>/delete/", views.quiz_delete, name="quiz_delete"),
    path("<int:quiz_pk>/questions/new/", views.question_create, name="question_create"),
    path("<int:pk>/start/", views.quiz_start, name="quiz_start"),
    path("attempts/<int:attempt_pk>/question/<int:number>/", views.attempt_question, name="attempt_question"),
    path("attempts/<int:attempt_pk>/results/", views.attempt_results, name="attempt_results"),
]
