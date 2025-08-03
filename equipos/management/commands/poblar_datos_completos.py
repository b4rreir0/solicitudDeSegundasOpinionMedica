from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
import random
from faker import Faker
import pytz

from equipos.models import EspecialidadOncologica, EquipoTrabajo, MiembroEquipo, AsignacionAutomatica, CanalChat, MensajeChat
from usuarios.models import Usuario, PerfilMedico, CodigoVerificacion
from opiniones_medicas.models import SolicitudOpinion, OpinionMedica, Calificacion, Seguimiento
from documentos.models import Documento, TipoDocumento


class Command(BaseCommand):
    help = 'Poblar la base de datos con datos completos y realistas para pruebas'

    def __init__(self):
        super().__init__()
        self.fake = Faker('es_ES')
        
    def add_arguments(self, parser):
        parser.add_argument(
            '--patients',
            type=int,
            default=50,
            help='Número de pacientes a crear (default: 50)'
        )
        parser.add_argument(
            '--doctors',
            type=int,
            default=20,
            help='Número de médicos a crear (default: 20)'
        )
        parser.add_argument(
            '--requests',
            type=int,
            default=100,
            help='Número de solicitudes a crear (default: 100)'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Iniciando poblado completo de la base de datos...'))
        
        with transaction.atomic():
            # 1. Crear especialidades oncológicas
            self.crear_especialidades()
            
            # 2. Crear tipos de documento
            self.crear_tipos_documento()
            
            # 3. Crear usuarios administrativos
            self.crear_admin()
            
            # 4. Crear médicos
            self.crear_medicos(options['doctors'])
            
            # 5. Crear pacientes
            self.crear_pacientes(options['patients'])
            
            # 6. Crear equipos de trabajo
            self.crear_equipos_trabajo()
            
            # 7. Crear reglas de asignación
            self.crear_reglas_asignacion()
            
            # 8. Crear solicitudes de opinión
            self.crear_solicitudes(options['requests'])
            
            # 9. Crear opiniones médicas
            self.crear_opiniones_medicas()
            
            # 10. Crear calificaciones
            self.crear_calificaciones()
            
            # 11. Crear seguimientos
            self.crear_seguimientos()
            
            # 12. Crear chats de equipo
            self.crear_chats_equipo()
        
        self.stdout.write(self.style.SUCCESS('✅ Base de datos poblada exitosamente!'))
        self.mostrar_estadisticas()

    def crear_especialidades(self):
        """Crear especialidades oncológicas"""
        self.stdout.write('📋 Creando especialidades oncológicas...')
        
        especialidades = [
            {
                'nombre': 'Oncología de Mama',
                'descripcion': 'Especialidad dedicada al diagnóstico y tratamiento integral del cáncer de mama',
                'icono': 'fas fa-ribbon'
            },
            {
                'nombre': 'Oncología Pulmonar',
                'descripcion': 'Especialidad enfocada en el tratamiento del cáncer de pulmón y vías respiratorias',
                'icono': 'fas fa-lungs'
            },
            {
                'nombre': 'Oncología Gastrointestinal',
                'descripcion': 'Tratamiento de cánceres del sistema digestivo y órganos relacionados',
                'icono': 'fas fa-stomach'
            },
            {
                'nombre': 'Oncología Urológica',
                'descripcion': 'Especialidad en cánceres del sistema genitourinario',
                'icono': 'fas fa-kidney'
            },
            {
                'nombre': 'Oncología Ginecológica',
                'descripcion': 'Tratamiento de cánceres del sistema reproductor femenino',
                'icono': 'fas fa-female'
            },
            {
                'nombre': 'Oncología Hematológica',
                'descripcion': 'Especialidad en cánceres de la sangre y médula ósea',
                'icono': 'fas fa-tint'
            },
            {
                'nombre': 'Oncología Dermatológica',
                'descripcion': 'Tratamiento de cánceres de la piel y tejidos blandos',
                'icono': 'fas fa-hand-paper'
            },
            {
                'nombre': 'Neuro-oncología',
                'descripcion': 'Especialidad en tumores del sistema nervioso central',
                'icono': 'fas fa-brain'
            },
            {
                'nombre': 'Oncología Pediátrica',
                'descripcion': 'Tratamiento de cánceres en niños y adolescentes',
                'icono': 'fas fa-child'
            },
            {
                'nombre': 'Oncología de Cabeza y Cuello',
                'descripcion': 'Tratamiento de cánceres en la región de cabeza y cuello',
                'icono': 'fas fa-head-side-mask'
            }
        ]
        
        for esp_data in especialidades:
            especialidad, created = EspecialidadOncologica.objects.get_or_create(
                nombre=esp_data['nombre'],
                defaults={
                    'descripcion': esp_data['descripcion'],
                    'icono': esp_data['icono']
                }
            )
            if created:
                self.stdout.write(f'  ✅ {especialidad.nombre}')

    def crear_tipos_documento(self):
        """Crear tipos de documento"""
        self.stdout.write('📄 Creando tipos de documento...')
        
        tipos = [
            {'nombre': 'Historial Médico', 'descripcion': 'Historial médico completo del paciente'},
            {'nombre': 'Radiografías', 'descripcion': 'Imágenes radiológicas'},
            {'nombre': 'Tomografías', 'descripcion': 'Estudios de tomografía computarizada'},
            {'nombre': 'Resonancia Magnética', 'descripcion': 'Estudios de resonancia magnética'},
            {'nombre': 'Biopsia', 'descripcion': 'Resultados de biopsia'},
            {'nombre': 'Análisis de Sangre', 'descripcion': 'Análisis de laboratorio'},
            {'nombre': 'Ecografías', 'descripcion': 'Estudios ecográficos'},
            {'nombre': 'Endoscopia', 'descripcion': 'Estudios endoscópicos'},
            {'nombre': 'Mamografía', 'descripcion': 'Estudios mamográficos'},
            {'nombre': 'Informes Médicos', 'descripcion': 'Informes médicos anteriores'},
        ]
        
        for tipo_data in tipos:
            tipo, created = TipoDocumento.objects.get_or_create(
                nombre=tipo_data['nombre'],
                defaults={
                    'descripcion': tipo_data['descripcion'],
                    'activo': True
                }
            )
            if created:
                self.stdout.write(f'  ✅ {tipo.nombre}')

    def crear_admin(self):
        """Crear usuario administrador"""
        self.stdout.write('👑 Creando administrador...')
        
        admin, created = Usuario.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Administrador',
                'last_name': 'Sistema',
                'email': 'admin@hospital.com',
                'rol': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
                'telefono': '+34 900 123 456',
                'direccion': 'Hospital Central, Madrid',
                'sexo': 'M',
                'fecha_nacimiento': datetime(1980, 1, 1).date(),
            }
        )
        
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write('  ✅ Administrador creado (usuario: admin, contraseña: admin123)')

    def crear_medicos(self, cantidad):
        """Crear médicos con perfiles completos"""
        self.stdout.write(f'👨‍⚕️ Creando {cantidad} médicos...')
        
        especialidades = list(EspecialidadOncologica.objects.all())
        hospitales = [
            'Hospital Universitario La Paz',
            'Hospital Clínico San Carlos',
            'Hospital Ramón y Cajal',
            'Hospital Universitario 12 de Octubre',
            'Hospital Gregorio Marañón',
            'Hospital Vall d\'Hebron',
            'Hospital Clínic de Barcelona',
            'Hospital La Fe Valencia',
            'Hospital Virgen del Rocío',
            'Hospital Universitario Central de Asturias'
        ]
        
        for i in range(cantidad):
            especialidad = random.choice(especialidades)
            
            # Crear usuario médico
            usuario = Usuario.objects.create_user(
                username=f'medico{i+1:03d}',
                first_name=self.fake.first_name(),
                last_name=self.fake.last_name(),
                email=f'medico{i+1:03d}@hospital.com',
                password='medico123',
                rol='medico',
                is_staff=True,
                is_active=True,
                telefono=self.fake.phone_number(),
                direccion=self.fake.address(),
                sexo=random.choice(['M', 'F']),
                fecha_nacimiento=self.fake.date_of_birth(minimum_age=30, maximum_age=65),
                peso=random.randint(50, 100)
            )
            
            # Crear perfil médico
            PerfilMedico.objects.create(
                usuario=usuario,
                numero_colegiado=f'COL{i+1:04d}',
                especialidad=especialidad.nombre,
                años_experiencia=random.randint(5, 30),
                hospital_clinica=random.choice(hospitales),
                activo=True
            )
            
            if i % 10 == 0:
                self.stdout.write(f'  ✅ Creados {i+1} médicos...')

    def crear_pacientes(self, cantidad):
        """Crear pacientes"""
        self.stdout.write(f'🏥 Creando {cantidad} pacientes...')
        
        for i in range(cantidad):
            usuario = Usuario.objects.create_user(
                username=f'paciente{i+1:03d}',
                first_name=self.fake.first_name(),
                last_name=self.fake.last_name(),
                email=f'paciente{i+1:03d}@email.com',
                password='paciente123',
                rol='paciente',
                is_active=True,
                telefono=self.fake.phone_number(),
                direccion=self.fake.address(),
                sexo=random.choice(['M', 'F']),
                fecha_nacimiento=self.fake.date_of_birth(minimum_age=18, maximum_age=80),
                peso=random.randint(40, 120)
            )
            
            if i % 20 == 0:
                self.stdout.write(f'  ✅ Creados {i+1} pacientes...')

    def crear_equipos_trabajo(self):
        """Crear equipos de trabajo"""
        self.stdout.write('🏥 Creando equipos de trabajo...')
        
        especialidades = EspecialidadOncologica.objects.all()
        medicos = Usuario.objects.filter(rol='medico')
        
        for especialidad in especialidades:
            # Buscar médicos de esta especialidad
            medicos_especialidad = medicos.filter(
                perfil_medico__especialidad=especialidad.nombre
            )
            
            if medicos_especialidad.exists():
                coordinador = medicos_especialidad.first()
                
                equipo, created = EquipoTrabajo.objects.get_or_create(
                    nombre=f'Equipo de {especialidad.nombre}',
                    defaults={
                        'especialidad': especialidad,
                        'descripcion': f'Equipo multidisciplinario especializado en {especialidad.nombre.lower()}, '
                                       f'dedicado a brindar atención integral y segunda opinión médica.',
                        'coordinador': coordinador,
                        'activo': True
                    }
                )
                
                # Agregar coordinador como miembro
                MiembroEquipo.objects.get_or_create(
                    equipo=equipo,
                    usuario=coordinador,
                    defaults={
                        'rol_en_equipo': 'coordinador',
                        'activo': True
                    }
                )
                
                # Agregar otros miembros del equipo
                otros_medicos = list(medicos_especialidad.exclude(id=coordinador.id))
                if otros_medicos:
                    # Agregar 2-4 miembros más
                    num_miembros = min(random.randint(2, 4), len(otros_medicos))
                    miembros_equipo = random.sample(otros_medicos, num_miembros)
                    
                    roles = ['oncologo', 'radiologo', 'patologo', 'cirujano', 'enfermero']
                    
                    for miembro in miembros_equipo:
                        MiembroEquipo.objects.get_or_create(
                            equipo=equipo,
                            usuario=miembro,
                            defaults={
                                'rol_en_equipo': random.choice(roles),
                                'activo': True
                            }
                        )
                
                self.stdout.write(f'  ✅ {equipo.nombre} ({equipo.total_miembros} miembros)')

    def crear_reglas_asignacion(self):
        """Crear reglas de asignación automática"""
        self.stdout.write('⚙️ Creando reglas de asignación...')
        
        equipos = EquipoTrabajo.objects.all()
        
        # Mapeo de tipos de cáncer por especialidad
        tipos_cancer = {
            'Oncología de Mama': ['mama', 'seno', 'mamario'],
            'Oncología Pulmonar': ['pulmón', 'pulmonar', 'bronquial', 'pleural'],
            'Oncología Gastrointestinal': ['colon', 'estómago', 'intestino', 'hígado', 'páncreas', 'esófago'],
            'Oncología Urológica': ['próstata', 'vejiga', 'riñón', 'testicular', 'renal'],
            'Oncología Ginecológica': ['ovario', 'cérvix', 'útero', 'endometrio', 'vaginal'],
            'Oncología Hematológica': ['leucemia', 'linfoma', 'mieloma', 'hodgkin'],
            'Oncología Dermatológica': ['melanoma', 'piel', 'basocelular', 'escamocelular'],
            'Neuro-oncología': ['cerebro', 'glioma', 'meningioma', 'neurológico'],
            'Oncología Pediátrica': ['pediátrico', 'infantil', 'niños'],
            'Oncología de Cabeza y Cuello': ['cabeza', 'cuello', 'tiroides', 'laringe']
        }
        
        for equipo in equipos:
            especialidad_nombre = equipo.especialidad.nombre
            
            if especialidad_nombre in tipos_cancer:
                for tipo in tipos_cancer[especialidad_nombre]:
                    AsignacionAutomatica.objects.get_or_create(
                        equipo=equipo,
                        criterio='tipo_cancer',
                        valor=tipo,
                        defaults={
                            'prioridad': 1,
                            'activo': True
                        }
                    )
                
                self.stdout.write(f'  ✅ Reglas para {equipo.nombre}')

    def crear_solicitudes(self, cantidad):
        """Crear solicitudes de opinión médica"""
        self.stdout.write(f'📋 Creando {cantidad} solicitudes...')
        
        pacientes = list(Usuario.objects.filter(rol='paciente'))
        medicos = list(Usuario.objects.filter(rol='medico'))
        equipos = list(EquipoTrabajo.objects.all())
        tipos_cancer = [
            'mama', 'pulmón', 'colon', 'próstata', 'estómago', 'hígado', 'páncreas',
            'ovario', 'cérvix', 'vejiga', 'riñón', 'leucemia', 'linfoma', 'melanoma',
            'cerebro', 'tiroides', 'esófago', 'intestino', 'seno', 'testicular'
        ]
        
        estadios = ['I', 'II', 'III', 'IV', 'IA', 'IB', 'IIA', 'IIB', 'IIIA', 'IIIB', 'IIIC']
        
        for i in range(cantidad):
            paciente = random.choice(pacientes)
            tipo_cancer = random.choice(tipos_cancer)
            
            # Crear fechas realistas
            fecha_creacion = timezone.make_aware(
                self.fake.date_time_between(
                    start_date='-6M',
                    end_date='now'
                )
            )
            
            solicitud = SolicitudOpinion.objects.create(
                paciente=paciente,
                titulo=f'Solicitud de segunda opinión - {tipo_cancer.title()}',
                descripcion_caso=self.fake.text(max_nb_chars=500),
                diagnostico_inicial=f'Diagnóstico inicial de cáncer de {tipo_cancer}',
                tratamiento_actual=self.fake.text(max_nb_chars=200),
                especialidad_requerida=f'Oncología especializada en {tipo_cancer}',
                prioridad=random.choice(['baja', 'media', 'alta']),
                estado=random.choice(['pendiente', 'asignada', 'en_revision', 'completada']),
                fecha_creacion=fecha_creacion,
                tipo_cancer=tipo_cancer,
                estadio=random.choice(estadios),
                fecha_diagnostico=self.fake.date_between(start_date='-2y', end_date='now'),
                tratamientos_previos=self.fake.text(max_nb_chars=300)
            )
            
            # Asignar médico y equipo si no está pendiente
            if solicitud.estado != 'pendiente':
                # Buscar equipo apropiado
                equipo_apropiado = None
                for equipo in equipos:
                    reglas = equipo.reglas_asignacion.filter(
                        criterio='tipo_cancer',
                        valor__icontains=tipo_cancer,
                        activo=True
                    )
                    if reglas.exists():
                        equipo_apropiado = equipo
                        break
                
                if equipo_apropiado:
                    solicitud.equipo_asignado = equipo_apropiado
                    solicitud.medico_asignado = random.choice(
                        list(equipo_apropiado.miembros.all())
                    )
                else:
                    solicitud.medico_asignado = random.choice(medicos)
                
                solicitud.fecha_asignacion = fecha_creacion + timedelta(
                    hours=random.randint(1, 48)
                )
                
                if solicitud.estado == 'completada':
                    solicitud.fecha_completada = solicitud.fecha_asignacion + timedelta(
                        days=random.randint(1, 10)
                    )
                
                solicitud.save()
            
            if i % 25 == 0:
                self.stdout.write(f'  ✅ Creadas {i+1} solicitudes...')

    def crear_opiniones_medicas(self):
        """Crear opiniones médicas para solicitudes completadas"""
        self.stdout.write('💬 Creando opiniones médicas...')
        
        solicitudes_completadas = SolicitudOpinion.objects.filter(
            estado='completada',
            medico_asignado__isnull=False
        )
        
        for solicitud in solicitudes_completadas:
            if not hasattr(solicitud, 'opinion_medica'):
                OpinionMedica.objects.create(
                    solicitud=solicitud,
                    medico=solicitud.medico_asignado,
                    diagnostico_propuesto=self.fake.text(max_nb_chars=400),
                    recomendaciones=self.fake.text(max_nb_chars=600),
                    tratamiento_sugerido=self.fake.text(max_nb_chars=400),
                    comentarios_adicionales=self.fake.text(max_nb_chars=300),
                    requiere_seguimiento=random.choice([True, False])
                )
        
        self.stdout.write(f'  ✅ Creadas {solicitudes_completadas.count()} opiniones médicas')

    def crear_calificaciones(self):
        """Crear calificaciones para opiniones médicas"""
        self.stdout.write('⭐ Creando calificaciones...')
        
        opiniones = OpinionMedica.objects.all()
        
        for opinion in opiniones:
            if not hasattr(opinion, 'calificacion') and random.choice([True, False]):
                Calificacion.objects.create(
                    opinion=opinion,
                    paciente=opinion.solicitud.paciente,
                    puntuacion=random.randint(3, 5),
                    comentario=self.fake.text(max_nb_chars=200)
                )
        
        calificaciones_creadas = Calificacion.objects.count()
        self.stdout.write(f'  ✅ Creadas {calificaciones_creadas} calificaciones')

    def crear_seguimientos(self):
        """Crear seguimientos para opiniones que lo requieren"""
        self.stdout.write('📅 Creando seguimientos...')
        
        opiniones_con_seguimiento = OpinionMedica.objects.filter(
            requiere_seguimiento=True
        )
        
        for opinion in opiniones_con_seguimiento:
            # Crear 1-3 seguimientos
            num_seguimientos = random.randint(1, 3)
            
            for i in range(num_seguimientos):
                Seguimiento.objects.create(
                    opinion=opinion,
                    medico=opinion.medico,
                    observaciones=self.fake.text(max_nb_chars=300)
                )
        
        seguimientos_creados = Seguimiento.objects.count()
        self.stdout.write(f'  ✅ Creados {seguimientos_creados} seguimientos')

    def crear_chats_equipo(self):
        """Crear chats y mensajes para equipos"""
        self.stdout.write('💬 Creando chats de equipo...')
        
        equipos = EquipoTrabajo.objects.all()
        
        for equipo in equipos:
            # Crear canal general
            canal, created = CanalChat.objects.get_or_create(
                equipo=equipo,
                nombre=f'Chat General - {equipo.nombre}',
                defaults={
                    'descripcion': f'Canal de comunicación general del equipo {equipo.nombre}'
                }
            )
            
            if created:
                # Crear algunos mensajes
                miembros = list(equipo.miembros.all())
                
                if miembros:
                    for _ in range(random.randint(5, 15)):
                        autor = random.choice(miembros)
                        fecha_mensaje = timezone.make_aware(
                            self.fake.date_time_between(
                                start_date='-30d',
                                end_date='now'
                            )
                        )
                        
                        MensajeChat.objects.create(
                            canal=canal,
                            usuario=autor,
                            contenido=self.fake.text(max_nb_chars=200),
                            fecha_envio=fecha_mensaje,
                            leido=random.choice([True, False])
                        )
        
        self.stdout.write(f'  ✅ Creados chats para {equipos.count()} equipos')

    def mostrar_estadisticas(self):
        """Mostrar estadísticas finales"""
        self.stdout.write('\n📊 ESTADÍSTICAS FINALES:')
        self.stdout.write('=' * 50)
        
        stats = [
            ('Usuarios totales', Usuario.objects.count()),
            ('Pacientes', Usuario.objects.filter(rol='paciente').count()),
            ('Médicos', Usuario.objects.filter(rol='medico').count()),
            ('Administradores', Usuario.objects.filter(rol='admin').count()),
            ('Especialidades', EspecialidadOncologica.objects.count()),
            ('Equipos de trabajo', EquipoTrabajo.objects.count()),
            ('Solicitudes', SolicitudOpinion.objects.count()),
            ('Opiniones médicas', OpinionMedica.objects.count()),
            ('Calificaciones', Calificacion.objects.count()),
            ('Seguimientos', Seguimiento.objects.count()),
            ('Canales de chat', CanalChat.objects.count()),
            ('Mensajes', MensajeChat.objects.count()),
            ('Tipos de documento', TipoDocumento.objects.count()),
            ('Reglas de asignación', AsignacionAutomatica.objects.count()),
        ]
        
        for nombre, cantidad in stats:
            self.stdout.write(f'  {nombre}: {cantidad}')
        
        self.stdout.write('\n🎉 ¡Base de datos poblada exitosamente!')
        self.stdout.write('\n🔐 CREDENCIALES DE ACCESO:')
        self.stdout.write('  👑 Admin: admin / admin123')
        self.stdout.write('  👨‍⚕️ Médicos: medico001, medico002, etc. / medico123')
        self.stdout.write('  🏥 Pacientes: paciente001, paciente002, etc. / paciente123')
