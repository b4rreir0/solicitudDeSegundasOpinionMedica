from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
import random
import string

from usuarios.models import PerfilMedico
from equipos.models import EspecialidadOncologica, EquipoTrabajo, MiembroEquipo, AsignacionAutomatica
from opiniones_medicas.models import SolicitudOpinion

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Crea datos de prueba completos: paciente, especialidad, grupo de trabajo, reglas de asignación'
    
    def generate_password(self, length=8):
        """Genera una contraseña aleatoria"""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                credenciales = []
                
                # 1. Crear especialidad oncológica
                especialidad, created = EspecialidadOncologica.objects.get_or_create(
                    nombre='Oncología Pulmonar',
                    defaults={
                        'descripcion': 'Especialidad enfocada en el tratamiento de cáncer de pulmón',
                        'icono': 'fas fa-lungs',
                        'activo': True
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'✅ Especialidad creada: {especialidad.nombre}'))
                else:
                    self.stdout.write(self.style.WARNING(f'⚠️  Especialidad ya existe: {especialidad.nombre}'))
                
                # 2. Crear paciente
                paciente_password = self.generate_password()
                try:
                    paciente = Usuario.objects.get(username='paciente_test')
                    created = False
                except Usuario.DoesNotExist:
                    paciente = Usuario(
                        username='paciente_test',
                        email='paciente.test@test.com',
                        first_name='María',
                        last_name='García',
                        rol='paciente',
                        telefono='+5215551111111',
                        sexo='F',
                        peso=65.0
                    )
                    paciente.set_password(paciente_password)
                    paciente.save()
                    created = True
                
                if created:
                    credenciales.append({
                        'tipo': 'Paciente',
                        'nombre': f'{paciente.first_name} {paciente.last_name}',
                        'username': paciente.username,
                        'email': paciente.email,
                        'password': paciente_password
                    })
                    self.stdout.write(self.style.SUCCESS(f'✅ Paciente creado: {paciente.username}'))
                else:
                    self.stdout.write(self.style.WARNING(f'⚠️  Paciente ya existe: {paciente.username}'))
                
                # 3. Crear médico líder
                lider_password = self.generate_password()
                try:
                    medico_lider = Usuario.objects.get(username='dr_lider')
                    created = False
                except Usuario.DoesNotExist:
                    medico_lider = Usuario.objects.create_user(
                        username='dr_lider',
                        email='dr.lider@test.com',
                        password=lider_password,
                        first_name='Roberto',
                        last_name='Martínez',
                        rol='medico',
                        telefono='+5215552222222'
                    )
                    created = True
                    
                    # Crear perfil médico para el líder
                    PerfilMedico.objects.create(
                        usuario=medico_lider,
                        numero_colegiado='LIDER001',
                        especialidad='Oncología Pulmonar',
                        hospital_clinica='Hospital Central',
                        años_experiencia=15
                    )
                    
                    credenciales.append({
                        'tipo': 'Médico Líder',
                        'nombre': f'{medico_lider.first_name} {medico_lider.last_name}',
                        'username': medico_lider.username,
                        'email': medico_lider.email,
                        'password': lider_password,
                        'especialidad': 'Oncología Pulmonar'
                    })
                    self.stdout.write(self.style.SUCCESS(f'✅ Médico líder creado: {medico_lider.username}'))
                else:
                    self.stdout.write(self.style.WARNING(f'⚠️  Médico líder ya existe: {medico_lider.username}'))
                
                # 4. Crear segundo médico
                medico2_password = self.generate_password()
                try:
                    medico2 = Usuario.objects.get(username='dr_colaborador')
                    created = False
                except Usuario.DoesNotExist:
                    medico2 = Usuario.objects.create_user(
                        username='dr_colaborador',
                        email='dr.colaborador@test.com',
                        password=medico2_password,
                        first_name='Ana',
                        last_name='López',
                        rol='medico',
                        telefono='+5215553333333'
                    )
                    created = True
                    
                    # Crear perfil médico para el colaborador
                    PerfilMedico.objects.create(
                        usuario=medico2,
                        numero_colegiado='COLAB001',
                        especialidad='Oncología Pulmonar',
                        hospital_clinica='Hospital Central',
                        años_experiencia=8
                    )
                    
                    credenciales.append({
                        'tipo': 'Médico Colaborador',
                        'nombre': f'{medico2.first_name} {medico2.last_name}',
                        'username': medico2.username,
                        'email': medico2.email,
                        'password': medico2_password,
                        'especialidad': 'Oncología Pulmonar'
                    })
                    self.stdout.write(self.style.SUCCESS(f'✅ Médico colaborador creado: {medico2.username}'))
                else:
                    self.stdout.write(self.style.WARNING(f'⚠️  Médico colaborador ya existe: {medico2.username}'))
                
                # 5. Crear equipo de trabajo
                equipo, created = EquipoTrabajo.objects.get_or_create(
                    nombre='Equipo Oncología Pulmonar',
                    defaults={
                        'especialidad': especialidad,
                        'descripcion': 'Equipo multidisciplinario especializado en cáncer de pulmón',
                        'coordinador': medico_lider,
                        'activo': True
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'✅ Equipo creado: {equipo.nombre}'))
                    
                    # Agregar miembros al equipo
                    MiembroEquipo.objects.get_or_create(
                        equipo=equipo,
                        usuario=medico_lider,
                        defaults={'rol_en_equipo': 'coordinador'}
                    )
                    
                    MiembroEquipo.objects.get_or_create(
                        equipo=equipo,
                        usuario=medico2,
                        defaults={'rol_en_equipo': 'oncologo'}
                    )
                    
                    self.stdout.write(self.style.SUCCESS('✅ Miembros agregados al equipo'))
                else:
                    self.stdout.write(self.style.WARNING(f'⚠️  Equipo ya existe: {equipo.nombre}'))
                
                # 6. Crear reglas de asignación automática
                regla, created = AsignacionAutomatica.objects.get_or_create(
                    equipo=equipo,
                    criterio='tipo_cancer',
                    valor='pulmón',
                    defaults={
                        'prioridad': 1,
                        'activo': True
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS('✅ Regla de asignación creada para cáncer de pulmón'))
                else:
                    self.stdout.write(self.style.WARNING('⚠️  Regla de asignación ya existe'))
                
                # Regla alternativa para especialidad
                regla2, created = AsignacionAutomatica.objects.get_or_create(
                    equipo=equipo,
                    criterio='especialidad',
                    valor='Oncología Pulmonar',
                    defaults={
                        'prioridad': 2,
                        'activo': True
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS('✅ Regla de asignación creada para especialidad'))
                
                # 7. Crear solicitud de prueba
                solicitud, created = SolicitudOpinion.objects.get_or_create(
                    titulo='Consulta sobre nódulo pulmonar',
                    defaults={
                        'paciente': paciente,
                        'descripcion_caso': 'Paciente de 45 años con nódulo pulmonar detectado en TAC de rutina. Solicito segunda opinión para determinar protocolo de seguimiento.',
                        'tipo_cancer': 'pulmón',
                        'especialidad_requerida': 'Oncología Pulmonar',
                        'prioridad': 'alta',
                        'estado': 'pendiente'
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS('✅ Solicitud de prueba creada'))
                else:
                    self.stdout.write(self.style.WARNING('⚠️  Solicitud de prueba ya existe'))
                
                # Mostrar credenciales
                if credenciales:
                    self.stdout.write(self.style.SUCCESS('\n🔑 === CREDENCIALES CREADAS ===\n'))
                    
                    for cred in credenciales:
                        self.stdout.write(f"🔹 {cred['tipo']}: {cred['nombre']}")
                        self.stdout.write(f"   Username: {cred['username']}")
                        self.stdout.write(f"   Email: {cred['email']}")
                        self.stdout.write(f"   Password: {cred['password']}")
                        if 'especialidad' in cred:
                            self.stdout.write(f"   Especialidad: {cred['especialidad']}")
                        self.stdout.write("")
                
                self.stdout.write(self.style.SUCCESS('✅ Todos los datos de prueba han sido creados correctamente.'))
                self.stdout.write(self.style.WARNING('⚠️  GUARDA ESTAS CREDENCIALES EN UN LUGAR SEGURO'))
                self.stdout.write(self.style.SUCCESS('\n📋 Para probar el flujo:'))
                self.stdout.write('   1. Ejecuta: python manage.py asignar_solicitudes --once')
                self.stdout.write('   2. La solicitud debe ser asignada automáticamente al equipo')
                self.stdout.write('   3. Los médicos pueden revisar y el líder aprobar')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error al crear datos de prueba: {str(e)}')
            )
