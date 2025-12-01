from django.contrib import admin
from django import forms
from proyectoapp.models import Usuario, Publicacion, UsuarioNormal, Organizacion, Municipalidad

class UsuarioForm(forms.ModelForm):
    """
    Formulario personalizado para el modelo Usuario.
    Permite cambiar la contraseña de forma segura con validación.
    """
    contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'vTextField'}),
        help_text="Introduce una nueva contraseña. Será hasheada automáticamente.",
        required=False,
        label="Contraseña"
    )
    
    class Meta:
        model = Usuario
        fields = '__all__'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # Si se ingresó una contraseña, se actualiza
        if self.cleaned_data['contrasena']:
            user.set_password(self.cleaned_data['contrasena'])
        if commit:
            user.save()
        return user


class UsuarioAdmin(admin.ModelAdmin):
    form = UsuarioForm
    list_display = ['email', 'tipo_usuario', 'es_admin']
    list_filter = ['tipo_usuario', 'es_admin']
    search_fields = ['email']
    fields = ['email', 'contrasena', 'tipo_usuario', 'es_admin']

class UsuarioNormalAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido', 'telefono', 'get_email']
    list_filter = ['nombre', 'apellido']
    search_fields = ['nombre', 'apellido', 'id_usuario__email']
    
    def get_email(self, obj):
        return obj.id_usuario.email
    get_email.short_description = 'Email'

class OrganizacionAdmin(admin.ModelAdmin):
    list_display = ['razon_social', 'rut', 'tipo_entidad', 'get_email']
    list_filter = ['tipo_entidad']
    search_fields = ['razon_social', 'rut', 'id_usuario__email']
    
    def get_email(self, obj):
        return obj.id_usuario.email
    get_email.short_description = 'Email'

class MunicipalidadAdmin(admin.ModelAdmin):
    list_display = ['nombre_municipalidad', 'region', 'comuna', 'get_email']
    list_filter = ['region', 'comuna']
    search_fields = ['nombre_municipalidad', 'region', 'id_usuario__email']
    
    def get_email(self, obj):
        return obj.id_usuario.email
    get_email.short_description = 'Email'

class PublicacionAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo_publicacion', 'direccion', 'fecha_publicacion', 'get_usuario_email']
    list_filter = ['tipo_publicacion', 'fecha_publicacion']
    search_fields = ['titulo', 'descripcion', 'id_usuario__email']
    readonly_fields = ['fecha_publicacion']
    
    def get_usuario_email(self, obj):
        return obj.id_usuario.email
    get_usuario_email.short_description = 'Usuario'

# Register your models here.
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(UsuarioNormal, UsuarioNormalAdmin)
admin.site.register(Organizacion, OrganizacionAdmin)
admin.site.register(Municipalidad, MunicipalidadAdmin)
admin.site.register(Publicacion, PublicacionAdmin)