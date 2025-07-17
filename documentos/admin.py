from django.contrib import admin
from .models import TipoDocumento, Documento, HistorialDocumento, ArchivoTemporal


@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    """Configuración del admin para TipoDocumento"""
    list_display = ('nombre', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    """Configuración del admin para Documento"""
    list_display = ('nombre', 'tipo_documento', 'solicitud', 'usuario', 'tamaño', 'fecha_subida')
    list_filter = ('tipo_documento', 'fecha_subida')
    search_fields = ('nombre', 'solicitud__titulo', 'usuario__username')


@admin.register(HistorialDocumento)
class HistorialDocumentoAdmin(admin.ModelAdmin):
    """Configuración del admin para HistorialDocumento"""
    list_display = ('documento', 'usuario', 'accion', 'fecha_accion')
    list_filter = ('accion', 'fecha_accion')
    search_fields = ('documento__nombre', 'usuario__username')


@admin.register(ArchivoTemporal)
class ArchivoTemporalAdmin(admin.ModelAdmin):
    """Configuración del admin para ArchivoTemporal"""
    list_display = ('nombre_original', 'usuario', 'fecha_subida')
    list_filter = ('fecha_subida',)
    search_fields = ('nombre_original', 'usuario__username')
