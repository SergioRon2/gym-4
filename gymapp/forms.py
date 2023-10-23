from django import forms
from .models import Asistencia


class AsistenciaForm(forms.ModelForm):
    id_usuario= forms.IntegerField(disabled=True, required=False)
    class Meta:
        model= Asistencia
        fields = '__all__'
        
