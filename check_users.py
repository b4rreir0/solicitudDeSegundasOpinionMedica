#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solicitud_medica.settings')
django.setup()

from usuarios.models import Usuario

def check_users():
    print("=== USUARIOS EXISTENTES ===")
    users = Usuario.objects.all()
    
    if not users:
        print("No hay usuarios en la base de datos")
        return
    
    print(f"Total de usuarios: {users.count()}")
    print("\nDetalles de usuarios:")
    print("-" * 60)
    
    for user in users:
        print(f"Usuario: {user.username}")
        print(f"Nombre: {user.first_name} {user.last_name}")
        print(f"Email: {user.email}")
        print(f"Rol: {user.get_rol_display()}")
        print(f"Activo: {user.is_active}")
        print(f"Staff: {user.is_staff}")
        print(f"Superuser: {user.is_superuser}")
        print("-" * 60)

if __name__ == "__main__":
    check_users()
