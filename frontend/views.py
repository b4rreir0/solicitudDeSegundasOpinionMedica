from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timedelta

from usuarios.models import Usuario, PerfilMedico
from usuarios.services import UsuarioRegistrationService
from opiniones_medicas.models import SolicitudOpinion, OpinionMedica, Calificacion, Seguimiento
from documentos.models import Documento, TipoDocumento


def home(request):
    """Vista principal del sistema"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    context = {
        'total_solicitudes': SolicitudOpinion.objects.count(),
        'total_medicos': Usuario.objects.filter(rol='medico').count(),
        'total_opiniones': OpinionMedica.objects.count(),
        'calificacion_promedio': Calificacion.objects.aggregate(
            promedio=Avg('puntuacion')
        ).get('promedio', 0) or 0,
    }
    return render(request, 'frontend/home.html', context)


@login_required
def dashboard(request):
    """Dashboard principal según el rol del usuario"""
    user = request.user
    context = {'user': user}
    
    if user.rol == 'paciente':
        # Estadísticas del paciente
        solicitudes = SolicitudOpinion.objects.filter(paciente=user)
        context.update({
            'total_solicitudes': solicitudes.count(),
            'solicitudes_pendientes': solicitudes.filter(estado='pendiente').count(),
            'solicitudes_completadas': solicitudes.filter(estado='completada').count(),
            'solicitudes_recientes': solicitudes.order_by('-fecha_creacion')[:5],
            'documentos_subidos': Documento.objects.filter(usuario=user).count(),
        })
        
    elif user.rol == 'medico':
        # Estadísticas del médico
        solicitudes_asignadas = SolicitudOpinion.objects.filter(medico_asignado=user)
        opiniones_emitidas = OpinionMedica.objects.filter(medico=user)
        
        context.update({
            'solicitudes_asignadas': solicitudes_asignadas.count(),
            'solicitudes_pendientes': solicitudes_asignadas.filter(estado__in=['asignada', 'en_revision']).count(),
            'opiniones_emitidas': opiniones_emitidas.count(),
            'calificacion_promedio': Calificacion.objects.filter(
                opinion__medico=user
            ).aggregate(promedio=Avg('puntuacion')).get('promedio', 0) or 0,
            'solicitudes_recientes': solicitudes_asignadas.order_by('-fecha_asignacion')[:5],
            'seguimientos_pendientes': Seguimiento.objects.filter(
                medico=user, 
                opinion__requiere_seguimiento=True
            ).count(),
        })
        
    elif user.rol == 'admin':
        # Estadísticas del administrador
        hoy = timezone.now().date()
        hace_30_dias = hoy - timedelta(days=30)
        
        context.update({
            'total_usuarios': Usuario.objects.count(),
            'total_medicos': Usuario.objects.filter(rol='medico').count(),
            'total_pacientes': Usuario.objects.filter(rol='paciente').count(),
            'total_solicitudes': SolicitudOpinion.objects.count(),
            'solicitudes_mes': SolicitudOpinion.objects.filter(
                fecha_creacion__date__gte=hace_30_dias
            ).count(),
            'solicitudes_pendientes': SolicitudOpinion.objects.filter(estado='pendiente').count(),
            'medicos_activos': Usuario.objects.filter(
                rol='medico',
                perfil_medico__activo=True
            ).count(),
            'solicitudes_por_estado': SolicitudOpinion.objects.values('estado').annotate(
                count=Count('id')
            ).order_by('-count'),
        })
    
    return render(request, 'frontend/dashboard.html', context)


@login_required
def nueva_solicitud(request):
    """Vista para crear una nueva solicitud de opinión médica"""
    if request.user.rol != 'paciente':
        messages.error(request, 'Solo los pacientes pueden crear solicitudes.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            # Crear la solicitud
            solicitud = SolicitudOpinion.objects.create(
                paciente=request.user,
                titulo=request.POST.get('titulo'),
                descripcion_caso=request.POST.get('descripcion_caso'),
                diagnostico_inicial=request.POST.get('diagnostico_inicial'),
                tratamiento_actual=request.POST.get('tratamiento_actual'),
                especialidad_requerida=request.POST.get('especialidad_requerida'),
                prioridad=request.POST.get('prioridad', 'media'),
            )
            
            # Procesar archivos subidos
            archivos = request.FILES.getlist('documentos')
            for archivo in archivos:
                tipo_documento = TipoDocumento.objects.get_or_create(
                    nombre='Documento médico',
                    defaults={'descripcion': 'Documento médico general'}
                )[0]
                
                Documento.objects.create(
                    solicitud=solicitud,
                    tipo_documento=tipo_documento,
                    usuario=request.user,
                    nombre=archivo.name,
                    archivo=archivo,
                    tamaño=archivo.size,
                )
            
            messages.success(request, 'Solicitud creada exitosamente.')
            return redirect('detalle_solicitud', solicitud_id=solicitud.id)
            
        except Exception as e:
            messages.error(request, f'Error al crear la solicitud: {str(e)}')
    
    # Obtener especialidades disponibles
    especialidades = SolicitudOpinion.objects.values_list(
        'especialidad_requerida', flat=True
    ).distinct()
    
    tipos_documento = TipoDocumento.objects.filter(activo=True)
    
    context = {
        'especialidades': especialidades,
        'tipos_documento': tipos_documento,
        'prioridades': SolicitudOpinion.PRIORIDAD_CHOICES,
    }
    
    return render(request, 'frontend/nueva_solicitud.html', context)


@login_required
def lista_solicitudes(request):
    """Vista para listar solicitudes según el rol del usuario"""
    user = request.user
    
    # Filtros base según el rol
    if user.rol == 'paciente':
        solicitudes = SolicitudOpinion.objects.filter(paciente=user)
    elif user.rol == 'medico':
        solicitudes = SolicitudOpinion.objects.filter(medico_asignado=user)
    else:  # admin
        solicitudes = SolicitudOpinion.objects.all()
    
    # Aplicar filtros adicionales
    estado = request.GET.get('estado')
    if estado:
        solicitudes = solicitudes.filter(estado=estado)
    
    especialidad = request.GET.get('especialidad')
    if especialidad:
        solicitudes = solicitudes.filter(especialidad_requerida=especialidad)
    
    prioridad = request.GET.get('prioridad')
    if prioridad:
        solicitudes = solicitudes.filter(prioridad=prioridad)
    
    # Búsqueda por texto
    busqueda = request.GET.get('buscar')
    if busqueda:
        solicitudes = solicitudes.filter(
            Q(titulo__icontains=busqueda) |
            Q(descripcion_caso__icontains=busqueda) |
            Q(especialidad_requerida__icontains=busqueda)
        )
    
    # Ordenamiento
    orden = request.GET.get('orden', '-fecha_creacion')
    solicitudes = solicitudes.order_by(orden)
    
    # Paginación
    paginator = Paginator(solicitudes, 10)
    page = request.GET.get('page')
    solicitudes_paginadas = paginator.get_page(page)
    
    # Obtener opciones para filtros
    estados = SolicitudOpinion.ESTADO_CHOICES
    especialidades = SolicitudOpinion.objects.values_list(
        'especialidad_requerida', flat=True
    ).distinct()
    prioridades = SolicitudOpinion.PRIORIDAD_CHOICES
    
    context = {
        'solicitudes': solicitudes_paginadas,
        'estados': estados,
        'especialidades': especialidades,
        'prioridades': prioridades,
        'filtros_aplicados': {
            'estado': estado,
            'especialidad': especialidad,
            'prioridad': prioridad,
            'buscar': busqueda,
            'orden': orden,
        }
    }
    
    return render(request, 'frontend/lista_solicitudes.html', context)


@login_required
def detalle_solicitud(request, solicitud_id):
    """Vista para mostrar los detalles de una solicitud específica"""
    solicitud = get_object_or_404(SolicitudOpinion, id=solicitud_id)
    
    # Verificar permisos
    if request.user.rol == 'paciente' and solicitud.paciente != request.user:
        messages.error(request, 'No tienes permisos para ver esta solicitud.')
        return redirect('lista_solicitudes')
    
    if request.user.rol == 'medico' and solicitud.medico_asignado != request.user:
        messages.error(request, 'No tienes permisos para ver esta solicitud.')
        return redirect('lista_solicitudes')
    
    # Obtener datos relacionados
    documentos = solicitud.documentos.all()
    opinion = getattr(solicitud, 'opinion_medica', None)
    calificacion = getattr(opinion, 'calificacion', None) if opinion else None
    seguimientos = opinion.seguimientos.all() if opinion else []
    
    context = {
        'solicitud': solicitud,
        'documentos': documentos,
        'opinion': opinion,
        'calificacion': calificacion,
        'seguimientos': seguimientos,
    }
    
    return render(request, 'frontend/detalle_solicitud.html', context)


@login_required
def perfil_usuario(request):
    """Vista para mostrar y editar el perfil del usuario"""
    user = request.user
    
    if request.method == 'POST':
        try:
            # Actualizar datos básicos
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.telefono = request.POST.get('telefono', '')
            user.direccion = request.POST.get('direccion', '')
            
            fecha_nacimiento = request.POST.get('fecha_nacimiento')
            if fecha_nacimiento:
                user.fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
            
            user.save()
            
            # Si es médico, actualizar perfil médico
            if user.rol == 'medico':
                perfil_medico, created = PerfilMedico.objects.get_or_create(usuario=user)
                perfil_medico.especialidad = request.POST.get('especialidad', '')
                perfil_medico.hospital_clinica = request.POST.get('hospital_clinica', '')
                perfil_medico.años_experiencia = int(request.POST.get('años_experiencia', 0))
                perfil_medico.save()
            
            messages.success(request, 'Perfil actualizado exitosamente.')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar el perfil: {str(e)}')
    
    perfil_medico = getattr(user, 'perfil_medico', None)
    
    # Calcular estadísticas según el rol
    if user.rol == 'paciente':
        solicitudes_completadas = user.solicitudes_paciente.filter(estado='completada').count()
        solicitudes_pendientes = user.solicitudes_paciente.filter(estado='pendiente').count()
        total_solicitudes = user.solicitudes_paciente.count()
        
        context = {
            'user': user,
            'perfil_medico': perfil_medico,
            'solicitudes_completadas': solicitudes_completadas,
            'solicitudes_pendientes': solicitudes_pendientes,
            'total_solicitudes': total_solicitudes,
        }
    elif user.rol == 'medico':
        solicitudes_asignadas = user.solicitudes_medico.count()
        opiniones_emitidas = user.opiniones_emitidas.count()
        
        context = {
            'user': user,
            'perfil_medico': perfil_medico,
            'solicitudes_asignadas': solicitudes_asignadas,
            'opiniones_emitidas': opiniones_emitidas,
        }
    else:
        context = {
            'user': user,
            'perfil_medico': perfil_medico,
        }
    
    return render(request, 'frontend/perfil.html', context)


@login_required
def emitir_opinion(request, solicitud_id):
    """Vista para que los médicos emitan opiniones"""
    if request.user.rol != 'medico':
        messages.error(request, 'Solo los médicos pueden emitir opiniones.')
        return redirect('dashboard')
    
    solicitud = get_object_or_404(SolicitudOpinion, id=solicitud_id)
    
    if solicitud.medico_asignado != request.user:
        messages.error(request, 'No tienes permisos para emitir opinión sobre esta solicitud.')
        return redirect('lista_solicitudes')
    
    if hasattr(solicitud, 'opinion_medica'):
        messages.warning(request, 'Ya existe una opinión para esta solicitud.')
        return redirect('detalle_solicitud', solicitud_id=solicitud.id)
    
    if request.method == 'POST':
        try:
            opinion = OpinionMedica.objects.create(
                solicitud=solicitud,
                medico=request.user,
                diagnostico_propuesto=request.POST.get('diagnostico_propuesto'),
                recomendaciones=request.POST.get('recomendaciones'),
                tratamiento_sugerido=request.POST.get('tratamiento_sugerido', ''),
                comentarios_adicionales=request.POST.get('comentarios_adicionales', ''),
                requiere_seguimiento=request.POST.get('requiere_seguimiento') == 'on',
            )
            
            # Actualizar estado de la solicitud
            solicitud.estado = 'completada'
            solicitud.fecha_completada = timezone.now()
            solicitud.save()
            
            messages.success(request, 'Opinión médica emitida exitosamente.')
            return redirect('detalle_solicitud', solicitud_id=solicitud.id)
            
        except Exception as e:
            messages.error(request, f'Error al emitir la opinión: {str(e)}')
    
    context = {
        'solicitud': solicitud,
    }
    
    return render(request, 'frontend/emitir_opinion.html', context)


@login_required
def calificar_opinion(request, opinion_id):
    """Vista para que los pacientes califiquen las opiniones"""
    if request.user.rol != 'paciente':
        messages.error(request, 'Solo los pacientes pueden calificar opiniones.')
        return redirect('dashboard')
    
    opinion = get_object_or_404(OpinionMedica, id=opinion_id)
    
    if opinion.solicitud.paciente != request.user:
        messages.error(request, 'No tienes permisos para calificar esta opinión.')
        return redirect('lista_solicitudes')
    
    if hasattr(opinion, 'calificacion'):
        messages.warning(request, 'Ya has calificado esta opinión.')
        return redirect('detalle_solicitud', solicitud_id=opinion.solicitud.id)
    
    if request.method == 'POST':
        try:
            calificacion = Calificacion.objects.create(
                opinion=opinion,
                paciente=request.user,
                puntuacion=int(request.POST.get('puntuacion')),
                comentario=request.POST.get('comentario', ''),
            )
            
            messages.success(request, 'Calificación enviada exitosamente.')
            return redirect('detalle_solicitud', solicitud_id=opinion.solicitud.id)
            
        except Exception as e:
            messages.error(request, f'Error al enviar la calificación: {str(e)}')
    
    context = {
        'opinion': opinion,
    }
    
    return render(request, 'frontend/calificar_opinion.html', context)


# Vistas de autenticación
def login_view(request):
    """Vista de inicio de sesión"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Credenciales inválidas.')
    
    return render(request, 'frontend/login.html')


def register_view(request):
    """Vista de registro - SOLO para pacientes"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            # Forzar rol de paciente - los médicos no se registran por este medio
            rol = 'paciente'
            
            if password != password_confirm:
                messages.error(request, 'Las contraseñas no coinciden.')
                return render(request, 'frontend/register.html')
            
            if Usuario.objects.filter(username=username).exists():
                messages.error(request, 'El nombre de usuario ya existe.')
                return render(request, 'frontend/register.html')
            
            if Usuario.objects.filter(email=email).exists():
                messages.error(request, 'El email ya está registrado.')
                return render(request, 'frontend/register.html')
            
            user = Usuario.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                rol=rol,
                telefono=request.POST.get('telefono', ''),
                sexo=request.POST.get('sexo', ''),
                peso=request.POST.get('peso') or None,
            )
            
            messages.success(request, 'Cuenta de paciente creada exitosamente. Ya puedes iniciar sesión.')
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f'Error al crear la cuenta: {str(e)}')
    
    return render(request, 'frontend/register.html')


@login_required
def logout_view(request):
    """Vista de cierre de sesión"""
    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente.')
    return redirect('home')


# Vistas AJAX
@login_required
def ajax_asignar_medico(request):
    """Vista AJAX para asignar médico a una solicitud"""
    if request.method == 'POST' and request.user.rol == 'admin':
        try:
            data = json.loads(request.body)
            solicitud_id = data.get('solicitud_id')
            medico_id = data.get('medico_id')
            
            solicitud = get_object_or_404(SolicitudOpinion, id=solicitud_id)
            medico = get_object_or_404(Usuario, id=medico_id, rol='medico')
            
            solicitud.medico_asignado = medico
            solicitud.estado = 'asignada'
            solicitud.fecha_asignacion = timezone.now()
            solicitud.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Médico asignado exitosamente.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al asignar médico: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})


@login_required
def ajax_obtener_medicos(request):
    """Vista AJAX para obtener médicos por especialidad"""
    especialidad = request.GET.get('especialidad')
    
    medicos = Usuario.objects.filter(
        rol='medico',
        perfil_medico__activo=True
    )
    
    if especialidad:
        medicos = medicos.filter(perfil_medico__especialidad__icontains=especialidad)
    
    medicos_data = []
    for medico in medicos:
        medicos_data.append({
            'id': medico.id,
            'nombre': medico.get_full_name() or medico.username,
            'especialidad': medico.perfil_medico.especialidad,
            'experiencia': medico.perfil_medico.años_experiencia,
            'hospital': medico.perfil_medico.hospital_clinica,
        })
    
    return JsonResponse({'medicos': medicos_data})


@login_required
def crear_paciente(request):
    """Vista para que médicos creen cuentas de pacientes"""
    if request.user.rol != 'medico':
        messages.error(request, 'Solo los médicos pueden crear cuentas de pacientes.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        email_paciente = request.POST.get('email_paciente')
        nombre_completo = request.POST.get('nombre_completo')
        
        if not email_paciente:
            messages.error(request, 'El email del paciente es requerido.')
            return render(request, 'frontend/crear_paciente.html')
        
        # Usar el servicio de registro
        resultado = UsuarioRegistrationService.crear_paciente_por_medico(
            medico=request.user,
            email_paciente=email_paciente,
            nombre_completo=nombre_completo
        )
        
        if resultado['success']:
            messages.success(request, resultado['mensaje'])
            return redirect('crear_paciente')
        else:
            messages.error(request, resultado['error'])
    
    return render(request, 'frontend/crear_paciente.html')


@login_required
def cambiar_password(request):
    """Vista para cambiar la contraseña del usuario"""
    if request.method == 'POST':
        password_actual = request.POST.get('password_actual')
        password_nueva = request.POST.get('password_nueva')
        password_confirmacion = request.POST.get('password_confirmacion')
        
        # Validar contraseña actual
        if not request.user.check_password(password_actual):
            messages.error(request, 'La contraseña actual es incorrecta.')
            return render(request, 'frontend/cambiar_password.html')
        
        # Validar que las nuevas contraseñas coincidan
        if password_nueva != password_confirmacion:
            messages.error(request, 'Las nuevas contraseñas no coinciden.')
            return render(request, 'frontend/cambiar_password.html')
        
        # Validar longitud mínima
        if len(password_nueva) < 8:
            messages.error(request, 'La nueva contraseña debe tener al menos 8 caracteres.')
            return render(request, 'frontend/cambiar_password.html')
        
        try:
            # Cambiar la contraseña
            request.user.set_password(password_nueva)
            request.user.save()
            
            # Mantener la sesión activa
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            
            messages.success(request, 'Contraseña cambiada exitosamente.')
            return redirect('perfil')
            
        except Exception as e:
            messages.error(request, f'Error al cambiar la contraseña: {str(e)}')
    
    return render(request, 'frontend/cambiar_password.html')
