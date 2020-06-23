# Generated by Django 2.2.10 on 2020-06-14 11:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('surveys', '0008_auto_20200614_1118'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dimension',
            name='scale',
        ),
        migrations.AddField(
            model_name='dimension',
            name='content_type',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='dimension',
            name='object_id',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
    ]