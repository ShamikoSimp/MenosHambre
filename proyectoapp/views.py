from django.urls import reverse
from django.conf import settings
import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from functools import wraps
from .models import Usuario, UsuarioNormal, Organizacion, Publicacion, Beneficiario, Donacion, DonacionMonetaria
from .forms import UsuarioForm, UsuarioNormalForm, OrganizacionForm, AccesoForm, PublicacionForm, BeneficiarioForm, DonacionForm, DonacionMonetariaForm
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import UsuarioSerializer, UsuarioNormalSerializer, OrganizacionSerializer, PublicacionSerializer
from .audio_logger import registrar_lectura, obtener_todas_las_lecturas, obtener_lecturas_por_publicacion

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('id_usuario'):
            messages.error(request, "Debe iniciar sesión para acceder a esta página.")
            return redirect('acceso')
        if not request.session.get('es_admin'):
            messages.error(request, "Acceso denegado. Se requieren permisos de administrador.")
            return redirect('inicio')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@admin_required
def admin_gestion(request):
    # Obtener todas las publicaciones ordenadas por fecha
    publicaciones = Publicacion.objects.all().order_by('-fecha_publicacion')
    # Obtener información adicional de los usuarios
    usuarios = {u.id_usuario: u for u in Usuario.objects.all()}
    usuarios_normales = {un.id_usuario_id: un for un in UsuarioNormal.objects.all()}
    organizaciones = {org.id_usuario_id: org for org in Organizacion.objects.all()}
    
    # Enriquecer los datos de las publicaciones
    for pub in publicaciones:
        pub.autor = usuarios.get(pub.id_usuario_id)
        if pub.autor.tipo_usuario == 'usuario':
            pub.autor_detalle = usuarios_normales.get(pub.autor.id_usuario)
        elif pub.autor.tipo_usuario == 'organizacion':
            pub.autor_detalle = organizaciones.get(pub.autor.id_usuario)
    
    return render(request, 'templatesApp/AdminGestion.html', {
        'publicaciones': publicaciones
    })

@admin_required
def historial_lecturas(request):
    """
    Vista para que administradores vean el historial de lecturas de texto a voz.
    """
    lecturas = obtener_todas_las_lecturas()
    
    # Enriquecer con información de usuarios si está disponible
    for lectura in lecturas:
        if lectura.get('id_usuario'):
            try:
                usuario = Usuario.objects.get(id_usuario=lectura['id_usuario'])
                lectura['usuario_email'] = usuario.email
                lectura['tipo_usuario'] = usuario.tipo_usuario
            except Usuario.DoesNotExist:
                lectura['usuario_email'] = 'Usuario eliminado'
    
    # Ordenar por timestamp descendente (más recientes primero)
    lecturas.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    
    return render(request, 'templatesApp/HistorialLecturas.html', {
        'lecturas': lecturas,
        'total_lecturas': len(lecturas)
    })

def eliminar_publicacion(request, id_publicacion):
    if not request.session.get('id_usuario'):
        return redirect('acceso')
    
    # Si es admin, puede eliminar cualquier publicación
    if request.session.get('es_admin'):
        publicacion = get_object_or_404(Publicacion, id_publicacion=id_publicacion)
    else:
        # Si no es admin, solo puede eliminar sus propias publicaciones
        publicacion = get_object_or_404(Publicacion, id_publicacion=id_publicacion, id_usuario=request.session['id_usuario'])
    
    if request.method == 'POST':
        publicacion.delete()
        messages.success(request, '¡Publicación eliminada!')
        
        # Redirigir a admin_gestion si es admin, sino a gestion normal
        if request.session.get('es_admin'):
            return redirect('admin_gestion')
    return redirect('gestion')


def editar_publicacion(request, id_publicacion):
    if not request.session.get('id_usuario'):
        return redirect('acceso')
    
    # Si es admin, puede editar cualquier publicación
    if request.session.get('es_admin'):
        publicacion = get_object_or_404(Publicacion, id_publicacion=id_publicacion)
    else:
        # Si no es admin, solo puede editar sus propias publicaciones
        publicacion = get_object_or_404(Publicacion, id_publicacion=id_publicacion, id_usuario=request.session['id_usuario'])
    
    if request.method == 'POST':
        publicacion.titulo = request.POST.get('titulo')
        publicacion.descripcion = request.POST.get('descripcion')
        publicacion.direccion = request.POST.get('direccion')
        publicacion.save()
        messages.success(request, '¡Publicación actualizada!')
        
        # Redirigir a admin_gestion si es admin, sino a gestion normal
        if request.session.get('es_admin'):
            return redirect('admin_gestion')
    return redirect('gestion')

def gestion(request):
    if not request.session.get('id_usuario'):
        return redirect('acceso')
    publicaciones = Publicacion.objects.filter(id_usuario=request.session['id_usuario']).order_by('-fecha_publicacion')
    return render(request, 'templatesApp/Gestion.html', {
        'publicaciones': publicaciones
    })

# Vista para mostrar datos del usuario y opción de cerrar sesión
def usuario(request):
    if not request.session.get('id_usuario'):
        return redirect('acceso')
    usuario = None
    usuario_normal = None
    organizacion = None
    try:
        usuario = Usuario.objects.get(id_usuario=request.session['id_usuario'])
        # Cargar datos según tipo de usuario
        if usuario.tipo_usuario == 'usuario':
            try:
                usuario_normal = UsuarioNormal.objects.get(id_usuario=usuario)
            except UsuarioNormal.DoesNotExist:
                usuario_normal = None
        elif usuario.tipo_usuario == 'organizacion':
            try:
                organizacion = Organizacion.objects.get(id_usuario=usuario)
            except Organizacion.DoesNotExist:
                organizacion = None
    except Usuario.DoesNotExist:
        usuario = None

    return render(request, 'templatesApp/Usuario.html', {
        'usuario': usuario,
        'usuario_normal': usuario_normal,
        'organizacion': organizacion,
    })

# Vista para cerrar sesión
def cerrar_sesion(request):
    request.session.flush()
    return redirect('inicio')



def inicio(request):
    usuarios = UsuarioNormal.objects.select_related('id_usuario').all()
    publicaciones = Publicacion.objects.all().order_by('-fecha_publicacion')
    return render(request, 'templatesApp/Inicio.html', {
        'usuarios': usuarios,
        'publicaciones': publicaciones
    })


def publicaciones_view(request):
    """Página pública para listar publicaciones (sin filtros por comuna)."""
    # Recuperar todas las publicaciones sin aplicar filtros
    publicaciones = Publicacion.objects.all().order_by('-fecha_publicacion')

    return render(request, 'templatesApp/Publicaciones.html', {
        'publicaciones': publicaciones,
    })


def beneficiarios_view(request):
    """Página para que organizaciones vean y creen beneficiarios.
    Solo accesible para usuarios registrados como organizaciones.
    """
    if not request.session.get('id_usuario'):
        messages.error(request, "Debes iniciar sesión para acceder a esta página.")
        return redirect('acceso')
    
    usuario = Usuario.objects.get(id_usuario=request.session['id_usuario'])
    
    # Verificar que el usuario sea una organización
    if usuario.tipo_usuario != 'organizacion':
        messages.error(request, "Solo las organizaciones pueden acceder a esta página.")
        return redirect('inicio')
    
    # Obtener todos los beneficiarios
    beneficiarios = Beneficiario.objects.all().order_by('nombre')
    
    form = BeneficiarioForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        beneficiario = form.save(commit=False)
        beneficiario.id_usuario_registrador = usuario
        beneficiario.save()
        messages.success(request, '¡Beneficiario añadido correctamente!')
        return redirect('beneficiarios')
    
    return render(request, 'templatesApp/Beneficiarios.html', {
        'beneficiarios': beneficiarios,
        'form': form,
    })


def tipopublicacion(request):
    return render(request, "templatesApp/tipoPublicacion.html")


def publicar(request):
    tipo_usuario = request.GET.get('usuario') 
    tipo_publicacion = request.GET.get('tipo_publicacion') or request.GET.get('tipo') or ''  
    form = PublicacionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        publicacion = form.save(commit=False)
        if request.session.get('id_usuario'):
            publicacion.id_usuario = Usuario.objects.get(id_usuario=request.session['id_usuario'])
            publicacion.tipo_publicacion = tipo_publicacion
            publicacion.fecha_publicacion = timezone.now().date()
            publicacion.save()
            messages.success(request, '¡Publicación realizada con éxito!')
            return redirect('inicio')
        else:
            messages.error(request, 'Debes iniciar sesión para publicar.')
    return render(request, "templatesApp/Publicar.html", {
        'form': form,
        'tipo_usuario': tipo_usuario,
        'tipo_publicacion': tipo_publicacion
    })


def registro(request):
    tipo = request.GET.get("tipo")  

    if tipo not in ["usuario", "organizacion"]:
        messages.error(request, "Debes seleccionar un tipo de registro válido.")
        return render(request, "templatesApp/Registro.html", {"tipo": None})

    if request.method == "POST":
        usuario_form = UsuarioForm(request.POST)

        normal_form = UsuarioNormalForm(request.POST) if tipo == "usuario" else UsuarioNormalForm()
        org_form = OrganizacionForm(request.POST) if tipo == "organizacion" else OrganizacionForm()

        if usuario_form.is_valid():
            usuario = usuario_form.save(commit=False)
            usuario.tipo_usuario = tipo
            # La contraseña se hasheará automáticamente en el save() del modelo
            usuario.save()


            if tipo == "usuario" and normal_form.is_valid():
                normal = normal_form.save(commit=False)
                normal.id_usuario = usuario
                normal.save()
                messages.success(request, "Usuario registrado correctamente.")
                return redirect("inicio")

            elif tipo == "organizacion" and org_form.is_valid():
                organizacion = org_form.save(commit=False)
                organizacion.id_usuario = usuario
                organizacion.save()
                messages.success(request, "Organización registrada correctamente.")
                return redirect("inicio")

            else:
                usuario.delete()
                messages.error(request, "Error en los datos del formulario.")

        else:
            messages.error(request, "Error en el formulario de usuario.")

    else:
        usuario_form = UsuarioForm()
        normal_form = UsuarioNormalForm()
        org_form = OrganizacionForm()

    return render(request, "templatesApp/Registro.html", {
        "tipo": tipo,
        "usuario_form": usuario_form,
        "normal_form": normal_form,
        "org_form": org_form,
    })




def acceso(request):
    form = AccesoForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            email = form.cleaned_data["email"]
            contrasena = form.cleaned_data["contrasena"]
            try:
                usuario = Usuario.objects.get(email=email)
                if usuario.check_password(contrasena):
                    # Almacenar información básica del usuario en la sesión
                    request.session['id_usuario'] = usuario.id_usuario
                    request.session['email'] = usuario.email
                    request.session['es_admin'] = usuario.es_admin
                    request.session['tipo_usuario'] = usuario.tipo_usuario
                    # Preparar un nombre para mostrar en la navbar
                    display_name = usuario.email
                    try:
                        if usuario.tipo_usuario == 'usuario':
                            un = UsuarioNormal.objects.get(id_usuario=usuario)
                            display_name = f"{un.nombre} {un.apellido}".strip()
                        elif usuario.tipo_usuario == 'organizacion':
                            org = Organizacion.objects.get(id_usuario=usuario)
                            display_name = org.razon_social or usuario.email
                        elif usuario.es_admin:
                            # intentar mostrar nombre si existe en UsuarioNormal
                            try:
                                un = UsuarioNormal.objects.get(id_usuario=usuario)
                                display_name = f"{un.nombre} {un.apellido}".strip()
                            except UsuarioNormal.DoesNotExist:
                                display_name = usuario.email
                    except Exception:
                        # En caso de cualquier error, fallback al email
                        display_name = usuario.email
                    request.session['display_name'] = display_name
                    
                    # Mensaje personalizado según el tipo de usuario
                    if usuario.es_admin:
                        messages.success(request, "Bienvenido Administrador.")
                    else:
                        messages.success(request, "Acceso exitoso. Bienvenido.")
                    
                    return redirect("inicio")
                else:
                    form.add_error("contrasena", "Contraseña incorrecta.")
            except Usuario.DoesNotExist:
                form.add_error("email", "No existe una cuenta con este email.")
    return render(request, "templatesApp/Acceder.html", {"form": form})


def donacion(request):
    """Vista para manejar donaciones alimenticias y monetarias."""
    if not request.session.get('id_usuario'):
        messages.error(request, "Debes iniciar sesión para realizar una donación.")
        return redirect('acceso')
    
    tipo_donacion = request.POST.get('tipo_donacion') or request.GET.get('tipo_donacion') or 'alimenticia'
    usuario = Usuario.objects.get(id_usuario=request.session['id_usuario'])
    
    if request.method == 'POST':
        if tipo_donacion == 'alimenticia':
            form = DonacionForm(request.POST)
            if form.is_valid():
                donacion_obj = form.save(commit=True)
                messages.success(request, '¡Donación alimenticia registrada exitosamente!')
                return redirect('inicio')
        elif tipo_donacion == 'monetaria':
            form = DonacionMonetariaForm(request.POST)
            if form.is_valid():
                donacion_monetaria = form.save(commit=False)
                donacion_monetaria.id_usuario = usuario
                donacion_monetaria.save()
                messages.success(request, '¡Donación monetaria registrada exitosamente!')
                return redirect('inicio')
    else:
        if tipo_donacion == 'alimenticia':
            form = DonacionForm()
        else:
            form = DonacionMonetariaForm()
    
    return render(request, 'templatesApp/donacion.html', {
        'form': form,
        'tipo_donacion': tipo_donacion
    })

@api_view(['GET','POST'])
def usuario_list(request):
    if request.method == 'GET':
        usuarios = Usuario.objects.all()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = UsuarioSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'PUT', 'DELETE'])
def usuario_detail(request, pk):
    try:
        usuario = Usuario.objects.get(pk=pk)
    except Usuario.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data)
    
    if request.method == 'PUT':
        serializer = UsuarioSerializer(usuario, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE':
        usuario.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
@api_view(['GET','POST'])
def publicacion_list(request):
    if request.method == 'GET':
        publicaciones = Publicacion.objects.all()
        serializer = PublicacionSerializer(publicaciones, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = PublicacionSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'PUT', 'DELETE'])
def publicacion_detail(request, pk):
    try:
        publicacion = Publicacion.objects.get(pk=pk)
    except Publicacion.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = PublicacionSerializer(publicacion)
        return Response(serializer.data)
    
    if request.method == 'PUT':
        serializer = PublicacionSerializer(publicacion, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE':
        publicacion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

def login_usuario(request):
    usuario = authenticate(email='admin@gmail.com', password='admin')
    if usuario:
        login(request, usuario)
        return HttpResponse("Inicio de sesion exitoso")
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ver_datos_admin(request):
    if request.user.rol == 'admin':
        return Response({'mensaje': 'Tienes acceso total al sistema'})
    return Response({'error': 'No tienes acceso total al sistema'})

def leer_publicacion(request, id_publicacion):
    try:
        publicacion = Publicacion.objects.get(id_publicacion=id_publicacion)
    except Publicacion.DoesNotExist:
        return HttpResponse("Publicación no encontrada", status=404)
    # Validar que la API key de VoiceRSS esté configurada
    voicerss_key = getattr(settings, 'VOICERSS_API_KEY', None)
    if not voicerss_key:
        return HttpResponse("VoiceRSS no está configurado", status=500)

    # Texto a leer: título + descripción + dirección (si existe)
    partes = []
    if getattr(publicacion, 'titulo', None):
        partes.append(str(publicacion.titulo).strip())
    if getattr(publicacion, 'descripcion', None):
        partes.append(str(publicacion.descripcion).strip())
    # Agregar dirección con etiqueta para mejorar claridad en la lectura
    if getattr(publicacion, 'direccion', None):
        direccion = str(publicacion.direccion).strip()
        if direccion:
            partes.append(f"Dirección: {direccion}")
    # Agregar comuna si está disponible
    if getattr(publicacion, 'comuna', None):
        comuna = str(publicacion.comuna).strip()
        if comuna:
            partes.append(f"Comuna: {comuna}")

    texto = ". ".join(partes)

    # Llamada a VoiceRSS
    url = "https://api.voicerss.org/"
    params = {
        "key": voicerss_key,
        "hl": "es-mx",      # voz en español (México soportado por VoiceRSS)
        "src": texto,       # texto a hablar
        "c": "MP3"          # Formato de audio
    }

    try:
        response = requests.get(url, params=params, timeout=10)
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Error conectando con VoiceRSS: {str(e)}", status=500)

    # VoiceRSS devuelve texto cuando hay error ("ERROR something...")
    if response.content.startswith(b"ERROR"):
        error_msg = response.content.decode('utf-8', errors='ignore')
        return HttpResponse(f"Error en VoiceRSS: {error_msg}", status=500)

    # Registrar la lectura en JSON (sin bloquear si hay error)
    id_usuario = request.session.get('id_usuario')
    registrar_lectura(
        id_publicacion=id_publicacion,
        titulo=publicacion.titulo,
        texto=texto,
        id_usuario=id_usuario
    )

    return HttpResponse(response.content, content_type="audio/mpeg")