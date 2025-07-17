from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'solicitudes', views.SolicitudOpinionViewSet)
router.register(r'opiniones', views.OpinionMedicaViewSet)
router.register(r'calificaciones', views.CalificacionViewSet)
router.register(r'seguimientos', views.SeguimientoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('estadisticas/', views.EstadisticasView.as_view(), name='estadisticas'),
    path('mis-solicitudes/', views.MisSolicitudesView.as_view(), name='mis-solicitudes'),
    path('solicitudes-asignadas/', views.SolicitudesAsignadasView.as_view(), name='solicitudes-asignadas'),
]
