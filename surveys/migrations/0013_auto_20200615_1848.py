# Generated by Django 2.2.10 on 2020-06-15 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0012_auto_20200615_0953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instrument',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]