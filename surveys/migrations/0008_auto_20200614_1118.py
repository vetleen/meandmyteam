# Generated by Django 2.2.10 on 2020-06-14 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0007_auto_20200614_1108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instrument',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
