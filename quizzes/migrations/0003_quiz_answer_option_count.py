from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("quizzes", "0002_quiz_ordering")]

    operations = [
        migrations.AddField(
            model_name="quiz",
            name="answer_option_count",
            field=models.PositiveSmallIntegerField(default=4, verbose_name="Кількість варіантів відповіді"),
        ),
    ]
