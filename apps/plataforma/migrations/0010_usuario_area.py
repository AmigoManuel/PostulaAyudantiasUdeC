# Generated by Django 3.1.3 on 2020-11-05 23:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plataforma', '0009_auto_20201105_2020'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='area',
            field=models.CharField(choices=[(0, 'Pregrado'), (1, 'Postgrado'), (2, 'Externo')], default=0, max_length=20),
        ),
    ]
