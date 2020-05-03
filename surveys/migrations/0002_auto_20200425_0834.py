# Generated by Django 2.2.10 on 2020-04-25 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='address_line_1',
            field=models.CharField(blank=True, help_text='Adress of the Organization', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='address_line_2',
            field=models.CharField(blank=True, help_text='Address contd.', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='city',
            field=models.CharField(blank=True, help_text='City where the Organization is located', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='country',
            field=models.CharField(blank=True, help_text='Country where the Organization is located', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='zip_code',
            field=models.CharField(blank=True, help_text='Zip code of the Organization', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.CharField(blank=True, help_text='Name of the Organization', max_length=255, null=True),
        ),
    ]