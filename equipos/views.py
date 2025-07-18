from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
import json

from .models import (
    EspecialidadOncologica, 
    EquipoTrabajo, 
    MiembroEquipo, 
    AsignacionAutomatica,
    CanalChat,
    MensajeChat
)
from usuarios.models import Usuario
from opiniones_medicas.models import SolicitudOpinion


@login_required
def lista_equipos(request):
    """Vista para listar todos los equipos de trabajo"""
    equipos = EquipoTrabajo.objects.filter(activo=True).select_related(
        'especialidad', 'coordinador'
    ).prefetch_related('miembros')
    
    # Filtros
    especialidad = request.GET.get('especialidad')
    if especialidad:
        equipos = equipos.filter(especialidad_id=especialidad)
    
    busqueda = request.GET.get('buscar')
    if busqueda:
        equipos = equipos.filter(
            Q(nombre__icontains=busqueda) |
            Q(descripcion__icontains=busqueda) |
            Q(especialidad__nombre__icontains=busqueda)
        )
    
    # Paginación
    paginator = Paginator(equipos, 12)
    page = request.GET.get('page')
    equipos_paginados = paginator.get_page(page)
    
    # Obtener especialidades para el filtro
    especialidades = EspecialidadOncologica.objects.filter(activo=True)
    
    context = {
        'equipos': equipos_paginados,
        'especialidades': especialidades,
        'filtros': {
            'especialidad': especialidad,
            'buscar': busqueda,
        }
    }
    
    return render(request, 'equipos/lista_equipos.html', context)


@login_required
def detalle_equipo(request, equipo_id):
    """Vista para mostrar los detalles de un equipo específico"""
    equipo = get_object_or_404(EquipoTrabajo, id=equipo_id, activo=True)
    
    # Verificar si el usuario es miembro del equipo
    es_miembro = equipo.miembros.filter(id=request.user.id).exists()
    
    if not es_miembro and request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para ver este equipo.')
        return redirect('lista_equipos')
    
    # Obtener miembros del equipo
    miembros = MiembroEquipo.objects.filter(
        equipo=equipo, 
        activo=True
    ).select_related('usuario')
    
    # Obtener solicitudes asignadas al equipo
    solicitudes = equipo.solicitudes_asignadas.filter(
        estado__in=['asignada', 'en_revision']
    ).select_related('paciente')[:10]
    
    # Obtener estadísticas del equipo
    total_solicitudes = equipo.solicitudes_asignadas.count()
    solicitudes_completadas = equipo.solicitudes_asignadas.filter(
        estado='completada'
    ).count()
    solicitudes_pendientes = equipo.solicitudes_asignadas.filter(
        estado__in=['asignada', 'en_revision']
    ).count()
    
    context = {
        'equipo': equipo,
        'miembros': miembros,
        'solicitudes': solicitudes,
        'es_miembro': es_miembro,
        'estadisticas': {
            'total_solicitudes': total_solicitudes,
            'solicitudes_completadas': solicitudes_completadas,
            'solicitudes_pendientes': solicitudes_pendientes,
        }
    }
    
    return render(request, 'equipos/detalle_equipo.html', context)


@login_required
def mis_equipos(request):
    """Vista para mostrar los equipos del usuario actual"""
    if request.user.rol not in ['medico', 'admin']:
        messages.error(request, 'Solo los médicos pueden ver equipos.')
        return redirect('dashboard')
    
    # Equipos donde el usuario es miembro
    equipos_miembro = request.user.equipos_miembro.filter(activo=True)
    
    # Equipos donde el usuario es coordinador
    equipos_coordinador = request.user.equipos_coordinados.filter(activo=True)
    
    context = {
        'equipos_miembro': equipos_miembro,
        'equipos_coordinador': equipos_coordinador,
    }
    
    return render(request, 'equipos/mis_equipos.html', context)


@login_required
def chat_equipo(request, equipo_id):
    """Vista para el chat del equipo"""
    equipo = get_object_or_404(EquipoTrabajo, id=equipo_id, activo=True)
    
    # Verificar si el usuario es miembro del equipo
    es_miembro = equipo.miembros.filter(id=request.user.id).exists()
    
    if not es_miembro and request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para acceder al chat de este equipo.')
        return redirect('lista_equipos')
    
    # Obtener o crear el canal de chat general del equipo
    canal, created = CanalChat.objects.get_or_create(
        equipo=equipo,
        nombre=f"Chat General - {equipo.nombre}",
        defaults={
            'descripcion': f'Canal de comunicación general del equipo {equipo.nombre}'
        }
    )
    
    # Obtener mensajes del canal
    mensajes = canal.mensajes.select_related('usuario').order_by('fecha_envio')
    
    # Marcar mensajes como leídos
    canal.mensajes.filter(leído=False).exclude(usuario=request.user).update(leído=True)
    
    context = {
        'equipo': equipo,
        'canal': canal,
        'mensajes': mensajes,
        'es_miembro': es_miembro,
    }
    
    return render(request, 'equipos/chat_equipo.html', context)


@login_required
@require_http_methods(["POST"])
def enviar_mensaje(request, equipo_id):
    """Vista AJAX para enviar mensajes al chat del equipo"""
    equipo = get_object_or_404(EquipoTrabajo, id=equipo_id, activo=True)
    
    # Verificar si el usuario es miembro del equipo
    es_miembro = equipo.miembros.filter(id=request.user.id).exists()
    
    if not es_miembro and request.user.rol != 'admin':
        return JsonResponse({'error': 'No tienes permisos para enviar mensajes.'}, status=403)
    
    try:
        data = json.loads(request.body)
        contenido = data.get('contenido', '').strip()
        
        if not contenido:
            return JsonResponse({'error': 'El mensaje no puede estar vacío.'}, status=400)
        
        # Obtener el canal de chat
        canal = CanalChat.objects.get(equipo=equipo, nombre=f"Chat General - {equipo.nombre}")
        
        # Crear el mensaje
        mensaje = MensajeChat.objects.create(
            canal=canal,
            usuario=request.user,
            contenido=contenido
        )
        
        return JsonResponse({
            'success': True,
            'mensaje': {
                'id': mensaje.id,
                'usuario': mensaje.usuario.nombre_completo or mensaje.usuario.username,
                'contenido': mensaje.contenido,
                'fecha_envio': mensaje.fecha_envio.strftime('%H:%M'),
                'es_propio': mensaje.usuario == request.user
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Error al enviar el mensaje: {str(e)}'}, status=500)


@login_required
def obtener_mensajes(request, equipo_id):
    """Vista AJAX para obtener mensajes del chat"""
    equipo = get_object_or_404(EquipoTrabajo, id=equipo_id, activo=True)
    
    # Verificar si el usuario es miembro del equipo
    es_miembro = equipo.miembros.filter(id=request.user.id).exists()
    
    if not es_miembro and request.user.rol != 'admin':
        return JsonResponse({'error': 'No tienes permisos.'}, status=403)
    
    try:
        canal = CanalChat.objects.get(equipo=equipo, nombre=f"Chat General - {equipo.nombre}")
        
        # Obtener mensajes desde una fecha específica
        desde = request.GET.get('desde')
        mensajes = canal.mensajes.select_related('usuario').order_by('fecha_envio')
        
        if desde:
            mensajes = mensajes.filter(fecha_envio__gt=desde)
        
        mensajes_data = []
        for mensaje in mensajes:
            mensajes_data.append({
                'id': mensaje.id,
                'usuario': mensaje.usuario.nombre_completo or mensaje.usuario.username,
                'contenido': mensaje.contenido,
                'fecha_envio': mensaje.fecha_envio.strftime('%H:%M'),
                'es_propio': mensaje.usuario == request.user
            })
        
        return JsonResponse({'mensajes': mensajes_data})
        
    except Exception as e:
        return JsonResponse({'error': f'Error al obtener mensajes: {str(e)}'}, status=500)


@login_required
def asignar_solicitud_automatica(request, solicitud_id):
    """Vista para asignar automáticamente una solicitud a un equipo"""
    if request.user.rol != 'admin':
        messages.error(request, 'Solo los administradores pueden asignar solicitudes.')
        return redirect('dashboard')
    
    solicitud = get_object_or_404(SolicitudOpinion, id=solicitud_id)
    
    # Buscar el equipo más adecuado basado en las reglas de asignación
    equipo_asignado = None
    
    # Reglas de asignación por tipo de cáncer
    if solicitud.tipo_cancer:
        reglas = AsignacionAutomatica.objects.filter(
            criterio='tipo_cancer',
            valor__icontains=solicitud.tipo_cancer,
            activo=True
        ).order_by('prioridad')
        
        if reglas.exists():
            equipo_asignado = reglas.first().equipo
    
    # Si no se encontró por tipo de cáncer, buscar por especialidad
    if not equipo_asignado:
        reglas = AsignacionAutomatica.objects.filter(
            criterio='especialidad',
            valor__icontains=solicitud.especialidad_requerida,
            activo=True
        ).order_by('prioridad')
        
        if reglas.exists():
            equipo_asignado = reglas.first().equipo
    
    # Asignar el equipo a la solicitud
    if equipo_asignado:
        solicitud.equipo_asignado = equipo_asignado
        solicitud.estado = 'asignada'
        solicitud.fecha_asignacion = timezone.now()
        solicitud.save()
        
        # Crear canal de chat para la solicitud
        canal_solicitud, created = CanalChat.objects.get_or_create(
            equipo=equipo_asignado,
            nombre=f"Solicitud #{solicitud.id} - {solicitud.titulo}",
            defaults={
                'descripcion': f'Chat para la solicitud de {solicitud.paciente.nombre_completo}'
            }
        )
        
        messages.success(request, f'Solicitud asignada exitosamente al equipo {equipo_asignado.nombre}')
    else:
        messages.warning(request, 'No se encontró un equipo adecuado para esta solicitud.')
    
    return redirect('detalle_solicitud', solicitud_id=solicitud.id)


@login_required
def crear_equipo(request):
    """Vista para crear un nuevo equipo de trabajo"""
    if request.user.rol != 'admin':
        messages.error(request, 'Solo los administradores pueden crear equipos.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            especialidad_id = request.POST.get('especialidad')
            descripcion = request.POST.get('descripcion')
            coordinador_id = request.POST.get('coordinador')
            
            especialidad = get_object_or_404(EspecialidadOncologica, id=especialidad_id)
            coordinador = get_object_or_404(Usuario, id=coordinador_id, rol='medico')
            
            equipo = EquipoTrabajo.objects.create(
                nombre=nombre,
                especialidad=especialidad,
                descripcion=descripcion,
                coordinador=coordinador
            )
            
            # Agregar el coordinador como miembro
            MiembroEquipo.objects.create(
                equipo=equipo,
                usuario=coordinador,
                rol_en_equipo='coordinador'
            )
            
            messages.success(request, 'Equipo creado exitosamente.')
            return redirect('detalle_equipo', equipo_id=equipo.id)
            
        except Exception as e:
            messages.error(request, f'Error al crear el equipo: {str(e)}')
    
    # Obtener datos para el formulario
    especialidades = EspecialidadOncologica.objects.filter(activo=True)
    medicos = Usuario.objects.filter(rol='medico', is_active=True)
    
    context = {
        'especialidades': especialidades,
        'medicos': medicos,
    }
    
    return render(request, 'equipos/crear_equipo.html', context)
