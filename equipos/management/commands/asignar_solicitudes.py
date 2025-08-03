from django.core.management.base import BaseCommand
from django.utils import timezone
from opiniones_medicas.models import SolicitudOpinion
from equipos.models import AsignacionAutomatica, EquipoTrabajo, CanalChat
import time
import threading


class Command(BaseCommand):
    help = 'Asigna automáticamente las solicitudes pendientes a equipos cada 30 segundos'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--once',
            action='store_true',
            help='Ejecutar solo una vez, no en bucle',
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=30,
            help='Intervalo en segundos entre ejecuciones (default: 30)',
        )
    
    def asignar_solicitudes_pendientes(self):
        """Lógica principal para asignar solicitudes"""
        pendientes = SolicitudOpinion.objects.filter(estado='pendiente')
        if not pendientes.exists():
            self.stdout.write(self.style.WARNING('No hay solicitudes pendientes para asignar.'))
            return 0

        asignadas = 0
        for solicitud in pendientes:
            if self.asignar_solicitud_individual(solicitud):
                asignadas += 1
        
        return asignadas
    
    def asignar_solicitud_individual(self, solicitud):
        """Asigna una solicitud individual a un equipo"""
        try:
            # Buscar reglas de asignación aplicables
            reglas = AsignacionAutomatica.objects.filter(activo=True).order_by('prioridad')
            
            for regla in reglas:
                equipo = None
                
                # Evaluar diferentes criterios
                if regla.criterio == 'especialidad' and solicitud.especialidad_requerida:
                    if regla.valor.lower() in solicitud.especialidad_requerida.lower():
                        equipo = regla.equipo
                
                elif regla.criterio == 'tipo_cancer' and solicitud.tipo_cancer:
                    if regla.valor.lower() in solicitud.tipo_cancer.lower():
                        equipo = regla.equipo
                
                elif regla.criterio == 'prioridad':
                    if regla.valor == str(solicitud.prioridad):
                        equipo = regla.equipo
                
                # Si encontramos un equipo, asignar
                if equipo and equipo.activo:
                    solicitud.equipo_asignado = equipo
                    solicitud.estado = 'asignada'
                    solicitud.fecha_asignacion = timezone.now()
                    solicitud.save()

                    # Crear canal de chat para la solicitud
                    canal_nombre = f"Solicitud #{solicitud.id} - {solicitud.titulo[:50]}"
                    CanalChat.objects.get_or_create(
                        equipo=equipo,
                        nombre=canal_nombre,
                        defaults={
                            'descripcion': f'Chat para solicitud de {solicitud.paciente.nombre_completo}'
                        }
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Solicitud {solicitud.id} asignada al equipo {equipo.nombre}'
                        )
                    )
                    return True
            
            # Si no se pudo asignar, buscar equipo por defecto
            equipo_default = EquipoTrabajo.objects.filter(activo=True).first()
            if equipo_default:
                solicitud.equipo_asignado = equipo_default
                solicitud.estado = 'asignada'
                solicitud.fecha_asignacion = timezone.now()
                solicitud.save()
                
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  Solicitud {solicitud.id} asignada al equipo por defecto: {equipo_default.nombre}'
                    )
                )
                return True
            
            self.stdout.write(
                self.style.ERROR(
                    f'❌ No se pudo asignar solicitud {solicitud.id} - Sin equipos disponibles'
                )
            )
            return False
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Error al asignar solicitud {solicitud.id}: {str(e)}'
                )
            )
            return False

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                '🚀 Iniciando servicio de asignación automática de solicitudes...'
            )
        )
        
        if options['once']:
            # Ejecutar solo una vez
            asignadas = self.asignar_solicitudes_pendientes()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Proceso completado. {asignadas} solicitudes asignadas.'
                )
            )
        else:
            # Ejecutar en bucle
            interval = options['interval']
            self.stdout.write(
                self.style.WARNING(
                    f'⏰ Ejecutándose cada {interval} segundos. Presiona Ctrl+C para detener.'
                )
            )
            
            try:
                while True:
                    start_time = time.time()
                    asignadas = self.asignar_solicitudes_pendientes()
                    
                    if asignadas > 0:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✅ Ciclo completado. {asignadas} solicitudes asignadas en {time.time() - start_time:.2f}s'
                            )
                        )
                    
                    time.sleep(interval)
                    
            except KeyboardInterrupt:
                self.stdout.write(
                    self.style.WARNING(
                        '\n🛑 Servicio de asignación automática detenido por el usuario.'
                    )
                )

