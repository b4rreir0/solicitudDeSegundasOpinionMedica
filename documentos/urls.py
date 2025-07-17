from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'tipos-documento', views.TipoDocumentoViewSet)
router.register(r'documentos', views.DocumentoViewSet)
router.register(r'archivos-temporales', views.ArchivoTemporalViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('upload/', views.UploadDocumentView.as_view(), name='upload-document'),
    path('download/<int:documento_id>/', views.DownloadDocumentView.as_view(), name='download-document'),
]
