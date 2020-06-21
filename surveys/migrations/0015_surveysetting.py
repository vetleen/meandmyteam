# Generated by Django 2.2.10 on 2020-06-19 09:23

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0006_organization_stripe_subscription_quantity'),
        ('surveys', '0014_auto_20200617_1343'),
    ]

    operations = [
        migrations.CreateModel(
            name='SurveySetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, help_text='This instrument is active for this organization')),
                ('survey_interval', models.SmallIntegerField(default=90, help_text='How many days between each survey', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(730)])),
                ('surveys_remain_open_days', models.SmallIntegerField(default=10, help_text='How many days should surveys be open for this organization', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(365)])),
                ('instrument', models.ForeignKey(help_text='Instruments this organization is using', on_delete=django.db.models.deletion.CASCADE, to='surveys.Instrument')),
                ('organization', models.ForeignKey(help_text='Organization this setting applies to', on_delete=django.db.models.deletion.CASCADE, to='website.Organization')),
            ],
        ),
    ]
