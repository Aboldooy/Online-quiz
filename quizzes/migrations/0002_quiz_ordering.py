from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("quizzes", "0001_initial")]

    operations = [
        migrations.AlterModelOptions(
            name="quiz",
            options={"ordering": ["-created_at", "-id"]},
        ),
    ]
