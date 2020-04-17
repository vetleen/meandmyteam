# Generated by Django 2.2.10 on 2020-04-17 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0005_remove_subscriber_department'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriber',
            name='payment_interval',
            field=models.CharField(blank=True, choices=[('m', 'monthly'), ('y', 'yearly')], default='', help_text='Payment interval', max_length=1),
        ),
    ]
