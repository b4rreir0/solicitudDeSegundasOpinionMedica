# solicitudDeSegundasOpinionMedica

Sistema de solicitud de segundas opiniones médicas desarrollado con Django - Un proyecto para facilitar la solicitud y gestión de segundas opiniones médicas.

## Descripción

Este proyecto tiene como objetivo crear una plataforma que permita a los pacientes solicitar segundas opiniones médicas de manera eficiente y organizada, utilizando Django como framework principal tanto para el backend como para el frontend.

## Características

- **Gestión de usuarios**: Sistema de autenticación con roles (paciente, médico, administrador)
- **Solicitudes de opiniones médicas**: Creación, seguimiento y gestión de solicitudes
- **Perfiles médicos**: Gestión de especialidades y información profesional
- **Documentos médicos**: Subida, gestión y descarga de documentos
- **Sistema de calificaciones**: Evaluación de las opiniones médicas
- **Seguimiento de casos**: Historial y seguimiento de cada caso
- **API REST**: Endpoints para integración con aplicaciones frontend

## Tecnologías utilizadas

- **Backend**: Django 5.2.4
- **API**: Django REST Framework
- **Base de datos**: SQLite (desarrollo)
- **Autenticación**: Django Authentication + Token Authentication
- **Archivos**: Gestión de archivos con Django FileField
- **CORS**: django-cors-headers para integración frontend

## Estructura del proyecto

```
solicitud_medica/
├── usuarios/           # Aplicación de gestión de usuarios
├── opiniones_medicas/  # Aplicación de opiniones médicas
├── documentos/         # Aplicación de gestión de documentos
├── solicitud_medica/   # Configuración principal del proyecto
├── media/              # Archivos subidos
├── static/             # Archivos estáticos
└── manage.py
```

## Instalación

### Prerrequisitos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de instalación

```bash
# Clonar el repositorio
git clone https://github.com/b4rreir0/solicitudDeSegundasOpinionMedica.git

# Navegar al directorio del proyecto
cd solicitudDeSegundasOpinionMedica

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
# Crear archivo .env basado en .env.example

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor de desarrollo
python manage.py runserver
```

## Uso

### Acceso al admin
- URL: http://localhost:8000/admin/
- Usar las credenciales del superusuario creado

### API Endpoints

#### Usuarios
- `GET/POST /api/usuarios/usuarios/` - Listar/crear usuarios
- `POST /api/usuarios/auth/login/` - Iniciar sesión
- `POST /api/usuarios/auth/register/` - Registrar usuario
- `GET /api/usuarios/auth/profile/` - Perfil del usuario

#### Opiniones Médicas
- `GET/POST /api/opiniones/solicitudes/` - Listar/crear solicitudes
- `GET/POST /api/opiniones/opiniones/` - Listar/crear opiniones
- `GET/POST /api/opiniones/calificaciones/` - Listar/crear calificaciones

#### Documentos
- `GET/POST /api/documentos/documentos/` - Listar/crear documentos
- `POST /api/documentos/upload/` - Subir documento
- `GET /api/documentos/download/<id>/` - Descargar documento

### Roles de usuario

1. **Paciente**: Puede crear solicitudes, subir documentos, calificar opiniones
2. **Médico**: Puede revisar solicitudes, emitir opiniones, hacer seguimiento
3. **Administrador**: Acceso completo al sistema

### Desarrollo

```bash
# Crear nuevas migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Ejecutar tests
python manage.py test

# Recopilar archivos estáticos
python manage.py collectstatic
```

## Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la licencia MIT - ver el archivo LICENSE para más detalles.

## Contacto

b4rreir0 - GitHub Profile
