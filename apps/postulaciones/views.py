from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, UpdateView
from django.contrib import messages
from django.views.generic.detail import SingleObjectMixin

from apps.plataforma.views import semestre_actual
from apps.postulaciones.forms import RegistrarPostulacionAyudantia, RegistrarPostulacionAlumno
from apps.plataforma.models import Curso, Usuario
from apps.postulaciones.models import Ayudantia, Postulacion
from django import forms


class OfertasAyudantias(LoginRequiredMixin, ListView):
    login_url = '/iniciar/'
    model = Postulacion
    form_class = RegistrarPostulacionAlumno
    template_name = 'plataforma/desplegar_ofertas_ayudantias.html'

    # Filtra las ayudantias a las cuales ya he postulado
    def get_queryset(self):
        alumno = Usuario.objects.get(pk=self.request.session.get('pk_usuario', ''))
        postulaciones = Postulacion.objects.filter(alumno=alumno)
        return Ayudantia.objects.exclude(postulacion__in=postulaciones)

    def post(self, request, *args, **kwargs):
        id_ayudantia = request.POST.get('id_ayudantia')
        semestreramo = request.POST.get('semestre')
        nota = request.POST.get('nota')
        ayudantia = Ayudantia.objects.get(pk=id_ayudantia)
        alumno = Usuario.objects.get(pk=self.request.session.get('pk_usuario', ''))
        Postulacion.objects.create(
            alumno=alumno,
            ayudantia=ayudantia,
            semestreramo=semestreramo,
            nota=nota
        )
        return HttpResponseRedirect(reverse_lazy('postulaciones:listar_ofertas'))


class NuevaPostulacion(UserPassesTestMixin, CreateView):
    login_url = '/iniciar/'  # Redirecciona en caso de no haber iniciado sesión
    model = Postulacion
    form_class = RegistrarPostulacionAlumno
    template_name = 'postulaciones/generar_postulacion.html'
    success_url = reverse_lazy('postulaciones:generar_postulacion')

    def test_func(self):
        return not (self.request.session.get('es_docente'))

    # Crea una postualción sobre la ayudantía escogida


class NuevaAyudantia(UserPassesTestMixin, CreateView):
    login_url = '/iniciar/'  # Redirecciona en caso de no haber iniciado sesión
    model = Ayudantia
    form_class = RegistrarPostulacionAyudantia
    template_name = 'postulaciones/nueva_ayudantia.html'
    success_url = reverse_lazy('postulaciones:nueva_ayudantia')

    # Comprueba que el usuario accediendo es docente
    def test_func(self):
        return self.request.session.get('es_docente')

    def get_context_data(self, **kwargs):
        context = super(NuevaAyudantia, self).get_context_data(**kwargs)
        docente = Usuario.objects.get(pk=self.request.session.get('pk_usuario', ''))
        cursos = Curso.objects.filter(docente=docente)  # QS con todos los cursos del docente
        # Se eliminan los cursos que ya tienen ayudantías
        cursos_con_ayudantias = Ayudantia.objects.filter(curso__in=cursos)  # QS de ayudantias con sus cursos ocupados
        cursos_excluidos = Curso.objects.filter(id__in=cursos_con_ayudantias.values('curso'))  # QS de los cursos que ya tienen ayudantia
        cursos = cursos.difference(cursos_excluidos)  # cursos diponibles para ofertar, equivalente a un EXCEPT en sql
        context['form'].fields['curso'] = forms.ModelChoiceField(
            queryset=cursos,
            empty_label="Seleccione curso",
            widget=forms.Select(attrs={'class': 'form-control'})
        )
        return context

    def form_valid(self, form):
        ayudantia = form.save(commit=False)
        ayudantia.semestre = semestre_actual  # Se asigna el semestre actual a la ayudantía
        ayudantia.save()
        return HttpResponseRedirect(reverse_lazy('postulaciones:nueva_ayudantia'))


# Postulaciones realizadas sobre mis ayudantias ofrecidas
class PostulacionesRealizadas(ListView):
    model = Postulacion
    template_name = 'postulaciones/postulaciones_realizadas.html'

    # Filtra las postulaciones sobre mis ayudantias
    def get_queryset(self):
        docente = Usuario.objects.get(pk=self.request.session.get('pk_usuario', ''))
        ayudantias = Ayudantia.objects.filter(curso__docente=docente)
        return Postulacion.objects.filter(ayudantia__in=ayudantias)

    def post(self, request, *args, **kwargs):
        id_postulacion = request.POST.get('id_postulacion')
        postulacion = Postulacion.objects.filter(pk=id_postulacion)
        ayudantia = postulacion[0].ayudantia

        if request.POST.get('data-accept') == "True":
            postulacion.update(
                estado=True
            )

            Ayudantia.objects.filter(pk=ayudantia.id).update(
                puestos=ayudantia.puestos - 1
            )
        else:
            postulacion.delete()

        return HttpResponseRedirect(reverse('postulaciones:mis_ayudantias'))


class PostulacionesAlumno(ListView):
    model = Postulacion
    template_name = 'postulaciones/postulaciones_alumno.html'

    def get_queryset(self):
        alumno = Usuario.objects.get(pk=self.request.session.get('pk_usuario', ''))
        return Postulacion.objects.filter(alumno=alumno)
