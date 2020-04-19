# Generated by Django 2.2.10 on 2020-04-19 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_auto_20200418_1800'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriber',
            name='stripe_id',
            field=models.CharField(blank=True, default=None, help_text='Subscribers Customer object ID in Stripe API', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='salesargument',
            name='badge_text',
            field=models.CharField(blank=True, default=None, help_text='What should the badge (if any) say?', max_length=255, null=True),
        ),
    ]
