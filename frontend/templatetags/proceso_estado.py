from django import template
from django.utils import timezone
from datetime import datetime

register = template.Library()

@register.inclusion_tag('frontend/components/proceso_estado.html')
def mostrar_proceso_estado(solicitud):
    """
    Template tag para mostrar el estado del proceso de una solicitud
    """
    
    # Definir los pasos del proceso
    pasos = [
        {
            'id': 'pendiente',
            'titulo': 'Solicitud Creada',
            'descripcion': 'Solicitud enviada y pendiente de asignación',
            'icono': '📝',
            'fecha': solicitud.fecha_creacion,
            'activo': True
        },
        {
            'id': 'asignada',
            'titulo': 'Médico Asignado',
            'descripcion': 'Especialista asignado para revisar el caso',
            'icono': '👨‍⚕️',
            'fecha': solicitud.fecha_asignacion,
            'activo': solicitud.estado in ['asignada', 'en_revision', 'completada']
        },
        {
            'id': 'en_revision',
            'titulo': 'En Revisión',
            'descripcion': 'Médico revisando documentos y caso',
            'icono': '🔍',
            'fecha': None,  # Se puede agregar campo fecha_revision al modelo
            'activo': solicitud.estado in ['en_revision', 'completada']
        },
        {
            'id': 'completada',
            'titulo': 'Opinión Emitida',
            'descripcion': 'Segunda opinión médica completada',
            'icono': '✅',
            'fecha': solicitud.fecha_completada,
            'activo': solicitud.estado == 'completada'
        }
    ]
    
    # Calcular porcentaje de progreso
    estados_orden = ['pendiente', 'asignada', 'en_revision', 'completada']
    try:
        estado_actual_index = estados_orden.index(solicitud.estado)
        porcentaje_progreso = ((estado_actual_index + 1) / len(estados_orden)) * 100
    except ValueError:
        porcentaje_progreso = 0
    
    # Si está cancelada, mostrar estado especial
    if solicitud.estado == 'cancelada':
        porcentaje_progreso = 0
        for paso in pasos:
            if paso['id'] != 'pendiente':
                paso['activo'] = False
    
    # Información adicional
    tiempo_transcurrido = timezone.now() - solicitud.fecha_creacion
    dias_transcurridos = tiempo_transcurrido.days
    
    # Prioridad con clase CSS
    prioridad_clase = f"prioridad-{solicitud.prioridad}"
    
    context = {
        'solicitud': solicitud,
        'pasos': pasos,
        'porcentaje_progreso': porcentaje_progreso,
        'dias_transcurridos': dias_transcurridos,
        'prioridad_clase': prioridad_clase,
        'estado_actual': solicitud.estado,
    }
    
    return context


@register.filter
def estado_color(estado):
    """
    Filtro para obtener el color correspondiente a un estado
    """
    colores = {
        'pendiente': '#FFC107',
        'asignada': '#BBDEFB',
        'en_revision': '#2A628F',
        'completada': '#4CAF50',
        'cancelada': '#F44336',
    }
    return colores.get(estado, '#E0E0E0')


@register.filter
def prioridad_icono(prioridad):
    """
    Filtro para obtener el icono correspondiente a una prioridad
    """
    iconos = {
        'baja': '🟢',
        'media': '🟡',
        'alta': '🟠',
        'urgente': '🔴',
    }
    return iconos.get(prioridad, '⚪')


@register.filter
def tiempo_estimado(estado):
    """
    Filtro para obtener el tiempo estimado según el estado
    """
    tiempos = {
        'pendiente': '1-2 días',
        'asignada': '2-3 días',
        'en_revision': '3-5 días',
        'completada': 'Finalizado',
        'cancelada': 'Cancelado',
    }
    return tiempos.get(estado, 'No disponible')


@register.simple_tag
def progreso_porcentaje(estado):
    """
    Tag para calcular el porcentaje de progreso
    """
    estados_orden = ['pendiente', 'asignada', 'en_revision', 'completada']
    try:
        estado_index = estados_orden.index(estado)
        return ((estado_index + 1) / len(estados_orden)) * 100
    except ValueError:
        return 0
