from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0002_alter_customuser_date_joined")]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="avatar",
            field=models.ImageField(blank=True, upload_to="avatars/", verbose_name="Аватар"),
        ),
    ]
