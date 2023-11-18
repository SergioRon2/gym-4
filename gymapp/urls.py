from django.contrib import admin
from django.urls import path
from gymapp import views
from django.contrib.auth.views import LogoutView
from .views import obtener_csrf_token

urlpatterns = [
    # path('login/', views.Logueo.as_view(), name='login'),
    # path('logout/',LogoutView.as_view(next_page='login'), name='logout'),
    path('', views.app, name='app'),
    path('login/', views.Logueo.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'),name='logout'),
    path('usuarios/', views.usuario, name='usuarios'),
    path('lector/',views.lector, name='lector'),
    path('asistencias/', views.lista_asistencia, name='lista_asistencias'),
    path('plan/', views.plan, name='plan'),
    path('nuevo_usuario/', views.NuevoUsuario.as_view(), name='nuevo_usuario'),
    path('detalle/<int:pk>', views.DetalleUsuario.as_view(), name='detalle'),
    path('editar/<int:pk>', views.EditarUsuario.as_view(), name='editar'),
    path('eliminar/<int:pk>', views.EliminarUsuario.as_view(), name='eliminar'),
    path('ganancia/', views.ganancias_mensuales, name='ganancia'),
    path('obtener-csrf-token/', obtener_csrf_token, name='obtener_csrf_token'),

]
