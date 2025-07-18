from django.urls import path
from . import views

app_name = 'equipos'

urlpatterns = [
    # Vistas principales de equipos
    path('', views.lista_equipos, name='lista_equipos'),
    path('mis-equipos/', views.mis_equipos, name='mis_equipos'),
    path('crear/', views.crear_equipo, name='crear_equipo'),
    path('<int:equipo_id>/', views.detalle_equipo, name='detalle_equipo'),
    
    # Chat del equipo
    path('<int:equipo_id>/chat/', views.chat_equipo, name='chat_equipo'),
    path('<int:equipo_id>/chat/enviar/', views.enviar_mensaje, name='enviar_mensaje'),
    path('<int:equipo_id>/chat/mensajes/', views.obtener_mensajes, name='obtener_mensajes'),
    
    # Asignación automática
    path('asignar-solicitud/<int:solicitud_id>/', views.asignar_solicitud_automatica, name='asignar_solicitud_automatica'),
]
