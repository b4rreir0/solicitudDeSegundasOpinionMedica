from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class Usuario(AbstractUser):
    """Modelo personalizado de usuario para el sistema de solicitudes médicas"""
    
    ROLES = [
        ('paciente', 'Paciente'),
        ('medico', 'Médico'),
        ('admin', 'Administrador'),
    ]
    
    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default='paciente',
        help_text='Rol del usuario en el sistema'
    )
    
    telefono = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message='El número de teléfono debe tener entre 9 y 15 dígitos'
        )],
        help_text='Número de teléfono del usuario'
    )
    
    fecha_nacimiento = models.DateField(
        blank=True,
        null=True,
        help_text='Fecha de nacimiento del usuario'
    )
    
    direccion = models.TextField(
        blank=True,
        null=True,
        help_text='Dirección del usuario'
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"
    
    @property
    def nombre_completo(self):
        return f"{self.first_name} {self.last_name}".strip()


class PerfilMedico(models.Model):
    """Perfil adicional para usuarios médicos"""
    
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='perfil_medico'
    )
    
    numero_colegiado = models.CharField(
        max_length=50,
        unique=True,
        help_text='Número de colegiado médico'
    )
    
    especialidad = models.CharField(
        max_length=100,
        help_text='Especialidad médica'
    )
    
    hospital_clinica = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text='Hospital o clínica donde trabaja'
    )
    
    años_experiencia = models.PositiveIntegerField(
        help_text='Años de experiencia profesional'
    )
    
    activo = models.BooleanField(
        default=True,
        help_text='Indica si el médico está activo para recibir consultas'
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil Médico'
        verbose_name_plural = 'Perfiles Médicos'
    
    def __str__(self):
        return f"Dr. {self.usuario.nombre_completo} - {self.especialidad}"
