from django.db import migrations
from django.contrib.auth.hashers import make_password

def hash_existing_passwords(apps, schema_editor):
    # Obtener el modelo histórico
    Usuario = apps.get_model('proyectoapp', 'Usuario')
    # Hashear todas las contraseñas existentes
    for usuario in Usuario.objects.all():
        # Guardar la contraseña actual en texto plano
        plain_password = usuario.contrasena
        # Aplicar el hash
        usuario.contrasena = make_password(plain_password)
        usuario.save()

def reverse_passwords(apps, schema_editor):
    # No podemos revertir el hash, así que no hacemos nada
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('proyectoapp', '0002_organizacion_documento_respaldo_and_more'),  # Ajusta esto según tu última migración
    ]

    operations = [
        migrations.RunPython(hash_existing_passwords, reverse_passwords),
    ]