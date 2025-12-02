from proyectoapp.models import Usuario, UsuarioNormal, Organizacion, Publicacion
from rest_framework import serializers

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

class UsuarioNormalSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioNormal
        fields = '__all__'

class OrganizacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organizacion
        fields = '__all__'

class PublicacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publicacion
        fields = '__all__'

class AudioReadingSerializer(serializers.Serializer):
    id_publicacion = serializers.IntegerField()
    titulo = serializers.CharField()
    texto = serializers.CharField()
    id_usuario = serializers.IntegerField(allow_null=True)
    fecha_hora = serializers.CharField()
    timestamp = serializers.FloatField()