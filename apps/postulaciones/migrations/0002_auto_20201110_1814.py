# Generated by Django 3.1.2 on 2020-11-10 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('postulaciones', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='postulacion',
            name='nota',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='postulacion',
            name='semestreramo',
            field=models.CharField(default=1, max_length=6),
            preserve_default=False,
        ),
    ]
