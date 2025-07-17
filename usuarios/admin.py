from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, PerfilMedico


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Configuración del admin para el modelo Usuario"""
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_active', 'fecha_creacion')
    list_filter = ('rol', 'is_active', 'is_staff', 'fecha_creacion')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': ('rol', 'telefono', 'fecha_nacimiento', 'direccion')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {
            'fields': ('rol', 'telefono', 'fecha_nacimiento', 'direccion')
        }),
    )


@admin.register(PerfilMedico)
class PerfilMedicoAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo PerfilMedico"""
    
    list_display = ('usuario', 'numero_colegiado', 'especialidad', 'hospital_clinica', 'años_experiencia', 'activo')
    list_filter = ('especialidad', 'activo', 'fecha_creacion')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'numero_colegiado', 'especialidad')
    
    fieldsets = (
        ('Información del Médico', {
            'fields': ('usuario', 'numero_colegiado', 'especialidad')
        }),
        ('Información Profesional', {
            'fields': ('hospital_clinica', 'años_experiencia', 'activo')
        }),
    )
