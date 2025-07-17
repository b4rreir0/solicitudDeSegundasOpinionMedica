from rest_framework import serializers
from .models import Usuario, PerfilMedico


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Usuario"""
    
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'rol', 
                 'telefono', 'fecha_nacimiento', 'direccion', 'fecha_creacion', 'is_active']
        read_only_fields = ['id', 'fecha_creacion']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class PerfilMedicoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo PerfilMedico"""
    
    usuario = UsuarioSerializer(read_only=True)
    
    class Meta:
        model = PerfilMedico
        fields = '__all__'
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']


class UsuarioCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear usuarios"""
    
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'rol']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuario.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
