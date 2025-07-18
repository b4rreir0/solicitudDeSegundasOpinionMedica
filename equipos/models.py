from django.db import models
from django.conf import settings
from usuarios.models import Usuario


class EspecialidadOncologica(models.Model):
    """Especialidades oncológicas disponibles"""
    
    nombre = models.CharField(
        max_length=100,
        unique=True,
        help_text='Nombre de la especialidad oncológica'
    )
    
    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text='Descripción de la especialidad'
    )
    
    icono = models.CharField(
        max_length=50,
        default='fas fa-stethoscope',
        help_text='Icono FontAwesome para la especialidad'
    )
    
    activo = models.BooleanField(
        default=True,
        help_text='Indica si la especialidad está activa'
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Especialidad Oncológica'
        verbose_name_plural = 'Especialidades Oncológicas'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class EquipoTrabajo(models.Model):
    """Equipos de trabajo multidisciplinarios para oncología"""
    
    nombre = models.CharField(
        max_length=200,
        unique=True,
        help_text='Nombre del equipo de trabajo'
    )
    
    especialidad = models.ForeignKey(
        EspecialidadOncologica,
        on_delete=models.CASCADE,
        related_name='equipos',
        help_text='Especialidad oncológica del equipo'
    )
    
    descripcion = models.TextField(
        help_text='Descripción del equipo y sus funciones'
    )
    
    coordinador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='equipos_coordinados',
        help_text='Médico coordinador del equipo'
    )
    
    miembros = models.ManyToManyField(
        Usuario,
        through='MiembroEquipo',
        related_name='equipos_miembro',
        help_text='Miembros del equipo'
    )
    
    activo = models.BooleanField(
        default=True,
        help_text='Indica si el equipo está activo'
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Equipo de Trabajo'
        verbose_name_plural = 'Equipos de Trabajo'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.especialidad.nombre}"
    
    @property
    def total_miembros(self):
        return self.miembros.count()
    
    @property
    def solicitudes_activas(self):
        return self.solicitudes_asignadas.filter(estado__in=['asignada', 'en_revision']).count()


class MiembroEquipo(models.Model):
    """Tabla intermedia para miembros de equipos con información adicional"""
    
    ROLES_EQUIPO = [
        ('coordinador', 'Coordinador'),
        ('oncologo', 'Oncólogo'),
        ('radiologo', 'Radiólogo'),
        ('patologo', 'Patólogo'),
        ('cirujano', 'Cirujano'),
        ('radioterapeuta', 'Radioterapeuta'),
        ('enfermero', 'Enfermero Oncológico'),
        ('psicologo', 'Psicólogo'),
        ('nutricionista', 'Nutricionista'),
        ('farmaceutico', 'Farmacéutico'),
        ('otro', 'Otro'),
    ]
    
    equipo = models.ForeignKey(
        EquipoTrabajo,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='team_memberships'
    )
    
    rol_en_equipo = models.CharField(
        max_length=20,
        choices=ROLES_EQUIPO,
        default='oncologo',
        help_text='Rol del miembro en el equipo'
    )
    
    fecha_incorporacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Miembro de Equipo'
        verbose_name_plural = 'Miembros de Equipo'
        unique_together = ['equipo', 'usuario']
    
    def __str__(self):
        return f"{self.usuario.nombre_completo} - {self.equipo.nombre} ({self.get_rol_en_equipo_display()})"


class AsignacionAutomatica(models.Model):
    """Configuración para asignación automática de solicitudes"""
    
    CRITERIOS_ASIGNACION = [
        ('especialidad', 'Por Especialidad'),
        ('tipo_cancer', 'Por Tipo de Cáncer'),
        ('estadio', 'Por Estadio'),
        ('edad_paciente', 'Por Edad del Paciente'),
        ('prioridad', 'Por Prioridad'),
    ]
    
    equipo = models.ForeignKey(
        EquipoTrabajo,
        on_delete=models.CASCADE,
        related_name='reglas_asignacion'
    )
    
    criterio = models.CharField(
        max_length=20,
        choices=CRITERIOS_ASIGNACION,
        help_text='Criterio de asignación'
    )
    
    valor = models.CharField(
        max_length=200,
        help_text='Valor del criterio (ej: pulmón, mama, etc.)'
    )
    
    prioridad = models.IntegerField(
        default=1,
        help_text='Prioridad de la regla (1 = más alta)'
    )
    
    activo = models.BooleanField(
        default=True,
        help_text='Indica si la regla está activa'
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Regla de Asignación'
        verbose_name_plural = 'Reglas de Asignación'
        ordering = ['prioridad', 'fecha_creacion']
    
    def __str__(self):
        return f"{self.equipo.nombre} - {self.get_criterio_display()}: {self.valor}"


class CanalChat(models.Model):
    """Canal de comunicación para cada solicitud y equipo"""
    
    equipo = models.ForeignKey(
        EquipoTrabajo,
        on_delete=models.CASCADE,
        related_name='canales_chat'
    )
    
    nombre = models.CharField(
        max_length=200,
        help_text='Nombre del canal de chat'
    )
    
    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text='Descripción del canal de chat'
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Canal de Chat'
        verbose_name_plural = 'Canales de Chat'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f'Canal de Chat: {self.nombre}'


class MensajeChat(models.Model):
    """Mensajes dentro de un canal de chat"""
    
    canal = models.ForeignKey(
        CanalChat,
        on_delete=models.CASCADE,
        related_name='mensajes'
    )
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mensajes_enviados'
    )
    
    contenido = models.TextField(
        help_text='Contenido del mensaje'
    )
    
    fecha_envio = models.DateTimeField(auto_now_add=True)
    
    leido = models.BooleanField(
        default=False,
        help_text='Indica si el mensaje ha sido leído'
    )
    
    class Meta:
        verbose_name = 'Mensaje de Chat'
        verbose_name_plural = 'Mensajes de Chat'
        ordering = ['-fecha_envio']
    
    def __str__(self):
        return f'Mensaje de {self.usuario.username}: {self.contenido[:30]}...'
