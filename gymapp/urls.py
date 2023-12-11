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

    path('usuarios/<int:id>', views.usuario, name='usuarios'),

    path('obtener_tipos_id/', views.obtener_tipos_identificaciones, name='obtener-tipos-id'),

    path('lector/',views.lector, name='lector'),

    path('asistencias/', views.lista_asistencia, name='lista_asistencias'),
    
    path('plan/', views.plan, name='plan'),

    path('obtener_plan/', views.obtener_planes_gym, name='obtener-plan'),

    path('crear_plan/', views.crear_plan, name='crear_plan'),

    path('plan/<int:usuario_id>/', views.plan, name='plan_usuario'),

    path('nuevo_usuario/', views.nuevo_usuarioR, name='nuevo_usuario'),

    path('detalle/<int:pk>', views.DetalleUsuario.as_view(), name='detalle'),

    path('editar/<int:pk>', views.editar_usuario, name='editar'),

    path('eliminar/<int:pk>', views.EliminarUsuario.as_view(), name='eliminar'),

    path('articulos/', views.obtener_articulos, name='articulos'),

    path('crear_articulo/', views.crear_articulo, name='crear_articulo'),

    path('eliminar_articulo/<int:pk>', views.EliminarArticulo.as_view(), name='eliminar_articulo'), 

    path('detalle_articulo/<int:pk>', views.DetalleArticulo.as_view(), name='detalle_articulo'),

    path('ganancia/', views.registros_ganancia, name='registros_ganancia'),

    path('obtener-csrf-token/', obtener_csrf_token, name='obtener_csrf_token'),

]
