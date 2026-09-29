from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("quizzes", "0004_question_image_question_video")]

    operations = [
        migrations.AddField(
            model_name="quiz",
            name="timing_mode",
            field=models.CharField(choices=[("duration", "Загальний час на проходження"), ("scheduled", "Проходження у визначений період")], default="duration", max_length=12, verbose_name="Режим часу"),
        ),
        migrations.AddField(
            model_name="quiz",
            name="duration_minutes",
            field=models.PositiveSmallIntegerField(default=30, verbose_name="Час на тест, хв."),
        ),
        migrations.AddField(
            model_name="quiz",
            name="available_from",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Початок періоду проходження"),
        ),
        migrations.AddField(
            model_name="quiz",
            name="available_until",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Кінець періоду проходження"),
        ),
    ]
