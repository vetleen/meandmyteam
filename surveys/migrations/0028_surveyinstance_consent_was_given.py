# Generated by Django 2.2.10 on 2020-07-20 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0027_auto_20200707_2124'),
    ]

    operations = [
        migrations.AddField(
            model_name='surveyinstance',
            name='consent_was_given',
            field=models.BooleanField(default=False),
        ),
    ]