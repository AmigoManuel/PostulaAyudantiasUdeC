# Generated by Django 3.1.5 on 2021-01-04 20:38

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('postulaciones', '0002_auto_20201110_1814'),
    ]

    operations = [
        migrations.AddField(
            model_name='ayudantia',
            name='fecha_ingreso',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
