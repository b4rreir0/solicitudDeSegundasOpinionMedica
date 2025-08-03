from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator

from .models import Usuario
from opiniones_medicas.models import SolicitudOpinion
from equipos.models import EquipoTrabajo, CanalChat, MensajeChat


@login_required
def panel_medico(request):
    """Panel principal para médicos con menú lateral"""
    if request.user.rol != 'medico':
        messages.error(request, 'Solo los médicos pueden acceder a este panel.')
        return redirect('dashboard')
    
    # Obtener equipos del médico
    equipos = request.user.equipos_miembro.filter(activo=True)
    
    # Obtener chats activos
    chats_activos = CanalChat.objects.filter(
        equipo__in=equipos
    ).order_by('-fecha_creacion')[:10]
    
    context = {
        'equipos': equipos,
        'chats_activos': chats_activos,
    }
    
    return render(request, 'usuarios/panel_medico.html', context)


@login_required
def solicitudes_asignadas_medico(request):
    """Vista para mostrar solicitudes asignadas al médico"""
    if request.user.rol != 'medico':
        messages.error(request, 'Solo los médicos pueden acceder a esta vista.')
        return redirect('dashboard')
    
    # Obtener equipos del médico
    equipos = request.user.equipos_miembro.filter(activo=True)
    
    # Obtener solicitudes asignadas
    solicitudes = SolicitudOpinion.objects.filter(
        equipo_asignado__in=equipos,
        estado__in=['asignada', 'en_revision']
    ).select_related(
        'paciente', 'equipo_asignado'
    ).order_by('-fecha_asignacion')
    
    # Filtros
    estado_filtro = request.GET.get('estado')
    if estado_filtro:
        solicitudes = solicitudes.filter(estado=estado_filtro)
    
    equipo_filtro = request.GET.get('equipo')
    if equipo_filtro:
        solicitudes = solicitudes.filter(equipo_asignado_id=equipo_filtro)
    
    # Paginación
    paginator = Paginator(solicitudes, 10)
    page = request.GET.get('page')
    solicitudes_paginadas = paginator.get_page(page)
    
    context = {
        'solicitudes': solicitudes_paginadas,
        'equipos': equipos,
        'estado_filtro': estado_filtro,
        'equipo_filtro': equipo_filtro,
    }
    
    return render(request, 'usuarios/solicitudes_asignadas_medico.html', context)


@login_required
def solicitudes_revision_medico(request):
    """Vista para solicitudes que necesitan revisión por el jefe del grupo"""
    if request.user.rol != 'medico':
        messages.error(request, 'Solo los médicos pueden acceder a esta vista.')
        return redirect('dashboard')
    
    # Obtener equipos del médico
    equipos = request.user.equipos_miembro.filter(activo=True)
    
    # Obtener solicitudes que necesitan revisión
    solicitudes = SolicitudOpinion.objects.filter(
        equipo_asignado__in=equipos,
        estado='revision_pendiente'
    ).select_related(
        'paciente', 'equipo_asignado'
    ).order_by('-fecha_actualizacion')
    
    # Filtros
    equipo_filtro = request.GET.get('equipo')
    if equipo_filtro:
        solicitudes = solicitudes.filter(equipo_asignado_id=equipo_filtro)
    
    # Paginación
    paginator = Paginator(solicitudes, 10)
    page = request.GET.get('page')
    solicitudes_paginadas = paginator.get_page(page)
    
    context = {
        'solicitudes': solicitudes_paginadas,
        'equipos': equipos,
        'equipo_filtro': equipo_filtro,
    }
    
    return render(request, 'usuarios/solicitudes_revision_medico.html', context)


@login_required
def chats_medico(request):
    """Vista para mostrar todos los chats del médico"""
    if request.user.rol != 'medico':
        messages.error(request, 'Solo los médicos pueden acceder a esta vista.')
        return redirect('dashboard')
    
    # Obtener equipos del médico
    equipos = request.user.equipos_miembro.filter(activo=True)
    
    # Obtener chats de los equipos
    chats = CanalChat.objects.filter(
        equipo__in=equipos
    ).annotate(
        mensajes_no_leidos=Count('mensajes', filter=Q(mensajes__leido=False)),
        ultimo_mensaje=Q(mensajes__fecha_envio__isnull=False)
    ).select_related('equipo').order_by('-fecha_creacion')
    
    # Filtros
    equipo_filtro = request.GET.get('equipo')
    if equipo_filtro:
        chats = chats.filter(equipo_id=equipo_filtro)
    
    # Paginación
    paginator = Paginator(chats, 15)
    page = request.GET.get('page')
    chats_paginados = paginator.get_page(page)
    
    context = {
        'chats': chats_paginados,
        'equipos': equipos,
        'equipo_filtro': equipo_filtro,
    }
    
    return render(request, 'usuarios/chats_medico.html', context)


@login_required
def emitir_criterio(request, solicitud_id):
    """Vista para emitir criterio médico sobre una solicitud"""
    if request.user.rol != 'medico':
        messages.error(request, 'Solo los médicos pueden emitir criterios.')
        return redirect('dashboard')
    
    solicitud = get_object_or_404(SolicitudOpinion, id=solicitud_id)
    
    # Verificar que el médico pertenece al equipo asignado
    if not solicitud.equipo_asignado or not solicitud.equipo_asignado.miembros.filter(id=request.user.id).exists():
        messages.error(request, 'No tienes permisos para emitir criterio sobre esta solicitud.')
        return redirect('panel_medico')
    
    if request.method == 'POST':
        criterio = request.POST.get('criterio')
        observaciones = request.POST.get('observaciones', '')
        
        if criterio:
            # Crear la opinión médica
            from opiniones_medicas.models import OpinionMedica
            opinion, created = OpinionMedica.objects.get_or_create(
                solicitud=solicitud,
                defaults={
                    'medico': request.user,
                    'diagnostico_propuesto': criterio,
                    'recomendaciones': observaciones or 'Sin observaciones adicionales',
                }
            )
            
            if not created:
                # Actualizar opinión existente
                opinion.diagnostico_propuesto = criterio
                opinion.recomendaciones = observaciones or 'Sin observaciones adicionales'
                opinion.save()
            
            solicitud.medico_asignado = request.user
            solicitud.estado = 'revision_pendiente'
            solicitud.fecha_actualizacion = timezone.now()
            solicitud.save()
            
            messages.success(request, 'Criterio emitido exitosamente. Pendiente de aprobación por el coordinador.')
            return redirect('solicitudes_asignadas_medico')
    
    context = {
        'solicitud': solicitud,
    }
    
    return render(request, 'usuarios/emitir_criterio.html', context)


@login_required
def aprobar_solicitud(request, solicitud_id):
    """Vista para que el líder apruebe una solicitud"""
    if request.user.rol != 'medico':
        messages.error(request, 'Solo los médicos pueden aprobar solicitudes.')
        return redirect('dashboard')
    
    solicitud = get_object_or_404(SolicitudOpinion, id=solicitud_id)
    
    # Verificar que el usuario es coordinador del equipo asignado
    if not solicitud.equipo_asignado or solicitud.equipo_asignado.coordinador != request.user:
        messages.error(request, 'Solo el coordinador del equipo puede aprobar solicitudes.')
        return redirect('panel_medico')
    
    if solicitud.estado != 'revision_pendiente':
        messages.error(request, 'Esta solicitud no está pendiente de aprobación.')
        return redirect('panel_medico')
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        comentarios = request.POST.get('comentarios', '')
        
        if accion == 'aprobar':
            solicitud.estado = 'aprobada'
            messages.success(request, 'Solicitud aprobada exitosamente. El paciente puede ver la respuesta.')
        elif accion == 'rechazar':
            solicitud.estado = 'en_revision'
            messages.warning(request, 'Solicitud enviada de vuelta para revisión.')
        
        solicitud.fecha_actualizacion = timezone.now()
        solicitud.save()
        
        return redirect('solicitudes_revision_medico')
    
    context = {
        'solicitud': solicitud,
    }
    
    return render(request, 'usuarios/aprobar_solicitud.html', context)
