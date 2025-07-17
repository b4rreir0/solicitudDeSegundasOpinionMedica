from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from .models import Usuario, PerfilMedico
from .serializers import UsuarioSerializer, PerfilMedicoSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet para el modelo Usuario"""
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]


class PerfilMedicoViewSet(viewsets.ModelViewSet):
    """ViewSet para el modelo PerfilMedico"""
    queryset = PerfilMedico.objects.all()
    serializer_class = PerfilMedicoSerializer
    permission_classes = [IsAuthenticated]


class LoginView(APIView):
    """Vista para el login de usuarios"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Implementar lógica de login
        return Response({'message': 'Login exitoso'})


class LogoutView(APIView):
    """Vista para el logout de usuarios"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Implementar lógica de logout
        return Response({'message': 'Logout exitoso'})


class RegisterView(APIView):
    """Vista para el registro de usuarios"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Implementar lógica de registro
        return Response({'message': 'Registro exitoso'})


class ProfileView(APIView):
    """Vista para el perfil del usuario"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Implementar lógica para obtener perfil
        return Response({'message': 'Perfil del usuario'})
