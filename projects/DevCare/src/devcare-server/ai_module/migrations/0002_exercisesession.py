from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ai_module", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ExerciseSession",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("exercise", models.CharField(max_length=64)),
                ("reps", models.PositiveIntegerField(default=0)),
                ("avg_range", models.FloatField(default=0.0)),
                ("form_accuracy", models.FloatField(default=0.0)),
                ("duration", models.FloatField(default=0.0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "patient",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="exercise_sessions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
