from django.contrib import admin
from .models import SolicitudOpinion, OpinionMedica, Calificacion, Seguimiento


@admin.register(SolicitudOpinion)
class SolicitudOpinionAdmin(admin.ModelAdmin):
    """Configuración del admin para SolicitudOpinion"""
    list_display = ('titulo', 'paciente', 'estado', 'prioridad', 'fecha_creacion', 'fecha_actualizacion')
    list_filter = ('estado', 'prioridad', 'especialidad_requerida', 'fecha_creacion')
    search_fields = ('titulo', 'paciente__username', 'descripcion_caso')


@admin.register(OpinionMedica)
class OpinionMedicaAdmin(admin.ModelAdmin):
    """Configuración del admin para OpinionMedica"""
    list_display = ('solicitud', 'medico', 'fecha_creacion', 'fecha_actualizacion')
    search_fields = ('solicitud__titulo', 'medico__username', 'diagnostico_propuesto')


@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    """Configuración del admin para Calificacion"""
    list_display = ('opinion', 'puntuacion', 'paciente', 'fecha_creacion')
    list_filter = ('puntuacion', 'fecha_creacion')
    search_fields = ('opinion__solicitud__titulo', 'paciente__username', 'comentario')


@admin.register(Seguimiento)
class SeguimientoAdmin(admin.ModelAdmin):
    """Configuración del admin para Seguimiento"""
    list_display = ('opinion', 'medico', 'fecha_creacion')
    search_fields = ('opinion__solicitud__titulo', 'medico__username', 'observaciones')
