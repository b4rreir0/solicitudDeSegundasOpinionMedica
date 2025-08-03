from django.urls import path
from . import views_medicos

urlpatterns = [
    path('', views_medicos.panel_medico, name='panel_medico'),
    path('solicitudes-asignadas/', views_medicos.solicitudes_asignadas_medico, name='solicitudes_asignadas_medico'),
    path('solicitudes-revision/', views_medicos.solicitudes_revision_medico, name='solicitudes_revision_medico'),
    path('chats/', views_medicos.chats_medico, name='chats_medico'),
    path('emitir-criterio/<int:solicitud_id>/', views_medicos.emitir_criterio, name='emitir_criterio'),
    path('aprobar-solicitud/<int:solicitud_id>/', views_medicos.aprobar_solicitud, name='aprobar_solicitud'),
]
