import datetime
from datetime import datetime
from django.db import models
import qrcode
from django.core.files import File
from datetime import timedelta
from django.utils import timezone
import tempfile 
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from django.utils import timezone



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

        super().save(*args, **kwargs)

    def dias_restantes(self):
        if self.fecha_fin:
            dias_restantes = (self.fecha_fin - timezone.now().date()).days
            return dias_restantes if dias_restantes >= 0 else 0
        return 0


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


class RegistroGanancia(models.Model):
    fecha = models.DateField(default=timezone.now)
    ganancia_diaria = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    gasto_diario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ganancia_mensual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    gasto_mensual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    articulos_vendidos = models.ManyToManyField(Articulo, through='DetalleVenta')

    def __str__(self):
        return f"Registro de Ganancia - {self.fecha}"

    def calcular_ganancia_mensual(self):
        # Calcular la ganancia mensual sumando todas las ganancias diarias del mes actual
        mes_actual = self.fecha.month
        año_actual = self.fecha.year

        ganancias_diarias_del_mes = RegistroGanancia.objects.filter(
            fecha__month=mes_actual,
            fecha__year=año_actual
        )

        total_ganancia_mensual = sum(registro.ganancia_diaria for registro in ganancias_diarias_del_mes)
        self.ganancia_mensual = total_ganancia_mensual
        self.save()

    def calcular_gasto_diario(self):
        # Calcular el gasto diario sumando todos los gastos diarios del mes actual
        mes_actual = self.fecha.month
        año_actual = self.fecha.year

        gastos_diarios_del_mes = RegistroGanancia.objects.filter(
            fecha__month=mes_actual,
            fecha__year=año_actual
        )

        total_gasto_diario = sum(registro.gasto_diario for registro in gastos_diarios_del_mes)
        self.gasto_diario = total_gasto_diario
        self.save()


class DetalleVenta(models.Model):
    registro_ganancia = models.ForeignKey(RegistroGanancia, on_delete=models.CASCADE)
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    cantidad_vendida = models.IntegerField(default=0)