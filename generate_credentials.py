#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solicitud_medica.settings')
django.setup()

from usuarios.models import Usuario

def generate_credentials():
    print("=" * 80)
    print("CREDENCIALES DE ACCESO PARA PRUEBAS")
    print("=" * 80)
    
    # Buscar un administrador
    admin_user = Usuario.objects.filter(is_superuser=True).first()
    if admin_user:
        print("\n🔑 ADMINISTRADOR:")
        print(f"   Usuario: {admin_user.username}")
        print(f"   Contraseña: 123456")  # Contraseña común para pruebas
        print(f"   Nombre: {admin_user.first_name} {admin_user.last_name}")
        print(f"   Email: {admin_user.email}")
        print(f"   Rol: {admin_user.get_rol_display()}")
    
    # Buscar dos médicos
    medicos = Usuario.objects.filter(rol='medico')[:2]
    print(f"\n👨‍⚕️ MÉDICOS ({len(medicos)} disponibles):")
    for i, medico in enumerate(medicos, 1):
        print(f"   --- Médico {i} ---")
        print(f"   Usuario: {medico.username}")
        print(f"   Contraseña: 123456")  # Contraseña común para pruebas
        print(f"   Nombre: {medico.first_name} {medico.last_name}")
        print(f"   Email: {medico.email}")
        print(f"   Rol: {medico.get_rol_display()}")
        print()
    
    # Buscar un paciente
    pacientes = Usuario.objects.filter(rol='paciente', is_superuser=False)[:2]
    print(f"👤 PACIENTES ({len(pacientes)} disponibles):")
    for i, paciente in enumerate(pacientes, 1):
        print(f"   --- Paciente {i} ---")
        print(f"   Usuario: {paciente.username}")
        print(f"   Contraseña: 123456")  # Contraseña común para pruebas
        print(f"   Nombre: {paciente.first_name} {paciente.last_name}")
        print(f"   Email: {paciente.email}")
        print(f"   Rol: {paciente.get_rol_display()}")
        print()
    
    print("=" * 80)
    print("NOTA: Todas las contraseñas son '123456' para facilitar las pruebas")
    print("=" * 80)

def reset_passwords():
    """Resetea las contraseñas de algunos usuarios para pruebas"""
    print("Actualizando contraseñas para pruebas...")
    
    # Usuarios específicos para resetear
    usernames = ['admin', 'German', 'dr_rodriguez', 'dra_martinez', 'paciente001', 'paciente002']
    
    for username in usernames:
        try:
            user = Usuario.objects.get(username=username)
            user.set_password('123456')
            user.save()
            print(f"✅ Contraseña actualizada para {username}")
        except Usuario.DoesNotExist:
            print(f"❌ Usuario {username} no encontrado")
    
    print("¡Contraseñas actualizadas!")

if __name__ == "__main__":
    reset_passwords()
    print("\n")
    generate_credentials()
