from django.contrib import admin

from .models import Answer, Attempt, Question, Quiz, SubmittedAnswer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 2


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "invite_code", "is_published", "created_at")
    list_filter = ("is_published",)
    search_fields = ("title", "description", "invite_code")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "quiz", "kind", "time_limit", "position")
    inlines = (AnswerInline,)


admin.site.register((Answer, Attempt, SubmittedAnswer))
