from django import forms
from .models import Asistencia, Usuario_gym, Articulo, Planes_gym

class AsistenciaForm(forms.ModelForm):
    id_usuario = forms.CharField(label='Número de ID', required=True)

    class Meta:
        model = Asistencia
        fields = ['id_usuario', 'fecha', 'presente']

    def clean_id_usuario(self):
        id_usuario = self.cleaned_data['id_usuario']
        usuario_obj = Usuario_gym.objects.filter(id_usuario=id_usuario).first()

        if not usuario_obj:
            raise forms.ValidationError('No se encontró un usuario con este número de ID.')

        # Establece el valor del campo 'usuario' en el modelo Asistencia
        self.instance.usuario = usuario_obj

        return id_usuario
    

class PlanesForm(forms.ModelForm):
    class Meta:
        model = Planes_gym
        fields = ['tipo_plan', 'precio', 'dias']


class ArticuloForm(forms.ModelForm):
    class Meta:
        model = Articulo
        fields = ['nombre', 'descripcion', 'precio', 'cantidad_disponible']