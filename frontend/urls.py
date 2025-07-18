from django.urls import path
from . import views

urlpatterns = [
    # Página principal
    path('', views.home, name='home'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Perfil de usuario
    path('perfil/', views.perfil_usuario, name='perfil'),
    
    # Solicitudes
    path('solicitudes/', views.lista_solicitudes, name='lista_solicitudes'),
    path('solicitudes/nueva/', views.nueva_solicitud, name='nueva_solicitud'),
    path('solicitudes/<int:solicitud_id>/', views.detalle_solicitud, name='detalle_solicitud'),
    
    # Vistas específicas para pacientes
    path('mis-solicitudes/', views.lista_solicitudes, name='mis_solicitudes'),
    path('crear-solicitud/', views.nueva_solicitud, name='crear_solicitud'),
    
    # Vistas específicas para médicos
    path('solicitudes-asignadas/', views.lista_solicitudes, name='solicitudes_asignadas'),
    path('emitir-opinion/<int:solicitud_id>/', views.emitir_opinion, name='emitir_opinion'),
    path('opiniones-emitidas/', views.lista_solicitudes, name='opiniones_emitidas'),
    
    # Calificaciones
    path('calificar-opinion/<int:opinion_id>/', views.calificar_opinion, name='calificar_opinion'),
    
    # Vistas AJAX
    path('ajax/asignar-medico/', views.ajax_asignar_medico, name='ajax_asignar_medico'),
    path('ajax/obtener-medicos/', views.ajax_obtener_medicos, name='ajax_obtener_medicos'),
    
    # Registro de pacientes por médicos
    path('crear-paciente/', views.crear_paciente, name='crear_paciente'),
    
    # Cambiar contraseña
    path('cambiar-password/', views.cambiar_password, name='cambiar_password'),
]
