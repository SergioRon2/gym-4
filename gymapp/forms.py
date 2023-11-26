from django import forms
from .models import Asistencia, Usuario_gym

from django import forms
from .models import Asistencia, Usuario_gym

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
