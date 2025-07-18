from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from .models import Usuario, PerfilMedico
from .serializers import UsuarioSerializer, PerfilMedicoSerializer
from .forms import RegistroPacienteForm, UsuarioUpdateForm
from django.contrib.auth.forms import UserCreationForm


class RegistroPacienteView(viewsets.ViewSet):
    """Vista para el registro de pacientes por médicos"""
    permission_classes = [IsAuthenticated]

    def create(self, request):
        form = RegistroPacienteForm(request.data or None)
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                return Response({'message': 'Paciente registrado y credenciales enviadas con éxito.'})
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
        return render(request, 'frontend/crear_paciente.html', {'form': form})


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
