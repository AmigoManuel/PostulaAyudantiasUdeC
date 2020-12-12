import requests
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib import messages

from apps.plataforma.forms import RegistrarUsuarioForm, NuevoCursoForm, ActualizarPerfilForm
from apps.plataforma.models import Usuario, Curso


# Esta es una vista para creación de un modelo
# por eso hereda de CreateView

# ambos metodos retornan una lista con los dict de datos
def get_cursos_list(semestre, email):
    url = "http://proyectoinformatico.udec.cl/proyecto/1/2020{}00/{}".format(str(semestre), str.upper(email))
    json_data = requests.get(url).json()
    return json_data


def get_alumno_verify(email):
    url = "http://proyectoinformatico.udec.cl/proyecto/2/{}".format(str.upper(email))
    json_data = requests.get(url).json()
    return json_data


class RegistrarAlumno(CreateView):
    model = Usuario
    form_class = RegistrarUsuarioForm
    template_name = 'plataforma/registrar_alumno.html'
    success_url = reverse_lazy('iniciar_sesion')

    def get_context_data(self, **kwargs):
        context = super(RegistrarAlumno, self).get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.form_class(self.request.GET)
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)

            cursos_list = get_cursos_list(2, usuario.email)
            # Condición para que sea docente este semestre
            if len(cursos_list) > 0:
                return HttpResponse("es docente")
            else:
                alumno_verify = get_alumno_verify(usuario.email)
                # Condición para que sea docente
                if len(alumno_verify) > 0:
                    return HttpResponse("es alumno")
            return HttpResponse("no es nada")

    '''def form_valid(self, form):
        instance = form.save(commit=False)
        instance.username = instance.email

        emails = Usuario.objects.values_list('email', flat=True)
        for email in emails:
            if instance.email == email:
                messages.error(self.request, "Ya existe un usuario con esta dirección de correo.")
                return HttpResponseRedirect(self.request.path_info)
        instance.save()
        return HttpResponseRedirect(reverse_lazy('iniciar_sesion'))'''


# La vista de inciar sesión esta definida como función
# pueden utilizarla como quieran
# pero usarla como función es un poco feo -_-
def iniciar_sesion(request):
    # Metodos post en caso de hacer un POST obviously
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # redirect()
            # Instancia de objeto usuario
            usuario = Usuario.objects.get(username=username)
            # Almacena la pk de usuario para utilizar a futuro
            request.session['pk_usuario'] = usuario.pk
            request.session['es_docente'] = usuario.es_docente
            request.session['es_administrador'] = usuario.es_administrador
            request.session['first_name'] = usuario.first_name
            request.session['last_name'] = usuario.last_name
            request.session['email'] = usuario.email
            # Redirige
            return HttpResponseRedirect(reverse('plataforma:dashboard'))
        pass

    # Contexto con variables que se le entrega al template
    context = {}
    # Despliega el template dentro del navegador
    return render(request, 'plataforma/login.html', context)


def cerrar_sesion(request):
    # Finalizamos la sesión
    logout(request)
    # Redireccionamos a la portada
    return HttpResponseRedirect(reverse('navegacion:inicio'))


# Pantalla principal luego de inciar sesión
class Dashboard(LoginRequiredMixin, TemplateView):
    login_url = '/iniciar/'
    template_name = 'plataforma/dashboard.html'


class RegistrarDocente(UserPassesTestMixin, CreateView):
    login_url = '/iniciar/'
    model = Usuario
    form_class = RegistrarUsuarioForm
    template_name = 'plataforma/registrar_docente.html'
    success_url = reverse_lazy('plataforma:registrar_docente')

    def test_func(self):
        return self.request.session.get('es_administrador')

    def get_context_data(self, **kwargs):
        context = super(RegistrarDocente, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.username = instance.email
        instance.es_docente = True

        emails = Usuario.objects.values_list('email', flat=True)
        for email in emails:
            if instance.email == email:
                messages.error(self.request, "Ya existe un usuario con esta dirección de correo.")
                return HttpResponseRedirect(self.request.path_info)

        instance.save()
        return HttpResponseRedirect(reverse_lazy('plataforma:dashboard'))


class NuevoCurso(UserPassesTestMixin, CreateView):
    login_url = '/iniciar/'
    model = Curso
    form_class = NuevoCursoForm
    template_name = 'plataforma/nuevo_curso.html'
    success_url = reverse_lazy('plataforma:nuevo_curso')

    def test_func(self):
        return self.request.session.get('es_docente')

    def form_valid(self, form):
        instance = form.save(commit=False)

        codigos = Curso.objects.values_list('codigo', flat=True)
        for codigo in codigos:
            if instance.codigo == codigo:
                messages.error(self.request, "Ya existe este curso.")
                return HttpResponseRedirect(self.request.path_info)

        docente = Usuario.objects.get(pk=self.request.session.get('pk_usuario', ''))
        instance.docente = docente
        instance.save()
        return HttpResponseRedirect(reverse_lazy('plataforma:nuevo_curso'))


# Editar perfil
class ActualizarPerfil(LoginRequiredMixin, UpdateView):
    login_url = '/iniciar/'
    model = Usuario
    form_class = ActualizarPerfilForm
    template_name = 'plataforma/editar_perfil.html'

    def get_context_data(self, **kwargs):
        context = super(ActualizarPerfil, self).get_context_data()
        # Determina si el perfil ingresado por pk es mio
        context['mi_perfil'] = False
        path = self.request.path_info.split("/")
        if self.request.session.get('pk_usuario', '') == int(path[-2]):
            context['mi_perfil'] = True
        return context

    def get_success_url(self):
        return reverse('plataforma:perfil', kwargs={'pk': self.object.pk})
