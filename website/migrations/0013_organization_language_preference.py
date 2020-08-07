# Generated by Django 2.2.13 on 2020-08-07 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0012_auto_20200730_1455'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='language_preference',
            field=models.CharField(blank=True, choices=[('en-us', 'English'), ('nb', 'Norsk')], help_text='Language preference', max_length=255, null=True),
        ),
    ]
