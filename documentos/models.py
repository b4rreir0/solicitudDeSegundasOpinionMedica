from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from opiniones_medicas.models import SolicitudOpinion
import os


def upload_to_documents(instance, filename):
    """Función para definir la ruta de subida de documentos"""
    return f'documentos/{instance.solicitud.id}/{filename}'


class TipoDocumento(models.Model):
    """Modelo para los tipos de documentos médicos"""
    
    nombre = models.CharField(
        max_length=100,
        unique=True,
        help_text='Nombre del tipo de documento'
    )
    
    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text='Descripción del tipo de documento'
    )
    
    activo = models.BooleanField(
        default=True,
        help_text='Indica si el tipo de documento está activo'
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Tipo de Documento'
        verbose_name_plural = 'Tipos de Documento'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Documento(models.Model):
    """Modelo para los documentos médicos adjuntos a las solicitudes"""
    
    solicitud = models.ForeignKey(
        SolicitudOpinion,
        on_delete=models.CASCADE,
        related_name='documentos',
        help_text='Solicitud a la que pertenece el documento'
    )
    
    tipo_documento = models.ForeignKey(
        TipoDocumento,
        on_delete=models.CASCADE,
        help_text='Tipo de documento'
    )
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text='Usuario que subió el documento'
    )
    
    nombre = models.CharField(
        max_length=200,
        help_text='Nombre del documento'
    )
    
    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text='Descripción del documento'
    )
    
    archivo = models.FileField(
        upload_to=upload_to_documents,
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'txt']
        )],
        help_text='Archivo del documento'
    )
    
    tamaño = models.PositiveIntegerField(
        help_text='Tamaño del archivo en bytes'
    )
    
    fecha_subida = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        ordering = ['-fecha_subida']
    
    def __str__(self):
        return f"{self.nombre} - {self.solicitud.titulo}"
    
    def save(self, *args, **kwargs):
        if self.archivo:
            self.tamaño = self.archivo.size
        super().save(*args, **kwargs)
    
    @property
    def extension(self):
        return os.path.splitext(self.archivo.name)[1].lower()
    
    @property
    def tamaño_legible(self):
        """Retorna el tamaño del archivo en formato legible"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.tamaño < 1024.0:
                return f"{self.tamaño:.1f} {unit}"
            self.tamaño /= 1024.0
        return f"{self.tamaño:.1f} TB"


class HistorialDocumento(models.Model):
    """Modelo para el historial de modificaciones de documentos"""
    
    ACCIONES = [
        ('subido', 'Subido'),
        ('modificado', 'Modificado'),
        ('eliminado', 'Eliminado'),
        ('descargado', 'Descargado'),
    ]
    
    documento = models.ForeignKey(
        Documento,
        on_delete=models.CASCADE,
        related_name='historial',
        help_text='Documento al que pertenece el historial'
    )
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text='Usuario que realizó la acción'
    )
    
    accion = models.CharField(
        max_length=20,
        choices=ACCIONES,
        help_text='Acción realizada'
    )
    
    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text='Descripción de la acción'
    )
    
    fecha_accion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Historial de Documento'
        verbose_name_plural = 'Historial de Documentos'
        ordering = ['-fecha_accion']
    
    def __str__(self):
        return f"{self.documento.nombre} - {self.get_accion_display()} ({self.fecha_accion.strftime('%d/%m/%Y %H:%M')})"


class ArchivoTemporal(models.Model):
    """Modelo para archivos temporales durante el proceso de subida"""
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text='Usuario que subió el archivo temporal'
    )
    
    archivo = models.FileField(
        upload_to='temp/',
        help_text='Archivo temporal'
    )
    
    nombre_original = models.CharField(
        max_length=200,
        help_text='Nombre original del archivo'
    )
    
    fecha_subida = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Archivo Temporal'
        verbose_name_plural = 'Archivos Temporales'
        ordering = ['-fecha_subida']
    
    def __str__(self):
        return f"{self.nombre_original} - {self.usuario.username}"
