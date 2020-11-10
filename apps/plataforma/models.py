from django.contrib.auth.models import User
from django.db import models


# Usuario hereda de User
# Atributos y metodos de User => https://docs.djangoproject.com/en/3.1/ref/contrib/auth/
class Usuario(User):
    # Herencia de atributos desde User
    user = models.OneToOneField(User, parent_link=True, on_delete=models.CASCADE)
    # Identificadores para tipo de usuario
    es_administrador = models.BooleanField(default=False)
    es_docente = models.BooleanField(default=False)
    # Información adicional
    intereses = models.TextField()
    ETAPAS = (
        (0, 'Primer año'),
        (1, 'Segundo año'),
        (2, 'Tercer año'),
        (3, 'Cuarto año'),
        (4, 'Quinto año'),
        (5, 'Sexto año o superior')
    )
    AREAS = (
        ('0', 'Pregrado'),
        ('1', 'Postgrado'),
        ('2', 'Externo')
    )
    etapa_carrera = models.IntegerField(default=0, choices=ETAPAS)
    area = models.CharField(max_length=20, default=0, choices=AREAS)

    # Esta función se usa para representar el objeto al realizar una query
    def __str__(self):
        return '{} {}'.format(self.user.first_name, self.user.last_name)


class Curso(models.Model):
    docente = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    # Atributos
    codigo = models.PositiveBigIntegerField(default=0)
    nombre = models.CharField(max_length=50, null=False)
    descripcion = models.TextField()

    def __str__(self):
        return '({}) {}'.format(self.codigo, self.nombre)
