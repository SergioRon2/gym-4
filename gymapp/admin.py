from django.contrib import admin
from .models import Usuario_gym, Planes_gym, Asistencia
# Register your models here.
class AsistenciaAdmin(admin.ModelAdmin):
    list_display=('usuario','fecha','presente')
class UsuaioAdmin(admin.ModelAdmin):
    list_display=('nombre','apellido','tipo_id','id_usuario','fecha_inicio_gym','fecha_fin','plan')
    search_fields=('nombre', 'apellido','id_usuario',)

admin.site.register(Usuario_gym,UsuaioAdmin)
admin.site.register(Planes_gym)
admin.site.register(Asistencia, AsistenciaAdmin)