from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.conf import settings
from .models import Usuario, PerfilMedico


class RegistroPacienteForm(forms.ModelForm):
    """Formulario para el registro de pacientes por parte de los médicos"""
    
    email_medico = forms.EmailField(
        label='Email del Médico',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'medico@ejemplo.com'}),
        help_text='Email del médico que registra al paciente'
    )
    
    confirmar_email = forms.EmailField(
        label='Confirmar Email del Paciente',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'paciente@ejemplo.com'})
    )
    
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefono', 'fecha_nacimiento', 'direccion']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'paciente@ejemplo.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+52 123 456 7890'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dirección completa'}),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Email del Paciente',
            'telefono': 'Teléfono',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'direccion': 'Dirección',
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError('Ya existe un usuario con este email.')
        return email
    
    def clean_confirmar_email(self):
        email = self.cleaned_data.get('email')
        confirmar_email = self.cleaned_data.get('confirmar_email')
        if email and confirmar_email and email != confirmar_email:
            raise ValidationError('Los emails no coinciden.')
        return confirmar_email
    
    def clean_email_medico(self):
        email_medico = self.cleaned_data.get('email_medico')
        try:
            medico = Usuario.objects.get(email=email_medico, rol='medico')
            if not hasattr(medico, 'perfil_medico') or not medico.perfil_medico.activo:
                raise ValidationError('El médico no está activo para registrar pacientes.')
        except Usuario.DoesNotExist:
            raise ValidationError('No existe un médico con este email.')
        return email_medico
    
    def save(self, commit=True):
        # Generar username único basado en el email
        email = self.cleaned_data.get('email')
        username = email.split('@')[0]
        
        # Asegurar que el username sea único
        counter = 1
        original_username = username
        while Usuario.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1
        
        # Crear el usuario
        user = super().save(commit=False)
        user.username = username
        user.rol = 'paciente'
        
        # Generar contraseña aleatoria
        password = get_random_string(12)
        user.set_password(password)
        
        if commit:
            user.save()
            
            # Enviar credenciales por correo electrónico
            self.enviar_credenciales(user, password)
            
            # Notificar al médico
            self.notificar_medico(user)
        
        return user
    
    def enviar_credenciales(self, user, password):
        """Enviar credenciales del paciente por correo electrónico"""
        subject = 'Credenciales de Acceso - Sistema de Solicitud de Segundas Opiniones Médicas'
        
        context = {
            'user': user,
            'password': password,
            'login_url': 'http://localhost:8000/login/',  # Cambiar por la URL real
        }
        
        html_message = render_to_string('emails/credenciales_usuario.html', context)
        plain_message = f"""
        Estimado/a {user.first_name} {user.last_name},

        Se ha creado una cuenta para usted en el Sistema de Solicitud de Segundas Opiniones Médicas.

        Sus credenciales de acceso son:
        Usuario: {user.username}
        Contraseña: {password}

        Puede acceder al sistema en: http://localhost:8000/login/

        Por favor, cambie su contraseña después del primer acceso.

        Saludos cordiales,
        Sistema de Solicitud de Segundas Opiniones Médicas
        """
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
    
    def notificar_medico(self, paciente):
        """Notificar al médico sobre el registro del paciente"""
        email_medico = self.cleaned_data.get('email_medico')
        medico = Usuario.objects.get(email=email_medico)
        
        subject = 'Nuevo Paciente Registrado - Sistema de Solicitud de Segundas Opiniones Médicas'
        
        context = {
            'medico': medico,
            'paciente': paciente,
        }
        
        html_message = render_to_string('emails/notificacion_medico.html', context)
        plain_message = f"""
        Estimado/a Dr. {medico.first_name} {medico.last_name},

        Se ha registrado un nuevo paciente en el sistema:
        
        Nombre: {paciente.first_name} {paciente.last_name}
        Email: {paciente.email}
        Teléfono: {paciente.telefono or 'No especificado'}
        
        El paciente ha recibido sus credenciales de acceso por correo electrónico.

        Saludos cordiales,
        Sistema de Solicitud de Segundas Opiniones Médicas
        """
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [medico.email],
            html_message=html_message,
            fail_silently=False,
        )


class PerfilMedicoForm(forms.ModelForm):
    """Formulario para el perfil del médico"""
    
    class Meta:
        model = PerfilMedico
        fields = ['numero_colegiado', 'especialidad', 'hospital_clinica', 'años_experiencia', 'activo']
        widgets = {
            'numero_colegiado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de colegiado'}),
            'especialidad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Especialidad médica'}),
            'hospital_clinica': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hospital o clínica'}),
            'años_experiencia': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Años de experiencia'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'numero_colegiado': 'Número de Colegiado',
            'especialidad': 'Especialidad',
            'hospital_clinica': 'Hospital o Clínica',
            'años_experiencia': 'Años de Experiencia',
            'activo': 'Activo para Consultas',
        }


class UsuarioUpdateForm(forms.ModelForm):
    """Formulario para actualizar información del usuario"""
    
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefono', 'fecha_nacimiento', 'direccion']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Email',
            'telefono': 'Teléfono',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'direccion': 'Dirección',
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Ya existe un usuario con este email.')
        return email
