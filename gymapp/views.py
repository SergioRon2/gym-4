import os
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
import numpy as np
from .models import Usuario_gym
from django.urls import reverse_lazy, reverse
from .models import Usuario_gym, Asistencia, Planes_gym
from django.utils import timezone
from datetime import datetime
from .forms import AsistenciaForm
from django.http import HttpResponseRedirect, HttpResponseServerError, JsonResponse
from pyzbar.pyzbar import decode
import pytz
from PIL import Image
import cv2
from dateutil import parser
from calendar import monthrange
import urllib.parse
from django.db.models import DateField
from django.db.models.functions import Trunc
from bootstrap_datepicker_plus.widgets import DatePickerInput
from django.contrib.auth.decorators import login_required
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models import Sum
from django.db.models import Count
from django.db.models import F


class Logueo(LoginView):
    template_name= 'gymapp/login.html'
    fields= '__all__'
    redirect_authenticated_user= True
    
    def get_success_url(self):
        return reverse_lazy('plan')



@login_required(login_url='login')
def app(request):
    id_usuario = request.GET.get('codigo')
    # usuario_obj = Usuario_gym.objects.filter(id_usuario=id_usuario).first()
    bogota_tz = pytz.timezone('America/Bogota')

    # Obtiene la fecha y hora actual en la zona horaria de Bogotá
    fecha_actual_bogota = datetime.now(bogota_tz).date()


    fecha_actual_bogota = datetime.now(bogota_tz).date
    asistencia_form = AsistenciaForm(initial={'id_usuario': id_usuario, 'fecha': fecha_actual_bogota})

    

    # Procesar el formulario de asistencia si se envió
    if request.method == 'POST':
        asistencia_form = AsistenciaForm(data=request.POST)

        if asistencia_form.is_valid():
            asistencia_form.save()
            # aviso
            return redirect(reverse('app') + '?ok')
        else:
            # error
            return redirect(reverse('app') + '?error')

    return render(request, 'gymapp/index.html', {'form': asistencia_form})


@login_required(login_url='login')
def usuario(request):   
    usuarios = Usuario_gym.objects.all()
    return render(request, 'gymapp/usuarios.html', {"usuarios":usuarios})


class NuevoUsuario(LoginRequiredMixin,CreateView):
    model = Usuario_gym
    fields = '__all__'
    template_name= 'gymapp/nuevo_usuario.html'
    success_url = reverse_lazy('plan')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['fecha_inicio_gym'].widget = DatePickerInput(format='%Y-%m-%d')
        return form


class EditarUsuario(LoginRequiredMixin,UpdateView):
    model = Usuario_gym
    fields = '__all__'
    template_name= 'gymapp/nuevo_usuario.html'
    success_url = reverse_lazy('plan')    


class DetalleUsuario(LoginRequiredMixin,DetailView):
    model = Usuario_gym
    context_object_name= 'detalle' 
    template_name= 'gymapp/detalle_usuario.html'

class EliminarUsuario(LoginRequiredMixin,DeleteView):
    model= Usuario_gym
    context_object_name= 'usuario'
    template_name= 'gymapp/eliminar_usuario.html'
    success_url= reverse_lazy('plan')
    
    

@login_required(login_url='login')
def lector(request):
    
    if request.method == 'POST' and request.FILES['imagen']:
        imagen = request.FILES['imagen']

        # Haz lo que necesites con la imagen, por ejemplo, guardarla en el servidor.
        
        qr_data = decode(cv2.imdecode(np.frombuffer(imagen.read(), np.uint8), -1))
        
        if qr_data:
            # Si se encontró un código QR en la imagen
            codigo_qr = qr_data[0].data.decode('utf-8')
            print(f'Imagen recibida y procesada correctamente. Código QR: {codigo_qr}')
            # Ruta a la carpeta media
            ruta_carpeta_media = "C:\\Users\\Shino\\Documents\\misentornos\\gym\\gym\\media\\gymapp" 
            
            usuario = Usuario_gym.objects.filter(id_usuario=codigo_qr).first()
            nombre_usuario = usuario.nombre  # Obtén el nombre del usuario
            apellido_usuario = usuario.apellido  # Obtén el apellido del usuario si es necesario
            full_name = nombre_usuario + ' ' + apellido_usuario
            # Iterar a través de los archivos en la carpeta media
            for nombre_archivo in os.listdir(ruta_carpeta_media):
                ruta_completa_archivo = os.path.join(ruta_carpeta_media, nombre_archivo)
                numero_archivo = decode(cv2.imread(ruta_completa_archivo))
                if numero_archivo and numero_archivo[0].data.decode('utf-8') == codigo_qr:
                    # El número decodificado del archivo coincide con el número del código QR
                    print(f"Se encontró un archivo coincidente: {ruta_completa_archivo}")
                    # Realiza las operaciones adicionales que necesites con el archivo encontrado
                    # mensaje = f'Imagen recibida y procesada correctamente. Código QR: {codigo_qr}'
                    response_data = {
                        'success': True,  # Puedes cambiar esto a False si hay algún error
                        'mensaje': 'Imagen procesada correctamente.',  # Tu mensaje de éxito o error
                        'codigo': codigo_qr,
                        'name':full_name,
                        # Nombre de la URL a la que deseas redirigir al usuario
                        }

                    # Devuelve los datos como JSON
                    return JsonResponse(response_data)
                    # return JsonResponse({'success': True, 'mensaje': mensaje})

            mensaje = 'No se encontró un archivo coincidente en la carpeta media.'
            return JsonResponse({'success': False, 'mensaje': mensaje})

        else:
            # Si no se encontró un código QR en la imagen
            print('No se encontró un código QR en la imagen.')
            return JsonResponse({'success': False, 'mensaje': 'No se encontró un código QR en la imagen.'})

    # Si es una solicitud GET, simplemente renderiza la página HTML
    return render(request, 'gymapp/qr.html')

@login_required(login_url='login')
def lista_asistencia(request):
    fecha_param = request.GET.get('fecha')
    id_usuario_param = request.GET.get('id_usuario')

    asistencias = Asistencia.objects.all()

    # Filtrar por fecha si se proporciona una fecha válida
    if fecha_param:
        try:
            fecha = parser.parse(fecha_param).date()
            asistencias = asistencias.filter(fecha=fecha)
        except ValueError:
            return render(request, 'error.html', {'mensaje': 'Formato de fecha inválido'})

    # Filtrar por id_usuario si se proporciona un ID válido
    if id_usuario_param:
        asistencias = asistencias.filter(usuario__id_usuario=id_usuario_param)

    # Obtener fechas únicas de la base de datos y ordenarlas en orden descendente
    fechas = (
        Asistencia.objects.annotate(date=Trunc('fecha', 'day', output_field=DateField()))
        .values('date')
        .distinct()
        .order_by('-date')
    )
    

    return render(request, 'gymapp/asistencia.html', {'asistencias': asistencias, 'fechas': fechas, 'fecha_seleccionada': fecha_param, 'id_usuario': id_usuario_param})

# calculando tiempo de plan
@login_required(login_url='login')
def plan(request):
    usuarios = Usuario_gym.objects.all()
    tarjetas = []

    for usuario in usuarios:
        # Calcula la diferencia en días entre la fecha actual y la fecha de finalización del plan
        dias_restantes = (usuario.fecha_fin - datetime.now().date()).days

        # Verifica si el usuario tiene de 0 a 31 días restantes en su plan
        if -365 <= dias_restantes <= 365:
            tarjeta = {
                'usuario': usuario,
                'dias_restantes': dias_restantes
            }
            tarjetas.append(tarjeta)

    # Ordena las tarjetas de menor a mayor días restantes
    tarjetas_ordenadas = sorted(tarjetas, key=lambda x: x['dias_restantes'])

    return render(request, 'gymapp/plan.html', {'tarjetas': tarjetas_ordenadas})

@login_required(login_url='login')
def ganancias_mensuales(request):
    usuarios = Usuario_gym.objects.all()
    tarjetas = []

    # Calcular el valor total de los planes
    total_valor_plan = Usuario_gym.objects.aggregate(Sum('plan__precio'))['plan__precio__sum']

    for usuario in usuarios:
        # Calcula la diferencia en días entre la fecha actual y la fecha de finalización del plan
        dias_restantes = (usuario.fecha_fin - datetime.now().date()).days

        # Verifica si el usuario tiene de 0 a 31 días restantes en su plan
        if -365 <= dias_restantes <= 365:
            tarjeta = {
                'usuario': usuario,
                'dias_restantes': dias_restantes
            }
            tarjetas.append(tarjeta)

    # Ordena las tarjetas de menor a mayor días restantes
    tarjetas_ordenadas = sorted(tarjetas, key=lambda x: x['dias_restantes'])

    return render(request, 'gymapp/ganancias_mensuales.html', {'tarjetas': tarjetas_ordenadas, 'total_valor_plan': total_valor_plan})

