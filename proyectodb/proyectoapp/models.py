from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password

class ApoyoBeneficiario(models.Model):
    id_apoyo = models.AutoField(primary_key=True)
    id_beneficiario = models.ForeignKey('Beneficiario', models.DO_NOTHING, db_column='id_beneficiario')
    id_publicacion = models.ForeignKey('Publicacion', models.DO_NOTHING, db_column='id_publicacion', blank=True, null=True)
    tipo_apoyo = models.CharField(max_length=50, blank=True, null=True)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    estado = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
            
        db_table = 'apoyo_beneficiario'


class ApoyoMunicipal(models.Model):
    id_apoyo = models.AutoField(primary_key=True)
    id_publicacion = models.ForeignKey('Publicacion', models.DO_NOTHING, db_column='id_publicacion')
    id_municipalidad = models.ForeignKey('Municipalidad', models.DO_NOTHING, db_column='id_municipalidad')
    tipo_apoyo = models.CharField(max_length=30)
    monto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fecha_apoyo = models.DateField(blank=True, null=True)

    class Meta:
            
        db_table = 'apoyo_municipal'


class Beneficiario(models.Model):
    id_beneficiario = models.AutoField(primary_key=True)
    id_usuario_registrador = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario_registrador')
    id_usuario_cuenta = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario_cuenta', related_name='beneficiario_id_usuario_cuenta_set', blank=True, null=True)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=30, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    comuna = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
            
        db_table = 'beneficiario'


class Campana(models.Model):
    id_campana = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario')
    titulo = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)

    class Meta:
            
        db_table = 'campana'


class Dependiente(models.Model):
    id_dependiente = models.AutoField(primary_key=True)
    id_beneficiario = models.ForeignKey(Beneficiario, models.DO_NOTHING, db_column='id_beneficiario')
    nombre = models.CharField(max_length=100, blank=True, null=True)
    edad = models.IntegerField()
    parentesco = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
            
        db_table = 'dependiente'


class Donacion(models.Model):
    id_donacion = models.AutoField(primary_key=True)
    id_publicacion = models.ForeignKey('Publicacion', models.DO_NOTHING, db_column='id_publicacion')
    nombre_producto = models.CharField(max_length=100)
    cantidad = models.IntegerField(blank=True, null=True)
    unidad_medida = models.CharField(max_length=20, blank=True, null=True)
    fecha_expiracion = models.DateField(blank=True, null=True)
    # Fecha en que se realizó la donación (presente en el diagrama)
    fecha_donacion = models.DateField(blank=True, null=True)

    class Meta:
            
        db_table = 'donacion'


class Municipalidad(models.Model):
    id_usuario = models.OneToOneField('Usuario', models.DO_NOTHING, db_column='id_usuario', primary_key=True)
    nombre_municipalidad = models.CharField(max_length=100)
    region = models.CharField(max_length=50, blank=True, null=True)
    comuna = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
            
        db_table = 'municipalidad'


class Notificacion(models.Model):
    id_notificacion = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario')
    titulo = models.CharField(max_length=100, blank=True, null=True)
    mensaje = models.CharField(max_length=200, blank=True, null=True)
    fecha_envio = models.DateTimeField(blank=True, null=True)
    leido = models.IntegerField(blank=True, null=True)

    class Meta:
            
        db_table = 'notificacion'


class Organizacion(models.Model):
    id_usuario = models.OneToOneField('Usuario', models.DO_NOTHING, db_column='id_usuario', primary_key=True)
    razon_social = models.CharField(max_length=100)
    rut = models.CharField(max_length=15)
    telefono_contacto = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    tipo_entidad = models.CharField(max_length=50, blank=True, null=True)
    documento_respaldo = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
            
        db_table = 'organizacion'


class Publicacion(models.Model):
    id_publicacion = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario')
    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    tipo_publicacion = models.CharField(max_length=30, blank=True, null=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    fecha_publicacion = models.DateField(blank=True, null=True)
    # Campo "Hora" presente en el diagrama ER: opcional para compatibilidad
    hora = models.TimeField(blank=True, null=True)
    documento_respaldo = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
            
        db_table = 'publicacion'


class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    id_beneficiario = models.ForeignKey(Beneficiario, models.DO_NOTHING, db_column='id_beneficiario')
    id_publicacion = models.ForeignKey(Publicacion, models.DO_NOTHING, db_column='id_publicacion')
    fecha_reserva = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
            
        db_table = 'reserva'


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    email = models.CharField(unique=True, max_length=100)
    contrasena = models.CharField(max_length=128)  # Aumentado para almacenar hash
    tipo_usuario = models.CharField(max_length=20, blank=True, null=True)
    es_admin = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self._state.adding or (
            hasattr(self, '_password_changed') and self._password_changed
        ):
            self.contrasena = make_password(self.contrasena)
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        return check_password(raw_password, self.contrasena)

    def set_password(self, raw_password):
        self.contrasena = raw_password
        self._password_changed = True

    class Meta:
        db_table = 'usuario'


class UsuarioNormal(models.Model):
    id_usuario = models.OneToOneField(Usuario, models.DO_NOTHING, db_column='id_usuario', primary_key=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    telefono = models.IntegerField(blank=True, null=True)

    class Meta:
            
        db_table = 'usuario_normal'