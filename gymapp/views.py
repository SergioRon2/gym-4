import os
from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView
from django.forms.models import model_to_dict
import numpy as np
from django.urls import reverse_lazy, reverse
from .models import DetalleVenta, Usuario_gym, Planes_gym, Asistencia, Articulo, RegistroGanancia
from datetime import datetime
from .forms import AsistenciaForm, ArticuloForm, PlanesForm
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from pyzbar.pyzbar import decode
import pytz
import cv2
from django.db.models import DateField, Count
from django.db.models.functions import Trunc
from django.middleware.csrf import get_token
import json
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from decimal import Decimal


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
def usuario(request, id=None):
    if id:
        # Si se proporciona un ID, obtenemos ese usuario específico
        usuario = get_object_or_404(Usuario_gym, id=id)
        usuario_dict = {
            'id': usuario.id,
            'nombre': usuario.nombre,
            'apellido': usuario.apellido,
            'tipo_id': usuario.tipo_id,
            'id_usuario': usuario.id_usuario,
            'codigo_qr_url': usuario.codigo_qr.url if usuario.codigo_qr else None
        }
        return JsonResponse({'usuario': usuario_dict})
    else:
        # Si no se proporciona un ID, devolvemos la lista de todos los usuarios
        usuarios = Usuario_gym.objects.all()
        usuarios_lista = [
            {
                'id': usuario.id,
                'nombre': usuario.nombre,
                'apellido': usuario.apellido,
                'tipo_id': usuario.tipo_id,
                'id_usuario': usuario.id_usuario,
                'codigo_qr_url': usuario.codigo_qr.url if usuario.codigo_qr else None
            }
            for usuario in usuarios
        ]
        return JsonResponse({'usuarios': usuarios_lista})



def obtener_tipos_identificaciones(request):
    
    tipos_id_posibles = dict(Usuario_gym.tipos_id_choice)

    # Construir la lista de todos los tipos de identificación posibles
    data = [{'tipo_id': value} for value in tipos_id_posibles]

    # Devolver la respuesta JSON
    return JsonResponse({'tipos_id': data})




class NuevoUsuario(CreateView): 
    model = Usuario_gym
    fields = '__all__'
    success_url = reverse_lazy('plan')

# La vista basada en funciones sigue siendo útil si necesitas una API específica
@csrf_exempt
def nuevo_usuarioR(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        print("Datos recibidos:", data)

        tipo_plan = data.get('plan')

        if tipo_plan:
            try:
                # Intenta obtener una instancia de Planes_gym según el tipo proporcionado
                plan_instance = Planes_gym.objects.get(tipo_plan=tipo_plan)
            except Planes_gym.DoesNotExist:
                # Manejar el caso cuando el tipo de plan no existe en la base de datos
                print(f'Tipo de plan inválido: {tipo_plan}')
                return JsonResponse({'success': False, 'mensaje': 'Tipo de plan inválido.'})

            # Obtener la fecha_inicio_gym del JSON
            fecha_inicio_gym_str = data.get('fecha_inicio_gym')

            # Verificar que la fecha_inicio_gym_str tiene un valor válido
            if fecha_inicio_gym_str:
                # Convertir la cadena de fecha a un objeto de fecha
                fecha_inicio_gym = datetime.strptime(fecha_inicio_gym_str, '%Y-%m-%d').date()
            else:
                # Si no hay un valor válido, usa la fecha actual como valor predeterminado
                fecha_inicio_gym = timezone.now().date()

            # Calcular fecha_fin
            fecha_fin = fecha_inicio_gym + timedelta(days=plan_instance.dias)

            new_user_gym = Usuario_gym.objects.create(
                nombre=data.get('nombre'),
                apellido=data.get('apellido'),
                tipo_id=data.get('tipo_id'),
                id_usuario=data.get('id_usuario'),
                plan=plan_instance,
                fecha_inicio_gym=fecha_inicio_gym,
                fecha_fin=fecha_fin,
            )

            if new_user_gym:
                new_user_gym_dict = model_to_dict(new_user_gym)
                response_data = {
                    'success': True,
                    'mensaje': 'Usuario creado correctamente.',
                    'usuario': new_user_gym_dict,
                }

                return JsonResponse(response_data)

        return JsonResponse({'success': False, 'mensaje': 'No se pudo guardar o tipo de plan no especificado.'})

    return JsonResponse({'success': False, 'mensaje': 'Método no permitido'})


def form_invalid(self, form):
        return JsonResponse({'success': False, 'mensaje': 'Formulario inválido.'})
        
class EditarUsuario(UpdateView):
    model = Usuario_gym
    fields = '__all__'
    success_url = reverse_lazy('plan')


@api_view(['PUT'])
def editar_usuario(request, pk):
    if request.method == 'PUT':
        try:
            usuario = Usuario_gym.objects.get(pk=pk)
        except Usuario_gym.DoesNotExist:
            return JsonResponse({'success': False, 'mensaje': 'Usuario no encontrado.'}, status=404)

        data = json.loads(request.body)
        print(data)

        # Actualización del tipo de plan
        tipo_plan = data.get('tipo_plan')
        if tipo_plan:
            try:
                plan_instance = Planes_gym.objects.get(tipo_plan=tipo_plan)
            except Planes_gym.DoesNotExist:
                return JsonResponse({'success': False, 'mensaje': 'Tipo de plan inválido.'}, status=400)

            usuario.plan = plan_instance

        # Actualización de la fecha de inicio
        fecha_inicio_gym_str = data.get('fecha_inicio_gym')
        if fecha_inicio_gym_str:
            try:
                fecha_inicio_gym = datetime.strptime(fecha_inicio_gym_str, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'success': False, 'mensaje': 'Fecha de inicio inválida.'}, status=400)
            usuario.fecha_inicio_gym = fecha_inicio_gym

        # Calcular y actualizar la fecha de finalización
        if usuario.plan and usuario.fecha_inicio_gym:
            usuario.fecha_fin = usuario.fecha_inicio_gym + timedelta(days=usuario.plan.dias)
        else:
            return JsonResponse({'success': False, 'mensaje': 'No se puede calcular la fecha de finalización.'}, status=400)

        # Actualización de otros campos (nombre, apellido, etc.)
        usuario.nombre = data.get('nombre', usuario.nombre)
        usuario.apellido = data.get('apellido', usuario.apellido)
        usuario.tipo_id = data.get('tipo_id', usuario.tipo_id)
        usuario.id_usuario = data.get('id_usuario', usuario.id_usuario)
        # Aquí puedes agregar más campos según tus necesidades
        
        print(usuario.fecha_inicio_gym, usuario.plan, usuario.fecha_fin)

        # Guardar los cambios en el usuario
        usuario.save()

        # Preparar la respuesta
        response_data = {
            'success': True,
            'mensaje': 'Usuario actualizado correctamente.',
            'usuario': {
                'id': usuario.id,
                'nombre': usuario.nombre,
                'apellido': usuario.apellido,
                'tipo_id': usuario.tipo_id,
                'id_usuario': usuario.id_usuario,
                'tipo_plan': usuario.plan.tipo_plan if usuario.plan else None,
                'fecha_inicio_gym': usuario.fecha_inicio_gym.strftime('%Y-%m-%d') if usuario.fecha_inicio_gym else None,
                'fecha_fin': usuario.fecha_fin.strftime('%Y-%m-%d') if usuario.fecha_fin else None,
            }
        }
        print("Datos del usuario actualizado:", response_data['usuario'])
        return JsonResponse(response_data)

    return JsonResponse({'success': False, 'mensaje': 'Método no permitido.'})

    
class DetalleUsuario(DetailView):
    model = Usuario_gym

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Obtener el plan asociado al usuario
        plan = self.object.plan

        # Usar usuario.plan.dias directamente en la función
        dias_restantes = (self.object.fecha_fin - datetime.now().date()).days

        # Construir el JSON de respuesta
        data = {
            'id': self.object.id,
            'nombre': self.object.nombre,
            'apellido': self.object.apellido,
            'tipo_id': self.object.get_tipo_id_display(),
            'id_usuario': self.object.id_usuario,
            'fecha_inicio_gym': self.object.fecha_inicio_gym,
            'fecha_fin' : self.object.fecha_fin,
            'codigo_qr_url': self.object.codigo_qr.url if self.object.codigo_qr else None,
            'tipo_plan': plan.tipo_plan,
            'precio': plan.precio,
            'dias_restantes': dias_restantes,
            # Agrega más campos según sea necesario
        }

        return JsonResponse(data)


class EliminarUsuario(DeleteView):
    model = Usuario_gym
    success_url = reverse_lazy('plan')

    def delete(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            return JsonResponse({'success': True, 'mensaje': 'Usuario eliminado correctamente.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


# @login_required(login_url='login')
@csrf_exempt
def lector(request):
    if request.method == 'POST' and 'imagen' in request.FILES:
        imagen = request.FILES['imagen']
        qr_data = decode(cv2.imdecode(np.frombuffer(imagen.read(), np.uint8), -1))
        if qr_data:
            # Si se encontró un código QR en la imagen
            codigo_qr = qr_data[0].data.decode('utf-8')
            print(f'Imagen recibida y procesada correctamente. Código QR: {codigo_qr}')
            ruta_carpeta_media = os.path.join(settings.BASE_DIR, 'media', 'gymapp')
            usuario = Usuario_gym.objects.filter(id_usuario=codigo_qr).first()
            if usuario:
                nombre_usuario = usuario.nombre
                apellido_usuario = usuario.apellido
                full_name = f'{nombre_usuario} {apellido_usuario}'
                # Registrar la asistencia
                fecha_actual = datetime.now().date()
                hora_actual = datetime.now().time().strftime('%H:%M:%S')
                try:
                    asistencia = Asistencia(usuario=usuario, fecha=fecha_actual, hora=hora_actual)
                    asistencia.save()
                    response_data = {
                        'success': True,
                        'mensaje': 'Asistencia registrada correctamente.',
                        'codigo': codigo_qr,
                        'name': full_name,
                    }
                    return JsonResponse(response_data)
                except Exception as e:
                    mensaje = f'Error al registrar la asistencia: {str(e)}'
                    return JsonResponse({'success': False, 'mensaje': mensaje})
            else:
                mensaje = f'No se encontró un usuario con el código QR: {codigo_qr}'
                return JsonResponse({'success': False, 'mensaje': mensaje})
        else:
            # Si no se encontró un código QR en la imagen
            print('No se encontró un código QR en la imagen.')
            return JsonResponse({'success': False, 'mensaje': 'No se encontró un código QR en la imagen.'})
    else:
        # Si la solicitud no es POST o no se proporcionó ninguna imagen
        mensaje = 'No se proporcionó una imagen en la solicitud POST.'
        return JsonResponse({'success': False, 'mensaje': mensaje})


# ---------------------------------------------------------------------------------------------


def consulta_asistencia(request, usuario_id=None):
    if usuario_id:
        # Si se proporciona un usuario_id, consultar asistencia específica para ese usuario
        usuario = get_object_or_404(Usuario_gym, pk=usuario_id)
        fecha_actual = timezone.now().date()
        try:
            asistencia = Asistencia.objects.get(usuario=usuario, fecha=fecha_actual)
            presente = asistencia.presente
            mensaje = f"Asistencia de {usuario} el {fecha_actual} está presente: {presente}"
        except Asistencia.DoesNotExist:
            presente = False
            mensaje = f"No hay registro de asistencia para {usuario} el {fecha_actual}"
        
        return JsonResponse({'presente': presente, 'mensaje': mensaje, 'usuario_id': usuario.id, 'nombre_usuario': usuario.nombre})
    else:
        # Si no se proporciona usuario_id, listar todas las asistencias
        fecha_param = request.GET.get('fecha')
        id_usuario_param = request.GET.get('id_usuario')

        asistencias = Asistencia.objects.all()

        # Filtrar por fecha si se proporciona una fecha válida
        if fecha_param:
            try:
                fecha = timezone.datetime.strptime(fecha_param, '%Y-%m-%d').date()
                asistencias = asistencias.filter(fecha=fecha)
            except ValueError:
                return HttpResponseBadRequest('Formato de fecha inválido')

        # Filtrar por id_usuario si se proporciona un ID válido
        if id_usuario_param:
            asistencias = asistencias.filter(usuario__id=id_usuario_param)

        # Obtener fechas únicas de la base de datos y ordenarlas en orden descendente
        fechas = (
            Asistencia.objects.annotate(date=Trunc('fecha', 'day', output_field=DateField()))
            .values('date')
            .distinct()
            .order_by('-date')
        )

        # Convertir queryset a lista de diccionarios para JsonResponse
        asistencias_lista = list(asistencias.values('id', 'fecha', 'presente', 'hora', 'usuario__id', 'usuario__nombre', 'usuario__id_usuario'))

        return JsonResponse({'asistencias': asistencias_lista, 'fechas': list(fechas), 'fecha_seleccionada': fecha_param, 'id_usuario': id_usuario_param})



@csrf_exempt
def crear_asistencia(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        nuip = data.get('nuip')
        presente = data.get('presente', False)  
        fecha = data.get('fecha')  
        hora = data.get('hora')

        try:
            # Buscar usuario por NUIP en lugar de ID primaria
            usuario = Usuario_gym.objects.get(id_usuario=nuip)

            # Crear la asistencia
            asistencia = Asistencia(usuario=usuario, fecha=fecha, presente=presente, hora=hora)
            asistencia.save()

            # Devolver la respuesta con los datos de la asistencia creada
            response_data = {
                'usuario_id': usuario.id,  # Puedes seguir devolviendo el ID primario si es necesario
                'nombre': usuario.nombre,
                'identificacion': usuario.id_usuario,
                'fecha': fecha,
                'hora' : hora,
                'mensaje': 'Asistencia creada correctamente'
            }
            return JsonResponse(response_data, status=201)
        except Usuario_gym.DoesNotExist:
            return JsonResponse({'error': f'No se encontró un usuario con NUIP {nuip}'}, status=404)

    return HttpResponseNotFound('Not Found this NUIP')


@csrf_exempt
def eliminar_asistencia(request, asistencia_id):
    try:
        # Buscar la asistencia por ID y eliminarla
        asistencia = Asistencia.objects.get(id=asistencia_id)
        asistencia.delete()
        
        # Devolver una respuesta de éxito
        return JsonResponse({'success': True, 'message': 'Asistencia eliminada correctamente'})
    except Asistencia.DoesNotExist:
        # Si la asistencia no se encuentra, devolver un error
        return JsonResponse({'success': False, 'message': 'No se encontró la asistencia correspondiente'}, status=404)
    except Exception as e:
        # Manejar otros errores y devolver un mensaje genérico de error
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


# ------------------------------------------------------------------


def obtener_planes_gym(request):
    planes_gym = Planes_gym.objects.all()
    
    data = [{'id' : plan.id, 'tipo_plan': plan.tipo_plan, 'precio': plan.precio, 'dias': plan.dias} for plan in planes_gym]
    
    return JsonResponse({'planes_gym': data})

@csrf_exempt
def crear_plan(request):
    if request.method == 'POST':
        # Obtén los datos del cuerpo de la solicitud en formato JSON
        data = json.loads(request.body)
        # Crea un formulario con los datos recibidos
        form = PlanesForm(data)
        if form.is_valid():
            # Guarda el nuevo plan
            nuevo_plan = form.save()
            # Devuelve una respuesta JSON con información sobre el nuevo plan
            response_data = {
                'success': True,
                'message': 'Plan creado con éxito',
                'data' : {
                    'plan_id': nuevo_plan.id,
                    'tipo_plan': nuevo_plan.tipo_plan,
                    'precio': nuevo_plan.precio,
                    'dias': nuevo_plan.dias,
                }
            }
        else:
            # Devuelve una respuesta JSON con errores si el formulario no es válido
            response_data = {
                'success': False,
                'errors': form.errors,
            }
        print(response_data)
        print('datos recibidos: ', data)
        return JsonResponse(response_data)
    else:
        # Devuelve una respuesta JSON indicando que el método no está permitido
        return JsonResponse({'error': 'Método no permitido'}, status=405)


def editar_plan(request, plan_id):
    # Obtiene el plan existente por su ID
    try:
        plan = Planes_gym.objects.get(id=plan_id)
    except Planes_gym.DoesNotExist:
        return JsonResponse({'error': 'Plan no encontrado'}, status=404)

    if request.method == 'PUT':
        # Obtiene los datos del cuerpo de la solicitud en formato JSON
        data = json.loads(request.body)

        # Crea un formulario con los datos recibidos y el plan existente
        form = PlanesForm(data, instance=plan)

        if form.is_valid():
            # Guarda la actualización del plan
            plan_actualizado = form.save()

            # Devuelve una respuesta JSON con información sobre el plan actualizado
            response_data = {
                'success': True,
                'message': 'Plan actualizado con éxito',
                'plan_id': plan_actualizado.id,
                'tipo_plan': plan_actualizado.tipo_plan,
                'precio': plan_actualizado.precio,
                'dias': plan_actualizado.dias,
            }
        else:
            # Devuelve una respuesta JSON con errores si el formulario no es válido
            response_data = {
                'success': False,
                'errors': form.errors,
            }

        print(response_data)
        return JsonResponse(response_data)
    else:
        # Devuelve una respuesta JSON indicando que el método no está permitido
        return JsonResponse({'error': 'Método no permitido'}, status=405)


def eliminar_plan(request, plan_id):
    if request.method == 'DELETE':
        # Busca el plan por su ID
        plan = get_object_or_404(Planes_gym, id=plan_id)

        # Elimina el plan de la base de datos
        plan.delete()

        # Devuelve una respuesta JSON indicando que el plan ha sido eliminado con éxito
        return JsonResponse({'success': True, 'message': 'Plan eliminado con éxito'})
    else:
        return JsonResponse({'success': False, 'message': 'Metodo no permitido'})



# calculando tiempo de plan
# @login_required(login_url='login')
def plan_usuario(request, usuario_id=None):
    try:
        if usuario_id:
            print(f"Recibida solicitud para usuario_id: {usuario_id}")
            usuario = get_object_or_404(Usuario_gym, pk=usuario_id)
            dias_restantes = (usuario.fecha_fin - datetime.now().date()).days

            tarjeta = {
                'id': usuario.id,
                'nombre_usuario': usuario.nombre,
                'apellido_usuario': usuario.apellido,
                'tipo_id_usuario': usuario.get_tipo_id_display(),
                'id_usuario_gym': usuario.id_usuario,
                'dias_restantes_usuario': dias_restantes,
                'fecha_inicio_usuario': usuario.fecha_inicio_gym,
                'tipo_plan_gym': usuario.plan.tipo_plan,
                'precio_plan_gym': usuario.plan.precio,
                'dias_plan_gym': usuario.plan.dias,
            }

            return JsonResponse({'tarjeta': tarjeta})
        else:
            usuarios = Usuario_gym.objects.all()
            tarjetas = []

            for usuario in usuarios:
                dias_restantes = (usuario.fecha_fin - datetime.now().date()).days

                if -365 <= dias_restantes <= 366:
                    tarjeta = {
                        'id': usuario.id,
                        'nombre_usuario': usuario.nombre,
                        'apellido_usuario': usuario.apellido,
                        'tipo_id_usuario': usuario.get_tipo_id_display(),
                        'id_usuario_gym': usuario.id_usuario,
                        'dias_restantes_usuario': dias_restantes,
                        'fecha_inicio_usuario': usuario.fecha_inicio_gym,
                        'tipo_plan_gym': usuario.plan.tipo_plan,
                        'precio_plan_gym': usuario.plan.precio,
                        'dias_plan_gym': usuario.plan.dias,
                        'fecha_fin' : usuario.fecha_fin,
                    }
                    tarjetas.append(tarjeta)

            tarjetas_ordenadas = sorted(tarjetas, key=lambda x: x['dias_restantes_usuario'])

            return JsonResponse({'tarjetas': tarjetas_ordenadas})

    except Exception as e:
        # Imprime información sobre la excepción
        print(f'Error en la solicitud: {str(e)}')
        return JsonResponse({'error': f'Error en la solicitud: {str(e)}'})







# -----------------------------------------------------------------------------------------------






def obtener_articulos(request, id=None):
    if request.method == 'GET':
        if id:  # Si se proporciona un ID en la URL
            try:
                articulo = Articulo.objects.get(id=id)
                data = {
                    'id': articulo.id,
                    'nombre': articulo.nombre,
                    'descripcion': articulo.descripcion, 
                    'precio': float(articulo.precio), 
                    'cantidad_disponible': articulo.cantidad_disponible,
                }
                return JsonResponse({'articulo': data})
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'El artículo no existe'}, status=404)
        else:
            articulos = Articulo.objects.all()
            data = [{
                'id': articulo.id,
                'nombre': articulo.nombre,
                'descripcion': articulo.descripcion, 
                'precio': float(articulo.precio), 
                'cantidad_disponible': articulo.cantidad_disponible,
            } for articulo in articulos]
            return JsonResponse({'articulos': data})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


def crear_articulo(request):
    if request.method == 'POST':

        data = json.loads(request.body)

        form = ArticuloForm(data)
        if form.is_valid():
            nuevo_articulo = form.save()
            response_data = {
                'success': True,
                'message': 'Artículo creado con éxito',
                'articulo_id': nuevo_articulo.id
            }
        else:
            response_data = {
                'success': False,
                'errors': form.errors
            }

        return JsonResponse(response_data)

    else:
        data = {
            'success': False,
            'message': 'Método no permitido'
        }
        return JsonResponse(data, status=405)

@csrf_exempt
def actualizar_articulo(request, id):
    try: 
        # Obtiene el artículo existente por su ID
        articulo = Articulo.objects.get(id=id)
    except Articulo.DoesNotExist:
        # Devuelve un error si el artículo no existe
        return JsonResponse({'error' : 'El artículo no existe'}, status=404)

    if request.method == 'PATCH':
        # Obtiene los datos del cuerpo de la solicitud en formato JSON
        data = json.loads(request.body)

        # Crea un formulario con los datos recibidos y el artículo existente
        form = ArticuloForm(data, instance=articulo)
        
        if form.is_valid():
            # Guarda la actualización del artículo
            articulo_actualizado = form.save()
        
            # Devuelve una respuesta JSON con información sobre el artículo actualizado
            response_data = {
                'success': True,
                'message': 'Artículo actualizado con éxito',
                'articulo_id': articulo_actualizado.id,
                'nombre': articulo_actualizado.nombre,
                'descripcion': articulo_actualizado.descripcion,
                'precio': articulo_actualizado.precio,
                'cantidad_disponible': articulo_actualizado.cantidad_disponible,
            }
        else: 
            # Devuelve una respuesta JSON con errores si el formulario no es válido
            response_data = {
                'success' : False,
                'errors' : form.errors,
            }
        return JsonResponse(response_data)
    else:
        # Devuelve una respuesta JSON indicando que el método no está permitido
        return JsonResponse({'error': 'Método no permitido'}, status=405)

from django.http import JsonResponse
from .models import Articulo

def eliminar_articulo(request, pk):
    if request.method == 'DELETE':
        try:
            # Obtén la instancia del artículo que se va a eliminar
            articulo = Articulo.objects.get(pk=pk)

            # Puedes agregar lógica adicional antes de eliminar el objeto si es necesario
            # Por ejemplo, verificar si el usuario tiene permisos para eliminar el objeto, etc.

            # Elimina el artículo
            articulo.delete()

            # Devuelve una respuesta JSON indicando que el artículo se eliminó correctamente
            return JsonResponse({'success': True, 'mensaje': 'Artículo eliminado correctamente.'})
        except Articulo.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'El artículo no existe.'})
        except Exception as e:
            # Devuelve una respuesta JSON indicando un error si la eliminación falla
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        # Si el método de solicitud HTTP no es POST, devuelve un error
        return JsonResponse({'success': False, 'error': 'Método no permitido.'}, status=405)


class DetalleArticulo(DetailView):
    model = Articulo

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Construir el JSON de respuesta
        data = {
            'id': self.object.id,
            'nombre': self.object.nombre,
            'descripcion': self.object.descripcion,
            'precio': self.object.precio,
            'cantidad_disponible': self.object.cantidad_disponible,
            # Agrega más campos según sea necesario
        }

        return JsonResponse(data)


def registros_ganancia(request):
    if request.method == 'GET':
        registros_ganancia = RegistroGanancia.objects.all()
        data = [{'fecha': registro.fecha.strftime('%Y-%m-%d'),
                'ganancia_diaria': float(registro.ganancia_diaria),
                'gasto_diario': float(registro.gasto_diario),
                'ganancia_mensual': float(registro.ganancia_mensual),
                'gasto_mensual': float(registro.gasto_mensual),
                'total_mensual': float(registro.total_mensual)
                } for registro in registros_ganancia]
        return JsonResponse({'registros_ganancia': data})


    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            data = {'success': False, 'message': 'Error al decodificar los datos JSON.'}
            return JsonResponse(data, status=400)

        fecha_actual = data.get('fecha', timezone.now().date())

        # Verificar si ya existe un registro para la fecha actual
        registro, created = RegistroGanancia.objects.get_or_create(fecha=fecha_actual)

        # Actualizar los valores de ganancia y gasto diario
        ganancia_diaria = Decimal(data.get('ganancia_diaria', 0))
        gasto_diario = Decimal(data.get('gasto_diario', 0))

        if not created:
            # Si el registro ya existe, sumar los valores a los existentes
            registro.ganancia_diaria += ganancia_diaria
            registro.gasto_diario += gasto_diario
        else:
            # Si es un nuevo registro, establecer los valores proporcionados
            registro.ganancia_diaria = ganancia_diaria
            registro.gasto_diario = gasto_diario

        registro.save()

        # Actualizar los detalles de venta
        detalles_venta = data.get('detalles_venta', [])
        for detalle in detalles_venta:
            articulo_id = detalle.get('articulo_id')
            cantidad_vendida = detalle.get('cantidad_vendida', 0)

            articulo = Articulo.objects.get(pk=articulo_id)

            DetalleVenta.objects.create(registro_ganancia=registro, articulo=articulo, cantidad_vendida=cantidad_vendida)

        data = {'success': True, 'message': 'Registro de ganancia y gasto creado o actualizado correctamente.'}
        return JsonResponse(data)

    else:
        data = {'success': False, 'message': 'Método no permitido'}
        return JsonResponse(data, status=405) 


def obtener_cantidad_planes_vendidos_por_mes(request):
    try:
        # Obtener la cantidad de cada plan vendido por mes
        cantidad_planes_vendidos = Usuario_gym.objects.filter(fecha_inicio_gym__month=timezone.now().month).values('plan__tipo_plan').annotate(cantidad=Count('plan__tipo_plan'))

        # Formatear los datos para enviarlos como respuesta JSON
        data = [{
            'mes': timezone.now().strftime('%B'),  # Obtener el nombre del mes actual
            'plan': registro['plan__tipo_plan'],
            'cantidad': registro['cantidad']
        } for registro in cantidad_planes_vendidos]

        return JsonResponse({'cantidad_planes_vendidos': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)