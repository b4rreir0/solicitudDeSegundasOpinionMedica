from rest_framework import serializers
from .models import TipoDocumento, Documento, HistorialDocumento, ArchivoTemporal


class TipoDocumentoSerializer(serializers.ModelSerializer):
    """Serializer para TipoDocumento"""
    
    class Meta:
        model = TipoDocumento
        fields = '__all__'
        read_only_fields = ['fecha_creacion']


class DocumentoSerializer(serializers.ModelSerializer):
    """Serializer para Documento"""
    
    class Meta:
        model = Documento
        fields = '__all__'
        read_only_fields = ['fecha_subida', 'tamaño']


class HistorialDocumentoSerializer(serializers.ModelSerializer):
    """Serializer para HistorialDocumento"""
    
    class Meta:
        model = HistorialDocumento
        fields = '__all__'
        read_only_fields = ['fecha_accion']


class ArchivoTemporalSerializer(serializers.ModelSerializer):
    """Serializer para ArchivoTemporal"""
    
    class Meta:
        model = ArchivoTemporal
        fields = '__all__'
        read_only_fields = ['fecha_subida']
