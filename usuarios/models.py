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
    
    # Asegurar que el email sea único
    email = models.EmailField(
        unique=True,
        help_text='Correo electrónico único del usuario'
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
    
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    
    sexo = models.CharField(
        max_length=1,
        choices=SEXO_CHOICES,
        blank=True,
        null=True,
        help_text='Sexo del paciente'
    )
    
    peso = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Peso del paciente en kg'
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        constraints = [
            models.UniqueConstraint(
                fields=['username'],
                name='unique_username'
            ),
            models.UniqueConstraint(
                fields=['email'],
                name='unique_email'
            )
        ]
    
    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"
    
    @property
    def nombre_completo(self):
        return f"{self.first_name} {self.last_name}".strip()
        
    def clean(self):
        """Validación personalizada del modelo"""
        from django.core.exceptions import ValidationError
        
        # Validar que el username no esté vacío
        if not self.username:
            raise ValidationError('El nombre de usuario es obligatorio')
        
        # Validar que el email no esté vacío
        if not self.email:
            raise ValidationError('El correo electrónico es obligatorio')
        
        # Validar unicidad del username (case-insensitive)
        existing_user = Usuario.objects.filter(
            username__iexact=self.username
        ).exclude(pk=self.pk)
        if existing_user.exists():
            raise ValidationError('Ya existe un usuario con este nombre de usuario')
        
        # Validar unicidad del email (case-insensitive)
        existing_email = Usuario.objects.filter(
            email__iexact=self.email
        ).exclude(pk=self.pk)
        if existing_email.exists():
            raise ValidationError('Ya existe un usuario con este correo electrónico')
    
    def save(self, *args, **kwargs):
        """Guardar con validación completa"""
        # Normalizar email y username
        if self.email:
            self.email = self.email.lower().strip()
        if self.username:
            self.username = self.username.lower().strip()
        
        # Ejecutar validación
        self.full_clean()
        
        super().save(*args, **kwargs)


class CodigoVerificacion(models.Model):
    """Modelo para códigos de verificación de email"""
    
    TIPO_CHOICES = [
        ('registro', 'Registro de Usuario'),
        ('recuperacion', 'Recuperación de Contraseña'),
        ('cambio_email', 'Cambio de Email'),
    ]
    
    email = models.EmailField(
        help_text='Email al que se envió el código'
    )
    
    codigo = models.CharField(
        max_length=6,
        help_text='Código de verificación de 6 dígitos'
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='registro',
        help_text='Tipo de verificación'
    )
    
    datos_temporales = models.JSONField(
        blank=True,
        null=True,
        help_text='Datos temporales del usuario para el registro'
    )
    
    usado = models.BooleanField(
        default=False,
        help_text='Indica si el código ya fue usado'
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(
        help_text='Fecha de expiración del código'
    )
    
    class Meta:
        verbose_name = 'Código de Verificación'
        verbose_name_plural = 'Códigos de Verificación'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.email} - {self.codigo} ({self.get_tipo_display()})"
    
    def is_expired(self):
        """Verifica si el código ha expirado"""
        from django.utils import timezone
        return timezone.now() > self.fecha_expiracion
    
    def is_valid(self):
        """Verifica si el código es válido (no usado y no expirado)"""
        return not self.usado and not self.is_expired()


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
