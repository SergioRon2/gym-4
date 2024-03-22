from django.urls import path
from gymapp import views
from django.contrib.auth.views import LogoutView
from .views import obtener_csrf_token

urlpatterns = [

    path('', views.app, name='app'),

    path('login/', views.Logueo.as_view(), name='login'),

    path('logout/', LogoutView.as_view(next_page='login'),name='logout'),

    # -------------------------------------------------------------------------------

    path('tipos-id/', views.obtener_tipos_identificaciones, name='tipos-id'),

    # -------------------------------------------------------------------------------

    path('lector/', views.lector, name='lector'),

    path('consulta-asistencia', views.consulta_asistencia, name='consulta-asistencia'),

    path('consulta-asistencia/<int:usuario_id>/', views.consulta_asistencia, name='consulta-asistencia'),

    path('crear-asistencia/', views.crear_asistencia, name='crear_asistencia'),

    path('eliminar-asistencia/<int:asistencia_id>', views.eliminar_asistencia, name='eliminar-asistencia'),

    # -------------------------------------------------------------------------------

    path('plan-usuario/', views.plan_usuario, name='plan'),

    path('plan-usuario/<int:usuario_id>/', views.plan_usuario, name='plan_usuario'),

    # ---------------------------------------------------------------------------------

    path('planes/', views.obtener_planes_gym, name='planes'),

    path('crear-plan/', views.crear_plan, name='crear_plan'),

    path('editar-plan/<int:plan_id>', views.editar_plan, name='editar-plan'),

    path('eliminar-plan/<int:plan_id>', views.eliminar_plan, name='eliminar-plan'),

    # ---------------------------------------------------------------------------------

    path('usuarios/', views.usuario, name='usuarios'),

    path('usuarios/<int:id>', views.usuario, name='usuarios'),

    path('nuevo_usuario/', views.nuevo_usuarioR, name='nuevo_usuario'),

    path('detalle-usuario/<int:pk>', views.DetalleUsuario.as_view(), name='detalle-usuario'),

    path('editar/<int:pk>', views.editar_usuario, name='editar'),

    path('eliminar/<int:pk>', views.EliminarUsuario.as_view(), name='eliminar'),

    # ---------------------------------------------------------------------------------

    path('articulos/', views.obtener_articulos, name='articulos'),

    path('articulos/<int:id>', views.obtener_articulos, name='articulos'),

    path('crear_articulo/', views.crear_articulo, name='crear_articulo'),

    path('actualizar-articulo/<int:id>', views.actualizar_articulo, name='actualizar_articulo'),

    path('eliminar_articulo/<int:pk>', views.eliminar_articulo, name='eliminar_articulo'),

    path('detalle_articulo/<int:pk>', views.DetalleArticulo.as_view(), name='detalle_articulo'),

    # ---------------------------------------------------------------------------------

    path('ganancia/', views.registros_ganancia, name='registros_ganancia'),

    path('obtener-csrf-token/', obtener_csrf_token, name='obtener_csrf_token'),

    path('cantidad-planes-vendidos-por-mes/', views.obtener_cantidad_planes_vendidos_por_mes, name='cantidad_planes_vendidos_por_mes'),

]
