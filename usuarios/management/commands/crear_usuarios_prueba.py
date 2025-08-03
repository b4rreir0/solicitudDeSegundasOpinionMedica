from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from usuarios.models import PerfilMedico
from django.db import transaction
import random
import string

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Crea usuarios de prueba: 1 paciente, 2 médicos y 1 admin'
    
    def generate_password(self, length=8):
        """Genera una contraseña aleatoria"""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Lista para almacenar las credenciales
                credenciales = []
                
                # 1. Crear 1 Paciente
                paciente_password = self.generate_password()
                paciente = Usuario.objects.create_user(
                    username='paciente1',
                    email='paciente1@test.com',
                    password=paciente_password,
                    first_name='Juan',
                    last_name='Pérez',
                    rol='paciente',
                    telefono='+5215551234567',
                    sexo='M',
                    peso=75.5
                )
                credenciales.append({
                    'rol': 'Paciente',
                    'nombre': f'{paciente.first_name} {paciente.last_name}',
                    'username': paciente.username,
                    'email': paciente.email,
                    'password': paciente_password
                })
                
                # 2. Crear 2 Médicos
                medico1_password = self.generate_password()
                medico1 = Usuario.objects.create_user(
                    username='medico1',
                    email='medico1@test.com',
                    password=medico1_password,
                    first_name='María',
                    last_name='González',
                    rol='medico',
                    telefono='+5215551234568'
                )
                
                # Crear perfil médico para médico1
                PerfilMedico.objects.create(
                    usuario=medico1,
                    numero_colegiado='MED001',
                    especialidad='Cardiología',
                    hospital_clinica='Hospital General',
                    años_experiencia=10
                )
                
                credenciales.append({
                    'rol': 'Médico',
                    'nombre': f'{medico1.first_name} {medico1.last_name}',
                    'username': medico1.username,
                    'email': medico1.email,
                    'password': medico1_password,
                    'especialidad': 'Cardiología'
                })
                
                medico2_password = self.generate_password()
                medico2 = Usuario.objects.create_user(
                    username='medico2',
                    email='medico2@test.com',
                    password=medico2_password,
                    first_name='Carlos',
                    last_name='Rodríguez',
                    rol='medico',
                    telefono='+5215551234569'
                )
                
                # Crear perfil médico para médico2
                PerfilMedico.objects.create(
                    usuario=medico2,
                    numero_colegiado='MED002',
                    especialidad='Oncología',
                    hospital_clinica='Hospital Universitario',
                    años_experiencia=15
                )
                
                credenciales.append({
                    'rol': 'Médico',
                    'nombre': f'{medico2.first_name} {medico2.last_name}',
                    'username': medico2.username,
                    'email': medico2.email,
                    'password': medico2_password,
                    'especialidad': 'Oncología'
                })
                
                # 3. Crear 1 Administrador
                admin_password = self.generate_password()
                admin = Usuario.objects.create_user(
                    username='admin1',
                    email='admin1@test.com',
                    password=admin_password,
                    first_name='Ana',
                    last_name='Martínez',
                    rol='admin',
                    telefono='+5215551234570',
                    is_staff=True,
                    is_superuser=True
                )
                
                credenciales.append({
                    'rol': 'Administrador',
                    'nombre': f'{admin.first_name} {admin.last_name}',
                    'username': admin.username,
                    'email': admin.email,
                    'password': admin_password
                })
                
                # Mostrar las credenciales
                self.stdout.write(self.style.SUCCESS('\n=== USUARIOS CREADOS EXITOSAMENTE ===\n'))
                
                for cred in credenciales:
                    self.stdout.write(f"🔹 {cred['rol']}: {cred['nombre']}")
                    self.stdout.write(f"   Username: {cred['username']}")
                    self.stdout.write(f"   Email: {cred['email']}")
                    self.stdout.write(f"   Password: {cred['password']}")
                    if 'especialidad' in cred:
                        self.stdout.write(f"   Especialidad: {cred['especialidad']}")
                    self.stdout.write("")
                
                self.stdout.write(self.style.SUCCESS('✅ Todos los usuarios han sido creados correctamente.'))
                self.stdout.write(self.style.WARNING('⚠️  GUARDA ESTAS CREDENCIALES EN UN LUGAR SEGURO'))
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error al crear usuarios: {str(e)}')
            )
