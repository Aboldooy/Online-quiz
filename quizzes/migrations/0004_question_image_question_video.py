from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("quizzes", "0003_quiz_answer_option_count")]

    operations = [
        migrations.AddField(model_name="question", name="image", field=models.ImageField(blank=True, upload_to="quiz_media/images/", verbose_name="Зображення")),
        migrations.AddField(model_name="question", name="video", field=models.FileField(blank=True, upload_to="quiz_media/videos/", verbose_name="Відео")),
    ]
