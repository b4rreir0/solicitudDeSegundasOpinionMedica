from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class SolicitudOpinion(models.Model):
    """Modelo para las solicitudes de segunda opinión médica"""
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('asignada', 'Asignada'),
        ('en_revision', 'En Revisión'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    paciente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solicitudes_paciente',
        help_text='Paciente que solicita la segunda opinión'
    )
    
    medico_asignado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_medico',
        help_text='Médico asignado para la segunda opinión'
    )
    
    titulo = models.CharField(
        max_length=200,
        help_text='Título breve de la solicitud'
    )
    
    descripcion_caso = models.TextField(
        help_text='Descripción detallada del caso médico'
    )
    
    diagnostico_inicial = models.TextField(
        blank=True,
        null=True,
        help_text='Diagnóstico inicial del médico tratante'
    )
    
    tratamiento_actual = models.TextField(
        blank=True,
        null=True,
        help_text='Tratamiento actual que está recibiendo el paciente'
    )
    
    especialidad_requerida = models.CharField(
        max_length=100,
        help_text='Especialidad médica requerida para la segunda opinión'
    )
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        help_text='Estado actual de la solicitud'
    )
    
    prioridad = models.CharField(
        max_length=20,
        choices=PRIORIDAD_CHOICES,
        default='media',
        help_text='Prioridad de la solicitud'
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_asignacion = models.DateTimeField(null=True, blank=True)
    fecha_completada = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Solicitud de Opinión'
        verbose_name_plural = 'Solicitudes de Opinión'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.titulo} - {self.paciente.username}"


class OpinionMedica(models.Model):
    """Modelo para las opiniones médicas emitidas"""
    
    solicitud = models.OneToOneField(
        SolicitudOpinion,
        on_delete=models.CASCADE,
        related_name='opinion_medica',
        help_text='Solicitud asociada a esta opinión'
    )
    
    medico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='opiniones_emitidas',
        help_text='Médico que emite la opinión'
    )
    
    diagnostico_propuesto = models.TextField(
        help_text='Diagnóstico propuesto por el médico'
    )
    
    recomendaciones = models.TextField(
        help_text='Recomendaciones del médico'
    )
    
    tratamiento_sugerido = models.TextField(
        blank=True,
        null=True,
        help_text='Tratamiento sugerido por el médico'
    )
    
    comentarios_adicionales = models.TextField(
        blank=True,
        null=True,
        help_text='Comentarios adicionales del médico'
    )
    
    requiere_seguimiento = models.BooleanField(
        default=False,
        help_text='Indica si el caso requiere seguimiento'
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Opinión Médica'
        verbose_name_plural = 'Opiniones Médicas'
    
    def __str__(self):
        return f"Opinión para: {self.solicitud.titulo}"


class Calificacion(models.Model):
    """Modelo para las calificaciones de las opiniones médicas"""
    
    opinion = models.OneToOneField(
        OpinionMedica,
        on_delete=models.CASCADE,
        related_name='calificacion',
        help_text='Opinión médica calificada'
    )
    
    paciente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='calificaciones_dadas',
        help_text='Paciente que califica la opinión'
    )
    
    puntuacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Puntuación del 1 al 5'
    )
    
    comentario = models.TextField(
        blank=True,
        null=True,
        help_text='Comentario del paciente sobre la opinión'
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Calificación'
        verbose_name_plural = 'Calificaciones'
    
    def __str__(self):
        return f"Calificación: {self.puntuacion}/5 - {self.opinion.solicitud.titulo}"


class Seguimiento(models.Model):
    """Modelo para el seguimiento de casos"""
    
    opinion = models.ForeignKey(
        OpinionMedica,
        on_delete=models.CASCADE,
        related_name='seguimientos',
        help_text='Opinión médica a la que pertenece el seguimiento'
    )
    
    medico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seguimientos_realizados',
        help_text='Médico que realiza el seguimiento'
    )
    
    observaciones = models.TextField(
        help_text='Observaciones del seguimiento'
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Seguimiento'
        verbose_name_plural = 'Seguimientos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Seguimiento - {self.opinion.solicitud.titulo} ({self.fecha_creacion.strftime('%d/%m/%Y')})"
