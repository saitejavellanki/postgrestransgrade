# Generated by Django 5.1.9 on 2025-06-19 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ocrtesting", "0015_alter_result_graded_alter_result_scored"),
    ]

    operations = [
        migrations.AddField(
            model_name="keyocr",
            name="referenceScript",
            field=models.JSONField(default={}),
            preserve_default=False,
        ),
    ]
