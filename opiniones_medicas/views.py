from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import SolicitudOpinion, OpinionMedica, Calificacion, Seguimiento
from .serializers import (
    SolicitudOpinionSerializer, OpinionMedicaSerializer,
    CalificacionSerializer, SeguimientoSerializer
)


class SolicitudOpinionViewSet(viewsets.ModelViewSet):
    """ViewSet para SolicitudOpinion"""
    queryset = SolicitudOpinion.objects.all()
    serializer_class = SolicitudOpinionSerializer
    permission_classes = [IsAuthenticated]


class OpinionMedicaViewSet(viewsets.ModelViewSet):
    """ViewSet para OpinionMedica"""
    queryset = OpinionMedica.objects.all()
    serializer_class = OpinionMedicaSerializer
    permission_classes = [IsAuthenticated]


class CalificacionViewSet(viewsets.ModelViewSet):
    """ViewSet para Calificacion"""
    queryset = Calificacion.objects.all()
    serializer_class = CalificacionSerializer
    permission_classes = [IsAuthenticated]


class SeguimientoViewSet(viewsets.ModelViewSet):
    """ViewSet para Seguimiento"""
    queryset = Seguimiento.objects.all()
    serializer_class = SeguimientoSerializer
    permission_classes = [IsAuthenticated]


class EstadisticasView(APIView):
    """Vista para obtener estadísticas"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'message': 'Estadísticas'})


class MisSolicitudesView(APIView):
    """Vista para obtener las solicitudes del usuario"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'message': 'Mis solicitudes'})


class SolicitudesAsignadasView(APIView):
    """Vista para obtener las solicitudes asignadas al médico"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'message': 'Solicitudes asignadas'})
