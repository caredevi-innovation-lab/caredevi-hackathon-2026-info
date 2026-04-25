from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("ai_module", "0002_exercisesession"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ExerciseAnalysis",
        ),
    ]
