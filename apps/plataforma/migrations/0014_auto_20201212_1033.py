# Generated by Django 3.1.4 on 2020-12-12 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plataforma', '0013_auto_20201212_0945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='etapa_carrera',
            field=models.IntegerField(choices=[(1, 'Primer año'), (2, 'Segundo año'), (3, 'Tercer año'), (4, 'Cuarto año'), (5, 'Quinto año'), (6, 'Sexto año o superior'), (7, 'No aplica')], default=0),
        ),
    ]
