from django.db import migrations
from django.contrib.auth.models import User

def crear_superusuario(apps, schema_editor):
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="Admin1234!"
        )

class Migration(migrations.Migration):

    dependencies = [
        ('proyectoapp', '000X_nombre_migracion_anterior'),  # Ajusta esto
    ]

    operations = [
        migrations.RunPython(crear_superusuario),
    ]
