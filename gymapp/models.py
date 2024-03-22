from datetime import datetime
from decimal import Decimal
import os
from django.db import models
from django.http import HttpResponse
import qrcode
from django.core.files import File
import tempfile
from django.db.models import Sum
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from django.utils import timezone
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.utils.encoding import smart_str


# Create your models here.
def generar_codigo_qr(data):
    qr = qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Crear un archivo temporal para guardar la imagen
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        img.save(temp_file, format='PNG')

    # Devolver el nombre del archivo temporal
    return temp_file.name


class Planes_gym(models.Model):
    tipo_plan = models.CharField(max_length=20)
    precio = models.IntegerField(default=0)
    dias = models.IntegerField(default=0)

    def __str__(self):
        return self.tipo_plan


class Usuario_gym(models.Model):
    tipos_id_choice=[
        ('Cédula de Ciudadanía','Cédula de Ciudadanía'),
        ('Tarjeta de Identidad', 'Tarjeta de Identidad'),
        ('Cédula de Extranjería', 'Cédula de Extranjería'),
        ('Pasaporte','Pasaporte'),
        ('Permiso Especial de Permanencia','Permiso Especial de Permanencia'),
    ]
    
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    tipo_id = models.CharField(max_length=50, choices=tipos_id_choice)
    id_usuario = models.IntegerField(default=0)
    codigo_qr = models.ImageField(upload_to='gymapp', null=True, blank=True, editable=False)
    plan = models.ForeignKey(Planes_gym, on_delete=models.CASCADE, null=True, blank=True)
    fecha_inicio_gym = models.DateField(default=timezone.now)
    fecha_fin = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    def save(self, *args, **kwargs):
        if isinstance(self.nombre, str):
            self.nombre = self.nombre.upper()
        if isinstance(self.apellido, str):
            self.apellido = self.apellido.upper()
            
        if self.plan and not self.fecha_fin:
            # Calcular la fecha de fin utilizando los días del plan
            self.fecha_fin = self.fecha_inicio_gym + timedelta(days=self.plan.dias)

            if self.plan.tipo_plan == 'Anual':  # Utilizar relativedelta solo para el plan anual
                self.fecha_fin = self.fecha_inicio_gym + relativedelta(years=1)
            else:
                # Utilizar timedelta para otros tipos de planes
                self.fecha_fin = self.fecha_inicio_gym + timedelta(days=self.plan.dias)
                
        qr_img_path = generar_codigo_qr(self.id_usuario)
        with open(qr_img_path, 'rb') as temp_file:
            self.codigo_qr.save(f"{self.nombre} {self.id_usuario}.png",File(temp_file), save=False)

        super().save(*args, **kwargs)

    def dias_restantes(self):
        if self.fecha_fin:
            dias_restantes = (self.fecha_fin - timezone.now().date()).days
            return dias_restantes if dias_restantes >= 0 else 0
        return 0

    def descargar_qr(request, user_id, user_name):
        # Lógica para generar el código QR y obtener la ruta del archivo
        # En este ejemplo, supongamos que ya tienes la ruta del archivo almacenada en la variable qr_file_path
        # Aquí deberías adaptar esta lógica según cómo estés generando y almacenando los códigos QR
        qr_file_path = f'media/gymapp/{user_name}{user_id}.png'

        # Abre el archivo y lee su contenido binario
        with open(qr_file_path, 'rb') as qr_file:
            # Lee el contenido binario del archivo
            qr_data = qr_file.read()

        # Preparar la respuesta HTTP con el contenido binario del archivo
        response = HttpResponse(qr_data, content_type='image/png')
        # Forzar la descarga del archivo en lugar de mostrarlo en el navegador
        response['Content-Disposition'] = f'attachment; filename="{smart_str(user_id)}.png"'

        return response

# eliminacion del codigo qr, va enlazado con el modelo usuario_gym
@receiver(pre_delete, sender=Usuario_gym)
def eliminar_codigo_qr(sender, instance, **kwargs):
    # Lógica para eliminar el código QR asociado al Usuario_gym
    if instance.codigo_qr:
        if os.path.isfile(instance.codigo_qr.path):
            os.remove(instance.codigo_qr.path)

@receiver(post_save, sender=Usuario_gym)
def actualizar_ganancia_diaria(sender, instance, created, **kwargs):
    if created and instance.plan:
        precio_plan = instance.plan.precio
        fecha_actual = datetime.now().date()
        registro_ganancia, _ = RegistroGanancia.objects.get_or_create(fecha=fecha_actual)
        registro_ganancia.ganancia_diaria += precio_plan
        registro_ganancia.save()


@receiver(pre_delete, sender=Usuario_gym)
def restar_ganancia_diaria(sender, instance, **kwargs):
    if instance.plan:
        precio_plan = instance.plan.precio
        fecha_actual = datetime.now().date()
        fecha_fin = instance.fecha_fin
        if fecha_fin and fecha_actual <= fecha_fin - timedelta(days=instance.plan.dias / 2):
            registro_ganancia, _ = RegistroGanancia.objects.get_or_create(fecha=fecha_actual)
            registro_ganancia.ganancia_diaria -= precio_plan
            registro_ganancia.save()


class Asistencia(models.Model):
    usuario = models.ForeignKey(Usuario_gym, on_delete=models.CASCADE)
    fecha = models.DateField(default=timezone.now)
    hora = models.TimeField(default=timezone.now)
    presente = models.BooleanField(default=True)

    def __str__(self):
        return f"Asistencia de {self.usuario} el {self.fecha}"
    
    def save(self, *args, **kwargs):
        if not self.hora:
            hora_actual_utc = timezone.now().strftime('%H:%M:%S')
            hora_actual_bogota = timezone.datetime.strptime(hora_actual_utc, '%H:%M:%S') - timedelta(hours=5)
            self.hora = hora_actual_bogota.time()
        super().save(*args, **kwargs)


class Articulo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_disponible = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre


@receiver(post_save, sender=Articulo)
def agregar_gasto_diario(sender, instance, created, **kwargs):
    if created:
        precio_articulo = Decimal(instance.precio)
        fecha_actual = timezone.now().date()
        registro_ganancia, _ = RegistroGanancia.objects.get_or_create(fecha=fecha_actual)
        registro_ganancia.gasto_diario += precio_articulo
        registro_ganancia.save()

@receiver(pre_delete, sender=Articulo)
def restar_gasto_diario(sender, instance, **kwargs):
    precio_articulo = Decimal(instance.precio)
    fecha_actual = timezone.now().date()
    registro_ganancia, _ = RegistroGanancia.objects.get_or_create(fecha=fecha_actual)
    registro_ganancia.gasto_diario -= precio_articulo
    registro_ganancia.save()


class RegistroGanancia(models.Model):
    fecha = models.DateField(default=timezone.now)
    ganancia_diaria = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    gasto_diario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ganancia_mensual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    gasto_mensual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_mensual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Registro de Ganancia - {self.fecha}"

    def calcular_ganancia_mensual(self):
        mes_actual = self.fecha.month
        año_actual = self.fecha.year
        total_ganancia_mensual = RegistroGanancia.objects.filter(fecha__month=mes_actual, fecha__year=año_actual).aggregate(Sum('ganancia_diaria'))['ganancia_diaria__sum'] or 0
        return total_ganancia_mensual

    def calcular_gasto_mensual(self):
        mes_actual = self.fecha.month
        año_actual = self.fecha.year
        total_gasto_mensual = RegistroGanancia.objects.filter(fecha__month=mes_actual, fecha__year=año_actual).aggregate(Sum('gasto_diario'))['gasto_diario__sum'] or 0
        return total_gasto_mensual

    def calcular_total_mensual(self):
        self.ganancia_mensual = self.calcular_ganancia_mensual()
        self.gasto_mensual = self.calcular_gasto_mensual()
        self.total_mensual = self.ganancia_mensual - self.gasto_mensual

    def save(self, *args, **kwargs):
        self.calcular_total_mensual()
        super().save(*args, **kwargs)


class DetalleVenta(models.Model):
    registro_ganancia = models.ForeignKey(RegistroGanancia, on_delete=models.CASCADE)
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    cantidad_vendida = models.IntegerField(default=0)
    
    
