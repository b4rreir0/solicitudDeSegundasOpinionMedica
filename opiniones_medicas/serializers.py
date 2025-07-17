from rest_framework import serializers
from .models import SolicitudOpinion, OpinionMedica, Calificacion, Seguimiento


class SolicitudOpinionSerializer(serializers.ModelSerializer):
    """Serializer para SolicitudOpinion"""
    
    class Meta:
        model = SolicitudOpinion
        fields = '__all__'
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']


class OpinionMedicaSerializer(serializers.ModelSerializer):
    """Serializer para OpinionMedica"""
    
    class Meta:
        model = OpinionMedica
        fields = '__all__'
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']


class CalificacionSerializer(serializers.ModelSerializer):
    """Serializer para Calificacion"""
    
    class Meta:
        model = Calificacion
        fields = '__all__'
        read_only_fields = ['fecha_creacion']


class SeguimientoSerializer(serializers.ModelSerializer):
    """Serializer para Seguimiento"""
    
    class Meta:
        model = Seguimiento
        fields = '__all__'
        read_only_fields = ['fecha_creacion']
