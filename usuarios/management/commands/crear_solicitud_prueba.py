from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from opiniones_medicas.models import SolicitudOpinion

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Crea una solicitud de prueba para probar el flujo de asignación'
    
    def handle(self, *args, **options):
        try:
            # Obtener el paciente de prueba
            paciente = Usuario.objects.get(username='paciente_test')
            
            # Crear solicitud de prueba
            solicitud = SolicitudOpinion.objects.create(
                paciente=paciente,
                titulo='Consulta sobre tratamiento de cáncer pulmonar',
                descripcion_caso='Paciente masculino de 55 años con diagnóstico reciente de adenocarcinoma de pulmón en estadio IIIA. Requiere segunda opinión sobre opciones de tratamiento incluyendo cirugía y quimioterapia neoadyuvante.',
                tipo_cancer='pulmón',
                especialidad_requerida='Oncología Pulmonar',
                prioridad='alta',
                estado='pendiente'
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Solicitud creada: {solicitud.id} - {solicitud.titulo}')
            )
            
            self.stdout.write(
                self.style.SUCCESS('📋 Ahora puedes ejecutar: python manage.py asignar_solicitudes --once')
            )
            
        except Usuario.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('❌ No se encontró el paciente de prueba. Ejecuta primero: python manage.py crear_datos_prueba')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error al crear solicitud: {str(e)}')
            )
