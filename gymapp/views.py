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
from django.middleware.csrf import get_token
import json


class Logueo(LoginView):
    template_name= 'gymapp/login.html'
    fields= '__all__'
    redirect_authenticated_user= True
    
    def get_success_url(self):
        return reverse_lazy('plan')



# @login_required(login_url='login')
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


def obtener_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})


# @login_required(login_url='login')
def usuario(request):
    usuarios = Usuario_gym.objects.all()

    usuarios_lista = []

    for usuario in usuarios:
        usuario_dict = {
            'id' : usuario.id,       #este id es la primary key
            'nombre': usuario.nombre,
            'apellido': usuario.apellido,
            'tipo_id': usuario.tipo_id,
            'id_usuario': usuario.id_usuario
        }
        usuarios_lista.append(usuario_dict)

    return JsonResponse({'usuarios': usuarios_lista})


class NuevoUsuario(CreateView):
    model = Usuario_gym
    fields = '__all__'
    success_url = reverse_lazy('plan')

    def form_valid(self, form):
        # Lógica adicional si es necesario
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            # Guardar el nuevo usuario
            self.object = form.save()

            # Devolver una respuesta JSON indicando éxito y los datos del nuevo usuario
            response_data = {
                'success': True,
                'mensaje': 'Usuario creado correctamente.',
                'usuario': {
                    'id': self.object.id,
                    'nombre': self.object.nombre,
                    'apellido': self.object.apellido,
                    'tipo_id': self.object.tipo_id,
                    'id_usuario': self.object.id_usuario,
                    # Agrega más campos según sea necesario
                }
            }
            return JsonResponse(response_data)
        else:
            # Devolver una respuesta JSON indicando que hubo errores en el formulario
            errors = dict(form.errors.items())
            return JsonResponse({'success': False, 'errors': errors})
        
class EditarUsuario(UpdateView):
    model = Usuario_gym
    fields = '__all__'
    template_name= 'gymapp/nuevo_usuario.html'
    success_url = reverse_lazy('plan')    


class DetalleUsuario(DetailView):
    model = Usuario_gym
    context_object_name= 'detalle' 
    template_name= 'gymapp/detalle_usuario.html'

class EliminarUsuario(DeleteView):
    model = Usuario_gym
    success_url = reverse_lazy('plan')

    def delete(self, request, *args, **kwargs):
        try:
            # Obtén la instancia del usuario que se va a eliminar
            self.object = self.get_object()

            # Puedes agregar lógica adicional antes de eliminar el objeto si es necesario
            # Por ejemplo, verificar si el usuario tiene permisos para eliminar el objeto, etc.

            # Elimina el usuario
            self.object.delete()

            # Devuelve una respuesta JSON indicando que el usuario se eliminó correctamente
            return JsonResponse({'success': True, 'mensaje': 'Usuario eliminado correctamente.'})
        except Exception as e:
            # Devuelve una respuesta JSON indicando un error si la eliminación falla
            return JsonResponse({'success': False, 'error': str(e)})


# @login_required(login_url='login')
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
            current_directory = os.path.dirname(os.path.abspath(__file__))
            ruta_carpeta_media = os.path.join(current_directory, '../media/gymapp') 
            
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

# @login_required(login_url='login')
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
            return JsonResponse({'error': 'Formato de fecha inválido'})

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

    # Convertir queryset a lista de diccionarios para JsonResponse
    asistencias_lista = list(asistencias.values())
    
    return JsonResponse({'asistencias': asistencias_lista, 'fechas': list(fechas), 'fecha_seleccionada': fecha_param, 'id_usuario': id_usuario_param})

# calculando tiempo de plan
# @login_required(login_url='login')
def plan(request):
    usuarios = Usuario_gym.objects.all()
    tarjetas = []

    for usuario in usuarios:
        dias_restantes = (usuario.fecha_fin - datetime.now().date()).days

        if -365 <= dias_restantes <= 365:
            tarjeta = {
                'usuario': {
                    'id' : usuario.id,
                    'nombre': usuario.nombre,
                    'apellido': usuario.apellido,
                    'tipo_id': usuario.tipo_id,
                    'id_usuario': usuario.id_usuario
                },
                'dias_restantes': dias_restantes
            }
            tarjetas.append(tarjeta)

    # Ordena las tarjetas de menor a mayor días restantes
    tarjetas_ordenadas = sorted(tarjetas, key=lambda x: x['dias_restantes'])

    return JsonResponse({'tarjetas': tarjetas_ordenadas})


# @login_required(login_url='login')
def ganancias_mensuales(request):
    usuarios = Usuario_gym.objects.all()
    tarjetas = []

    total_valor_plan = Usuario_gym.objects.aggregate(Sum('plan__precio'))['plan__precio__sum']

    for usuario in usuarios:
        dias_restantes = (usuario.fecha_fin - datetime.now().date()).days

        if -365 <= dias_restantes <= 365:
            tarjeta = {
                'usuario': {
                    'nombre': usuario.nombre,
                    'apellido': usuario.apellido,
                    'tipo_id': usuario.tipo_id,
                    'id': usuario.id_usuario
                },
                'dias_restantes': dias_restantes
            }
            tarjetas.append(tarjeta)

    # Ordena las tarjetas de menor a mayor días restantes
    tarjetas_ordenadas = sorted(tarjetas, key=lambda x: x['dias_restantes'])

    return JsonResponse({'tarjetas': tarjetas_ordenadas, 'total_valor_plan': total_valor_plan})
