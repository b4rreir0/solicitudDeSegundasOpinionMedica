from django.core.management.base import BaseCommand
from django.db import transaction
from equipos.models import EspecialidadOncologica, EquipoTrabajo, MiembroEquipo, AsignacionAutomatica
from usuarios.models import Usuario, PerfilMedico


class Command(BaseCommand):
    help = 'Poblar datos de ejemplo para especialidades oncológicas y equipos de trabajo'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando poblado de datos oncológicos...'))
        
        with transaction.atomic():
            # Crear especialidades oncológicas
            self.crear_especialidades()
            
            # Crear médicos de ejemplo
            self.crear_medicos_ejemplo()
            
            # Crear equipos de trabajo
            self.crear_equipos_trabajo()
            
            # Crear reglas de asignación automática
            self.crear_reglas_asignacion()
        
        self.stdout.write(self.style.SUCCESS('✅ Datos oncológicos creados exitosamente!'))

    def crear_especialidades(self):
        """Crear especialidades oncológicas"""
        self.stdout.write('Creando especialidades oncológicas...')
        
        especialidades = [
            {
                'nombre': 'Oncología de Mama',
                'descripcion': 'Especialidad dedicada al diagnóstico y tratamiento del cáncer de mama',
                'icono': 'fas fa-ribbon'
            },
            {
                'nombre': 'Oncología Pulmonar',
                'descripcion': 'Especialidad enfocada en el tratamiento del cáncer de pulmón',
                'icono': 'fas fa-lungs'
            },
            {
                'nombre': 'Oncología Gastrointestinal',
                'descripcion': 'Tratamiento de cánceres del sistema digestivo',
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
                'descripcion': 'Tratamiento de cánceres de la piel',
                'icono': 'fas fa-hand-paper'
            },
            {
                'nombre': 'Neuro-oncología',
                'descripcion': 'Especialidad en tumores del sistema nervioso',
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

    def crear_medicos_ejemplo(self):
        """Crear médicos de ejemplo"""
        self.stdout.write('Creando médicos de ejemplo...')
        
        medicos = [
            {
                'username': 'dr_rodriguez',
                'first_name': 'Carlos',
                'last_name': 'Rodríguez',
                'email': 'carlos.rodriguez@hospital.com',
                'especialidad': 'Oncología de Mama',
                'numero_colegiado': 'COL001',
                'años_experiencia': 15,
                'hospital': 'Hospital Nacional de Oncología'
            },
            {
                'username': 'dra_martinez',
                'first_name': 'María',
                'last_name': 'Martínez',
                'email': 'maria.martinez@hospital.com',
                'especialidad': 'Oncología Pulmonar',
                'numero_colegiado': 'COL002',
                'años_experiencia': 12,
                'hospital': 'Centro de Cáncer Pulmonar'
            },
            {
                'username': 'dr_lopez',
                'first_name': 'Juan',
                'last_name': 'López',
                'email': 'juan.lopez@hospital.com',
                'especialidad': 'Oncología Gastrointestinal',
                'numero_colegiado': 'COL003',
                'años_experiencia': 18,
                'hospital': 'Instituto de Gastroenterología'
            },
            {
                'username': 'dra_garcia',
                'first_name': 'Ana',
                'last_name': 'García',
                'email': 'ana.garcia@hospital.com',
                'especialidad': 'Oncología Ginecológica',
                'numero_colegiado': 'COL004',
                'años_experiencia': 14,
                'hospital': 'Hospital de la Mujer'
            },
            {
                'username': 'dr_sanchez',
                'first_name': 'Pedro',
                'last_name': 'Sánchez',
                'email': 'pedro.sanchez@hospital.com',
                'especialidad': 'Oncología Hematológica',
                'numero_colegiado': 'COL005',
                'años_experiencia': 16,
                'hospital': 'Centro de Hematología'
            },
            {
                'username': 'dr_fernandez',
                'first_name': 'Luis',
                'last_name': 'Fernández',
                'email': 'luis.fernandez@hospital.com',
                'especialidad': 'Oncología Urológica',
                'numero_colegiado': 'COL006',
                'años_experiencia': 13,
                'hospital': 'Hospital Urológico'
            },
            {
                'username': 'dra_jimenez',
                'first_name': 'Carmen',
                'last_name': 'Jiménez',
                'email': 'carmen.jimenez@hospital.com',
                'especialidad': 'Oncología Dermatológica',
                'numero_colegiado': 'COL007',
                'años_experiencia': 11,
                'hospital': 'Centro Dermatológico'
            },
            {
                'username': 'dr_ruiz',
                'first_name': 'Francisco',
                'last_name': 'Ruiz',
                'email': 'francisco.ruiz@hospital.com',
                'especialidad': 'Neuro-oncología',
                'numero_colegiado': 'COL008',
                'años_experiencia': 17,
                'hospital': 'Instituto Neurológico'
            }
        ]
        
        for medico_data in medicos:
            usuario, created = Usuario.objects.get_or_create(
                username=medico_data['username'],
                defaults={
                    'first_name': medico_data['first_name'],
                    'last_name': medico_data['last_name'],
                    'email': medico_data['email'],
                    'rol': 'medico',
                    'is_staff': True,
                    'is_active': True
                }
            )
            
            if created:
                usuario.set_password('medico123')
                usuario.save()
                
                # Crear perfil médico
                PerfilMedico.objects.create(
                    usuario=usuario,
                    numero_colegiado=medico_data['numero_colegiado'],
                    especialidad=medico_data['especialidad'],
                    años_experiencia=medico_data['años_experiencia'],
                    hospital_clinica=medico_data['hospital'],
                    activo=True
                )
                
                self.stdout.write(f'  ✅ Dr. {usuario.first_name} {usuario.last_name} - {medico_data["especialidad"]}')

    def crear_equipos_trabajo(self):
        """Crear equipos de trabajo multidisciplinarios"""
        self.stdout.write('Creando equipos de trabajo...')
        
        equipos = [
            {
                'nombre': 'Equipo Multidisciplinario de Mama',
                'especialidad': 'Oncología de Mama',
                'descripcion': 'Equipo especializado en el diagnóstico y tratamiento integral del cáncer de mama',
                'coordinador': 'dr_rodriguez',
                'miembros': ['dr_rodriguez']
            },
            {
                'nombre': 'Equipo de Oncología Pulmonar',
                'especialidad': 'Oncología Pulmonar',
                'descripcion': 'Equipo dedicado al manejo integral del cáncer de pulmón',
                'coordinador': 'dra_martinez',
                'miembros': ['dra_martinez']
            },
            {
                'nombre': 'Equipo Gastrointestinal',
                'especialidad': 'Oncología Gastrointestinal',
                'descripcion': 'Equipo especializado en cánceres del sistema digestivo',
                'coordinador': 'dr_lopez',
                'miembros': ['dr_lopez']
            },
            {
                'nombre': 'Equipo de Oncología Ginecológica',
                'especialidad': 'Oncología Ginecológica',
                'descripcion': 'Equipo dedicado a cánceres del sistema reproductor femenino',
                'coordinador': 'dra_garcia',
                'miembros': ['dra_garcia']
            },
            {
                'nombre': 'Equipo de Hematología Oncológica',
                'especialidad': 'Oncología Hematológica',
                'descripcion': 'Equipo especializado en cánceres hematológicos',
                'coordinador': 'dr_sanchez',
                'miembros': ['dr_sanchez']
            },
            {
                'nombre': 'Equipo Uro-oncológico',
                'especialidad': 'Oncología Urológica',
                'descripcion': 'Equipo dedicado a cánceres del sistema genitourinario',
                'coordinador': 'dr_fernandez',
                'miembros': ['dr_fernandez']
            },
            {
                'nombre': 'Equipo de Oncología Dermatológica',
                'especialidad': 'Oncología Dermatológica',
                'descripcion': 'Equipo especializado en cánceres de la piel',
                'coordinador': 'dra_jimenez',
                'miembros': ['dra_jimenez']
            },
            {
                'nombre': 'Equipo de Neuro-oncología',
                'especialidad': 'Neuro-oncología',
                'descripcion': 'Equipo dedicado a tumores del sistema nervioso',
                'coordinador': 'dr_ruiz',
                'miembros': ['dr_ruiz']
            }
        ]
        
        for equipo_data in equipos:
            try:
                especialidad = EspecialidadOncologica.objects.get(nombre=equipo_data['especialidad'])
                coordinador = Usuario.objects.get(username=equipo_data['coordinador'])
                
                equipo, created = EquipoTrabajo.objects.get_or_create(
                    nombre=equipo_data['nombre'],
                    defaults={
                        'especialidad': especialidad,
                        'descripcion': equipo_data['descripcion'],
                        'coordinador': coordinador,
                        'activo': True
                    }
                )
                
                if created:
                    # Agregar miembros al equipo
                    for username in equipo_data['miembros']:
                        usuario = Usuario.objects.get(username=username)
                        rol = 'coordinador' if username == equipo_data['coordinador'] else 'oncologo'
                        
                        MiembroEquipo.objects.create(
                            equipo=equipo,
                            usuario=usuario,
                            rol_en_equipo=rol,
                            activo=True
                        )
                    
                    self.stdout.write(f'  ✅ {equipo.nombre}')
                    
            except Exception as e:
                self.stdout.write(f'  ❌ Error creando equipo {equipo_data["nombre"]}: {str(e)}')

    def crear_reglas_asignacion(self):
        """Crear reglas de asignación automática"""
        self.stdout.write('Creando reglas de asignación automática...')
        
        reglas = [
            # Reglas por tipo de cáncer
            {'equipo': 'Equipo Multidisciplinario de Mama', 'criterio': 'tipo_cancer', 'valor': 'mama', 'prioridad': 1},
            {'equipo': 'Equipo Multidisciplinario de Mama', 'criterio': 'tipo_cancer', 'valor': 'seno', 'prioridad': 1},
            
            {'equipo': 'Equipo de Oncología Pulmonar', 'criterio': 'tipo_cancer', 'valor': 'pulmón', 'prioridad': 1},
            {'equipo': 'Equipo de Oncología Pulmonar', 'criterio': 'tipo_cancer', 'valor': 'pulmonar', 'prioridad': 1},
            
            {'equipo': 'Equipo Gastrointestinal', 'criterio': 'tipo_cancer', 'valor': 'colon', 'prioridad': 1},
            {'equipo': 'Equipo Gastrointestinal', 'criterio': 'tipo_cancer', 'valor': 'estómago', 'prioridad': 1},
            {'equipo': 'Equipo Gastrointestinal', 'criterio': 'tipo_cancer', 'valor': 'intestino', 'prioridad': 1},
            {'equipo': 'Equipo Gastrointestinal', 'criterio': 'tipo_cancer', 'valor': 'hígado', 'prioridad': 1},
            {'equipo': 'Equipo Gastrointestinal', 'criterio': 'tipo_cancer', 'valor': 'páncreas', 'prioridad': 1},
            
            {'equipo': 'Equipo de Oncología Ginecológica', 'criterio': 'tipo_cancer', 'valor': 'ovario', 'prioridad': 1},
            {'equipo': 'Equipo de Oncología Ginecológica', 'criterio': 'tipo_cancer', 'valor': 'cérvix', 'prioridad': 1},
            {'equipo': 'Equipo de Oncología Ginecológica', 'criterio': 'tipo_cancer', 'valor': 'útero', 'prioridad': 1},
            {'equipo': 'Equipo de Oncología Ginecológica', 'criterio': 'tipo_cancer', 'valor': 'endometrio', 'prioridad': 1},
            
            {'equipo': 'Equipo de Hematología Oncológica', 'criterio': 'tipo_cancer', 'valor': 'leucemia', 'prioridad': 1},
            {'equipo': 'Equipo de Hematología Oncológica', 'criterio': 'tipo_cancer', 'valor': 'linfoma', 'prioridad': 1},
            {'equipo': 'Equipo de Hematología Oncológica', 'criterio': 'tipo_cancer', 'valor': 'mieloma', 'prioridad': 1},
            
            {'equipo': 'Equipo Uro-oncológico', 'criterio': 'tipo_cancer', 'valor': 'próstata', 'prioridad': 1},
            {'equipo': 'Equipo Uro-oncológico', 'criterio': 'tipo_cancer', 'valor': 'vejiga', 'prioridad': 1},
            {'equipo': 'Equipo Uro-oncológico', 'criterio': 'tipo_cancer', 'valor': 'riñón', 'prioridad': 1},
            
            {'equipo': 'Equipo de Oncología Dermatológica', 'criterio': 'tipo_cancer', 'valor': 'melanoma', 'prioridad': 1},
            {'equipo': 'Equipo de Oncología Dermatológica', 'criterio': 'tipo_cancer', 'valor': 'piel', 'prioridad': 1},
            
            {'equipo': 'Equipo de Neuro-oncología', 'criterio': 'tipo_cancer', 'valor': 'cerebro', 'prioridad': 1},
            {'equipo': 'Equipo de Neuro-oncología', 'criterio': 'tipo_cancer', 'valor': 'neurológico', 'prioridad': 1},
            {'equipo': 'Equipo de Neuro-oncología', 'criterio': 'tipo_cancer', 'valor': 'glioma', 'prioridad': 1},
            
            # Reglas por especialidad
            {'equipo': 'Equipo Multidisciplinario de Mama', 'criterio': 'especialidad', 'valor': 'mama', 'prioridad': 2},
            {'equipo': 'Equipo de Oncología Pulmonar', 'criterio': 'especialidad', 'valor': 'pulmonar', 'prioridad': 2},
            {'equipo': 'Equipo Gastrointestinal', 'criterio': 'especialidad', 'valor': 'gastrointestinal', 'prioridad': 2},
            {'equipo': 'Equipo de Oncología Ginecológica', 'criterio': 'especialidad', 'valor': 'ginecológica', 'prioridad': 2},
            {'equipo': 'Equipo de Hematología Oncológica', 'criterio': 'especialidad', 'valor': 'hematológica', 'prioridad': 2},
            {'equipo': 'Equipo Uro-oncológico', 'criterio': 'especialidad', 'valor': 'urológica', 'prioridad': 2},
            {'equipo': 'Equipo de Oncología Dermatológica', 'criterio': 'especialidad', 'valor': 'dermatológica', 'prioridad': 2},
            {'equipo': 'Equipo de Neuro-oncología', 'criterio': 'especialidad', 'valor': 'neurológica', 'prioridad': 2},
        ]
        
        for regla_data in reglas:
            try:
                equipo = EquipoTrabajo.objects.get(nombre=regla_data['equipo'])
                
                regla, created = AsignacionAutomatica.objects.get_or_create(
                    equipo=equipo,
                    criterio=regla_data['criterio'],
                    valor=regla_data['valor'],
                    defaults={
                        'prioridad': regla_data['prioridad'],
                        'activo': True
                    }
                )
                
                if created:
                    self.stdout.write(f'  ✅ {equipo.nombre} - {regla_data["criterio"]}: {regla_data["valor"]}')
                    
            except Exception as e:
                self.stdout.write(f'  ❌ Error creando regla: {str(e)}')
