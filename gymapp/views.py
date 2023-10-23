import base64
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
import numpy as np
from .models import Usuario_gym
from django.urls import reverse_lazy, reverse
from .models import Usuario_gym, Asistencia
from django.utils import timezone
from .forms import AsistenciaForm
from django.http import HttpResponseRedirect, HttpResponseServerError, JsonResponse
from pyzbar.pyzbar import decode
from PIL import Image
import cv2
import urllib.parse
class Logueo(LoginView):
    template_name= 'gymapp/login.html'
    fields= '__all__'
    redirect_authenticated_user= True
    
    def get_success_url(self):
        return reverse_lazy('app')

def app(request):
    asistencia_form= AsistenciaForm()


    # Procesar el formulario de asistencia si se envió
    if request.method == 'POST':
        asistencia_form= AsistenciaForm(data=request.POST)
    
        if asistencia_form.is_valid():
            asistencia_form.save()
            #aviso 
            return redirect(reverse('app')+'?ok')

        else:
            #error
            return redirect(reverse('app')+'?error')

    #
    return render(request, 'gymapp/index.html',{'form': asistencia_form})
    
def usuario(request):
    usuarios = Usuario_gym.objects.all()
    return render(request, 'gymapp/usuarios.html', {"usuarios":usuarios})

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
                        'redireccionar': reverse('app'),  # Nombre de la URL a la que deseas redirigir al usuario
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