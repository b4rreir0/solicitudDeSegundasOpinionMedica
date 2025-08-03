from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Limpia completamente la base de datos eliminando todos los datos'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--confirmar',
            action='store_true',
            help='Confirma que quieres eliminar todos los datos (requerido)',
        )
    
    def handle(self, *args, **options):
        if not options['confirmar']:
            self.stdout.write(
                self.style.WARNING(
                    'ADVERTENCIA: Este comando eliminará TODOS los datos de la base de datos.\n'
                    'Para confirmar, ejecuta el comando con --confirmar'
                )
            )
            return
        
        # Confirmar una vez más
        self.stdout.write(
            self.style.WARNING(
                '¿Estás seguro de que quieres eliminar TODOS los datos?\n'
                'Esta acción NO se puede deshacer.'
            )
        )
        
        confirm = input('Escribe "CONFIRMAR" para continuar: ')
        if confirm != 'CONFIRMAR':
            self.stdout.write(self.style.ERROR('Operación cancelada.'))
            return
        
        try:
            # Obtener la ruta de la base de datos SQLite
            db_path = settings.DATABASES['default']['NAME']
            
            # Verificar si el archivo existe
            if os.path.exists(db_path):
                # Cerrar todas las conexiones
                connection.close()
                
                # Eliminar el archivo de la base de datos
                os.remove(db_path)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Base de datos eliminada exitosamente: {db_path}'
                    )
                )
                
                # Recrear la base de datos con las migraciones
                self.stdout.write(
                    self.style.WARNING(
                        'Ejecutando migraciones para recrear la base de datos...'
                    )
                )
                
                # Importar y ejecutar el comando migrate
                from django.core.management import call_command
                call_command('migrate')
                
                self.stdout.write(
                    self.style.SUCCESS(
                        'Base de datos recreada exitosamente con todas las tablas vacías.'
                    )
                )
                
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'El archivo de base de datos no existe: {db_path}'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error al limpiar la base de datos: {str(e)}'
                )
            )
