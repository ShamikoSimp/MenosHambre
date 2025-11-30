"""
URL configuration for proyectodb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from proyectoapp import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("tipopublicacion/", views.tipopublicacion, name="tipopublicacion"),
    path("publicar/", views.publicar, name="publicar"),
    path("registro/", views.registro, name="registro"),
    path("acceso/", views.acceso, name="acceso"),
    path("usuario/", views.usuario, name="usuario"),
    path("cerrar_sesion/", views.cerrar_sesion, name="cerrar_sesion"),
    path("gestion/", views.gestion, name="gestion"),
    path("panel-admin/", views.admin_gestion, name="admin_gestion"),
    path("historial-lecturas/", views.historial_lecturas, name="historial_lecturas"),
    path("editar_publicacion/<int:id_publicacion>/", views.editar_publicacion, name="editar_publicacion"),
    path("eliminar_publicacion/<int:id_publicacion>/", views.eliminar_publicacion, name="eliminar_publicacion"),
    path("leer-publicacion/<int:id_publicacion>/", views.leer_publicacion, name="leer_publicacion"),
    path('admin/', admin.site.urls),
    path('usuarios/', views.usuario_list),
    path('usuarios/<int:pk>', views.usuario_detail),
    path('publicaciones/', views.publicacion_list),
    path('publicaciones/<int:pk>', views.publicacion_detail),
    path('publicaciones/list/', views.publicaciones_view, name='publicaciones'),
    path('beneficiarios/', views.beneficiarios_view, name='beneficiarios'),
    path('ver/', views.ver_datos_admin),
]
