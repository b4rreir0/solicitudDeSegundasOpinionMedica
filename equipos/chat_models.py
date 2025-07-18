from django.db import models
from django.conf import settings
from equipos.models import EquipoTrabajo


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
    
    leído = models.BooleanField(
        default=False,
        help_text='Indica si el mensaje ha sido leído'
    )
    
    class Meta:
        verbose_name = 'Mensaje de Chat'
        verbose_name_plural = 'Mensajes de Chat'
        ordering = ['-fecha_envio']
    
    def __str__(self):
        return f'Mensaje de {self.usuario.username}: {self.contenido[:30]}...'

