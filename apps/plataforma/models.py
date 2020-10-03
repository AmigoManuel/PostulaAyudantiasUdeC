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

    # Esta función se usa para representar el objeto al realizar una query
    def __str__(self):
        return '{}'.format(self.user)
