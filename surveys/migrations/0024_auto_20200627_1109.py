# Generated by Django 2.2.10 on 2020-06-27 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0023_surveysetting_surveys'),
    ]

    operations = [
        migrations.AlterField(
            model_name='surveysetting',
            name='surveys',
            field=models.ManyToManyField(blank=True, to='surveys.Survey'),
        ),
    ]
