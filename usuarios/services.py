from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import Group
from django.utils.crypto import get_random_string
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
from .models import Usuario, PerfilMedico, CodigoVerificacion
from django.utils import timezone
from datetime import timedelta
import string
import random


class UsuarioRegistrationService:
    """Servicio para el registro de usuarios y envío de credenciales por email"""
    
    @staticmethod
    def generar_password_temporal():
        """Genera una contraseña temporal aleatoria"""
        caracteres = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(random.choice(caracteres) for _ in range(12))
    
    @staticmethod
    def generar_username_unico(email):
        """Genera un username único basado en el email"""
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        
        while Usuario.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        return username
    
    @staticmethod
    def crear_paciente_por_medico(medico, email_paciente, nombre_completo=None):
        """
        Crea una cuenta de paciente por solicitud de un médico
        
        Args:
            medico: Usuario médico que solicita la creación
            email_paciente: Email del paciente
            nombre_completo: Nombre completo del paciente (opcional)
        
        Returns:
            dict: Resultado de la operación
        """
        try:
            # Validar que el médico tenga permisos
            if medico.rol != 'medico':
                return {
                    'success': False,
                    'error': 'Solo los médicos pueden crear cuentas de pacientes'
                }
            
            # Verificar que el médico tiene perfil activo
            if not hasattr(medico, 'perfil_medico') or not medico.perfil_medico.activo:
                return {
                    'success': False,
                    'error': 'El médico no tiene un perfil activo'
                }
            
            # Verificar que el email no esté registrado
            if Usuario.objects.filter(email=email_paciente).exists():
                return {
                    'success': False,
                    'error': 'Ya existe un usuario con este email'
                }
            
            # Generar datos del usuario
            username = UsuarioRegistrationService.generar_username_unico(email_paciente)
            password_temporal = UsuarioRegistrationService.generar_password_temporal()
            
            # Separar nombre y apellido si se proporciona
            first_name = ''
            last_name = ''
            if nombre_completo:
                nombres = nombre_completo.strip().split()
                if nombres:
                    first_name = nombres[0]
                    if len(nombres) > 1:
                        last_name = ' '.join(nombres[1:])
            
            # Crear usuario
            usuario = Usuario.objects.create_user(
                username=username,
                email=email_paciente,
                password=password_temporal,
                first_name=first_name,
                last_name=last_name,
                rol='paciente'
            )
            
            # Enviar email con credenciales
            resultado_email = UsuarioRegistrationService.enviar_credenciales_email(
                usuario, 
                password_temporal, 
                medico
            )
            
            if not resultado_email['success']:
                # Si falla el envío del email, eliminar el usuario creado
                usuario.delete()
                return resultado_email
            
            return {
                'success': True,
                'usuario': usuario,
                'mensaje': f'Cuenta creada exitosamente para {email_paciente}. Se han enviado las credenciales por email.'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al crear la cuenta: {str(e)}'
            }
    
    @staticmethod
    def enviar_credenciales_email(usuario, password_temporal, medico_creador):
        """
        Envía las credenciales por email al usuario recién creado
        
        Args:
            usuario: Usuario creado
            password_temporal: Contraseña temporal
            medico_creador: Médico que solicitó la creación
        
        Returns:
            dict: Resultado del envío
        """
        try:
            # Preparar contexto para el template
            contexto = {
                'usuario': usuario,
                'password_temporal': password_temporal,
                'medico_creador': medico_creador,
                'login_url': settings.BASE_URL + reverse('login') if hasattr(settings, 'BASE_URL') else reverse('login'),
                'sitio_nombre': 'Sistema de Solicitudes Médicas',
            }
            
            # Renderizar template HTML
            mensaje_html = render_to_string('emails/credenciales_usuario.html', contexto)
            mensaje_texto = strip_tags(mensaje_html)
            
            # Enviar email
            send_mail(
                subject='Credenciales de acceso - Sistema de Solicitudes Médicas',
                message=mensaje_texto,
                html_message=mensaje_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.email],
                fail_silently=False,
            )
            
            return {
                'success': True,
                'mensaje': 'Email enviado exitosamente'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al enviar email: {str(e)}'
            }
    
    @staticmethod
    def reenviar_credenciales(usuario_id, medico_solicitante):
        """
        Reenvía las credenciales y genera nueva contraseña temporal
        
        Args:
            usuario_id: ID del usuario
            medico_solicitante: Médico que solicita el reenvío
        
        Returns:
            dict: Resultado de la operación
        """
        try:
            # Validar permisos
            if medico_solicitante.rol != 'medico':
                return {
                    'success': False,
                    'error': 'Solo los médicos pueden reenviar credenciales'
                }
            
            # Obtener usuario
            usuario = Usuario.objects.get(id=usuario_id, rol='paciente')
            
            # Generar nueva contraseña temporal
            nueva_password = UsuarioRegistrationService.generar_password_temporal()
            usuario.set_password(nueva_password)
            usuario.save()
            
            # Enviar email
            resultado_email = UsuarioRegistrationService.enviar_credenciales_email(
                usuario, 
                nueva_password, 
                medico_solicitante
            )
            
            return resultado_email
            
        except Usuario.DoesNotExist:
            return {
                'success': False,
                'error': 'Usuario no encontrado'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al reenviar credenciales: {str(e)}'
            }
