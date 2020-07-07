# Generated by Django 2.2.10 on 2020-07-07 09:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0025_auto_20200702_1344'),
    ]

    operations = [
        migrations.CreateModel(
            name='RespondentEmail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_date', models.DateField(blank=True, null=True)),
                ('category', models.CharField(max_length=255)),
                ('error_message', models.CharField(blank=True, max_length=255, null=True)),
                ('survey_instance', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='surveys.SurveyInstance')),
            ],
        ),
    ]
