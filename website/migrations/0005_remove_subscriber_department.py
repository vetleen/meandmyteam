# Generated by Django 2.2.10 on 2020-04-17 12:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_auto_20200417_1431'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscriber',
            name='department',
        ),
    ]
