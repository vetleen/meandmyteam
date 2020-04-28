# Generated by Django 2.2.10 on 2020-04-28 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0004_auto_20200426_1513'),
    ]

    operations = [
        migrations.AddField(
            model_name='surveyinstance',
            name='last_reminder',
            field=models.DateField(blank=True, help_text='Last reminder was sent', null=True),
        ),
        migrations.AddField(
            model_name='surveyinstance',
            name='sent_initial',
            field=models.BooleanField(default=False, help_text='This SI has been sent once, the initial time'),
        ),
    ]
