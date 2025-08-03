from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import views_medicos

router = DefaultRouter()
router.register(r'usuarios', views.UsuarioViewSet)
router.register(r'perfiles-medicos', views.PerfilMedicoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/profile/', views.ProfileView.as_view(), name='profile'),
    
    # Panel médico
    path('panel-medico/', views_medicos.panel_medico, name='panel_medico'),
    path('solicitudes-asignadas/', views_medicos.solicitudes_asignadas_medico, name='solicitudes_asignadas_medico'),
    path('solicitudes-revision/', views_medicos.solicitudes_revision_medico, name='solicitudes_revision_medico'),
    path('chats-medico/', views_medicos.chats_medico, name='chats_medico'),
    path('emitir-criterio/<int:solicitud_id>/', views_medicos.emitir_criterio, name='emitir_criterio'),
    path('aprobar-solicitud/<int:solicitud_id>/', views_medicos.aprobar_solicitud, name='aprobar_solicitud'),
]
