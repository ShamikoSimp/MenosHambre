from django.db import migrations
from django.contrib.auth.models import User

def crear_superusuario(apps, schema_editor):
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="Admin123"
        )

class Migration(migrations.Migration):

    dependencies = [
        ('proyectoapp', '0005_donacion_fecha_donacion_publicacion_hora_and_more.py'),  # Ajusta esto
    ]

    operations = [
        migrations.RunPython(crear_superusuario),
    ]
