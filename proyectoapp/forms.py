from django import forms
from django.core.exceptions import ValidationError
import re
from .models import Usuario, UsuarioNormal, Organizacion, Publicacion, Beneficiario, Donacion, DonacionMonetaria, Municipalidad, Campana
# --- FORMULARIO PUBLICACION ---
class PublicacionForm(forms.ModelForm):
    class Meta:
        model = Publicacion
        fields = ['titulo', 'descripcion', 'direccion']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
        }

# --- FORMULARIO DE ACCESO ---
class AccesoForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
        label="Email"
    )
    contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
        label="Contraseña"
    )


# --- FORMULARIO BASE USUARIO ---
class UsuarioForm(forms.ModelForm):
    contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'minlength': '8'}),
        label="Contraseña",
        help_text="Mínimo 8 caracteres, 1 mayúscula, 1 minúscula, 1 número y 1 carácter especial."
    )
    confirmar_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'minlength': '8'}),
        label="Confirmar contraseña"
    )

    class Meta:
        model = Usuario
        fields = ['email', 'contrasena']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            # Validar que el email tenga un dominio válido
            if '@' not in email or '.' not in email.split('@')[1]:
                raise ValidationError("Por favor, ingresa un correo electrónico válido con un dominio válido.")
            # Evitar registros duplicados por email (sin distinguir mayúsculas)
            from .models import Usuario
            qs = Usuario.objects.filter(email__iexact=email)
            if self.instance and getattr(self.instance, 'pk', None):
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("Ya existe una cuenta registrada con este correo.")
        return email

    def clean_contrasena(self):
        password = self.cleaned_data.get("contrasena")
        if password:
            # Validar requisitos de contraseña
            if len(password) < 8:
                raise ValidationError("La contraseña debe tener mínimo 8 caracteres.")
            if not re.search(r'[A-Z]', password):
                raise ValidationError("La contraseña debe contener al menos una mayúscula.")
            if not re.search(r'[a-z]', password):
                raise ValidationError("La contraseña debe contener al menos una minúscula.")
            if not re.search(r'[0-9]', password):
                raise ValidationError("La contraseña debe contener al menos un número.")
            if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'\"<>,.?/\\|`~]', password):
                raise ValidationError("La contraseña debe contener al menos un carácter especial (!@#$%^&* etc).")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("contrasena")
        confirmar = cleaned_data.get("confirmar_contrasena")

        if password and confirmar and password != confirmar:
            raise ValidationError("Las contraseñas no coinciden.")
        return cleaned_data


# --- FORMULARIO USUARIO NORMAL ---
class UsuarioNormalForm(forms.ModelForm):
    class Meta:
        model = UsuarioNormal
        fields = ['nombre', 'apellido', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")
        if any(char.isdigit() for char in nombre):
            raise ValidationError("El nombre no puede contener números.")
        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data.get("apellido")
        if any(char.isdigit() for char in apellido):
            raise ValidationError("El apellido no puede contener números.")
        return apellido

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono")
        if telefono:
            # Convertir a string para validar
            telefono_str = str(telefono)
            if len(telefono_str) < 9:
                raise ValidationError("El teléfono debe tener mínimo 9 caracteres.")
            if not telefono_str.isdigit():
                raise ValidationError("El teléfono no puede contener letras, solo números.")
            # Verificar que el teléfono no esté registrado por otro UsuarioNormal
            from .models import UsuarioNormal
            qs = UsuarioNormal.objects.filter(telefono=telefono)
            if self.instance and getattr(self.instance, 'pk', None):
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("El teléfono ya está registrado para otro usuario.")
        return telefono



# --- FORMULARIO ORGANIZACIÓN ---
class OrganizacionForm(forms.ModelForm):
    class Meta:
        model = Organizacion
        fields = ['razon_social', 'rut', 'telefono_contacto', 'direccion', 'tipo_entidad']
        widgets = {
            'razon_social': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'rut': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'telefono_contacto': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'tipo_entidad': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
        }

    def clean_razon_social(self):
        razon_social = self.cleaned_data.get("razon_social")
        if not razon_social or not razon_social.strip():
            raise ValidationError("La razón social no puede quedar vacía.")
        # Verificar duplicado de razón social
        from .models import Organizacion
        qs = Organizacion.objects.filter(razon_social__iexact=razon_social.strip())
        if self.instance and getattr(self.instance, 'pk', None):
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe una organización registrada con esa razón social.")
        return razon_social

    def clean_rut(self):
        rut = self.cleaned_data.get("rut")
        if not rut or not rut.strip():
            raise ValidationError("El RUT no puede quedar vacío.")
        if any(char.isalpha() for char in rut.replace('-', '').replace('.', '')):
            raise ValidationError("El RUT no puede contener letras, solo números y guiones.")
        # Verificar duplicado de RUT
        from .models import Organizacion
        qs = Organizacion.objects.filter(rut__iexact=rut.strip())
        if self.instance and getattr(self.instance, 'pk', None):
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe una organización registrada con ese RUT.")
        return rut

    def clean_telefono_contacto(self):
        telefono = self.cleaned_data.get("telefono_contacto")
        if not telefono or not telefono.strip():
            raise ValidationError("El teléfono no puede quedar vacío.")
        telefono_str = str(telefono).replace(' ', '').replace('-', '')
        if len(telefono_str) < 9:
            raise ValidationError("El teléfono debe tener mínimo 9 caracteres.")
        if not telefono_str.isdigit():
            raise ValidationError("El teléfono no puede contener letras, solo números.")
        # Verificar duplicado de teléfono para organizaciones
        from .models import Organizacion
        qs = Organizacion.objects.filter(telefono_contacto__iexact=str(telefono).strip())
        if self.instance and getattr(self.instance, 'pk', None):
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("El teléfono ya está registrado para otra organización.")
        return telefono

    def clean_direccion(self):
        direccion = self.cleaned_data.get("direccion")
        if not direccion or not direccion.strip():
            raise ValidationError("La dirección no puede quedar vacía.")
        return direccion

    def clean_tipo_entidad(self):
        tipo_entidad = self.cleaned_data.get("tipo_entidad")
        if not tipo_entidad or not tipo_entidad.strip():
            raise ValidationError("El tipo de entidad no puede quedar vacío.")
        if any(char.isdigit() for char in tipo_entidad):
            raise ValidationError("El tipo de entidad no puede contener números.")
        return tipo_entidad


# --- FORMULARIO BENEFICIARIO ---
class BeneficiarioForm(forms.ModelForm):
    class Meta:
        model = Beneficiario
        fields = ['nombre', 'tipo', 'telefono', 'direccion', 'comuna']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'tipo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tipo de beneficio'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'comuna': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comuna'}),
        }


# --- FORMULARIO DONACIÓN ALIMENTICIA ---
class DonacionForm(forms.ModelForm):
    class Meta:
        model = Donacion
        fields = ['nombre_producto', 'cantidad', 'unidad_medida', 'fecha_expiracion', 'fecha_donacion']
        widgets = {
            'nombre_producto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Arroz, Leche, Pan...'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 10', 'step': '0.01'}),
            'unidad_medida': forms.Select(attrs={'class': 'form-select'}),
            'fecha_expiracion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_donacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def clean_nombre_producto(self):
        nombre = self.cleaned_data.get('nombre_producto')
        if not nombre or not nombre.strip():
            raise ValidationError("El nombre del producto no puede quedar vacío.")
        return nombre
    
    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is not None and cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a 0.")
        return cantidad


# --- FORMULARIO DONACIÓN MONETARIA ---
class DonacionMonetariaForm(forms.ModelForm):
    class Meta:
        model = DonacionMonetaria
        fields = ['monto', 'fecha_donacion']
        widgets = {
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 10000', 'step': '100'}),
            'fecha_donacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto is not None and monto <= 0:
            raise ValidationError("El monto debe ser mayor a 0.")
        return monto


# --- FORMULARIO MUNICIPALIDAD ---
class MunicipalidadForm(forms.ModelForm):
    class Meta:
        model = Municipalidad
        fields = ['nombre_municipalidad', 'region', 'comuna']
        widgets = {
            'nombre_municipalidad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la Municipalidad'}),
            'region': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Región'}),
            'comuna': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comuna'}),
        }
    
    def clean_nombre_municipalidad(self):
        nombre = self.cleaned_data.get('nombre_municipalidad')
        if not nombre or not nombre.strip():
            raise ValidationError("El nombre de la municipalidad no puede quedar vacío.")
        # Verificar duplicado por nombre de municipalidad
        from .models import Municipalidad
        qs = Municipalidad.objects.filter(nombre_municipalidad__iexact=nombre.strip())
        if self.instance and getattr(self.instance, 'pk', None):
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe una municipalidad con ese nombre.")
        return nombre
    
    def clean_region(self):
        region = self.cleaned_data.get('region')
        if region and any(char.isdigit() for char in region):
            raise ValidationError("La región no puede contener números.")
        return region
    
    def clean_comuna(self):
        comuna = self.cleaned_data.get('comuna')
        if comuna and any(char.isdigit() for char in comuna):
            raise ValidationError("La comuna no puede contener números.")
        return comuna

# --- FORMULARIO CAMPAÑA ---
class CampanaForm(forms.ModelForm):
    class Meta:
        model = Campana
        fields = ['titulo', 'descripcion', 'fecha_inicio', 'fecha_fin']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la campaña'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción de la campaña', 'rows': 4}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')
        if not titulo or not titulo.strip():
            raise ValidationError("El título de la campaña no puede quedar vacío.")
        return titulo
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise ValidationError("La fecha de fin no puede ser anterior a la fecha de inicio.")
        return cleaned_data
