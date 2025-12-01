# Menos Hambre - Proyecto

## Configuración del Entorno

### Requisitos Previos
- Python 3.8 o superior
- MySQL
- pip (gestor de paquetes de Python)

### Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd proyectodb
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
pip install requests
```

3. Configurar variables de entorno:
   - Copiar el archivo `.env.example` a `.env`
   - Editar `.env` con tus configuraciones

```bash
cp .env.example .env
# Editar .env con tu editor preferido
```

4. Configurar la base de datos:
```bash
python manage.py migrate
```

5. Crear un superusuario (opcional):
```bash
python manage.py createsuperuser
```

6. Ejecutar el servidor de desarrollo:
```bash
python manage.py runserver
```

### Variables de Entorno

El proyecto usa las siguientes variables de entorno:

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| DJANGO_SECRET_KEY | Clave secreta de Django | Requerido |
| DJANGO_DEBUG | Modo debug | False |
| DJANGO_ALLOWED_HOSTS | Hosts permitidos | localhost,127.0.0.1 |
| DB_NAME | Nombre de la base de datos | menos_hambre |
| DB_USER | Usuario de la base de datos | root |
| DB_PASSWORD | Contraseña de la base de datos | - |
| DB_HOST | Host de la base de datos | localhost |
| DB_PORT | Puerto de la base de datos | 3306 |

### Seguridad

- Las contraseñas se almacenan usando hashing seguro
- CSRF protection activado
- Configuraciones de seguridad de cookies implementadas
- Variables sensibles en archivos .env (no incluidos en el control de versiones)

### Desarrollo

1. Crear una rama para tus cambios:
```bash
git checkout -b feature/tu-feature
```

2. Hacer commit de tus cambios:
```bash
git add .
git commit -m "Descripción de tus cambios"
```

3. Enviar cambios a GitHub:
```bash
git push origin feature/tu-feature
```

### Notas Importantes

- No compartir el archivo `.env` con credenciales reales
- Mantener `DEBUG = False` en producción
- Usar HTTPS en producción
- Actualizar regularmente las dependencias