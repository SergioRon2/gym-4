import datetime
from datetime import datetime

from django.db import models

import qrcode
from django.core.files import File
from datetime import timedelta
from django.utils import timezone
import tempfile 

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
    TIPOS_PLAN = (
        ('A', 'Anual'),
        ('T', 'Trimestral'),
        ('M', 'Mensual'),
        ('S3','21 Días'),
        ('S2','15 Días'),
        ('S', 'Semanal'),
        ('D','Diario'),
        ('O', 'Personalizado'),
    )
    
    tipo_plan = models.CharField(max_length=2, choices=TIPOS_PLAN)
    precio = models.IntegerField( default=0)
    dias = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.get_tipo_plan_display()}"

class Usuario_gym(models.Model):
    
    cedula= 'cedula de ciudadania'
    ti= 'tarjeta de identidad'
    ce= 'cedula de extranjeria'
    pasaporte= 'pasaporte'
    pep= 'permiso especial permanencia'
    
    tipos_id_choice=[
        (cedula,'Cédula de Ciudadanía'),
        (ti, 'Tarjeta de Identidad'),
        (ce, 'Cédula de Extranjería'),
        (pasaporte,'Pasaporte'),
        (pep,'Permiso Especial de Permanencia'),
    ]
    
    nombre= models.CharField(max_length=50)
    apellido= models.CharField(max_length=50)
    tipo_id = models.CharField(max_length=50, choices=tipos_id_choice, default=cedula)
    id_usuario= models.IntegerField(default=0)
    
    codigo_qr = models.ImageField(upload_to='gymapp',null=True, blank=True,editable=False)#Campo no visible, pero accesible
    plan = models.ForeignKey(Planes_gym, on_delete=models.CASCADE, null=True, blank=True)
    fecha_inicio_gym = models.DateField(default=datetime.now, null=True)
    fecha_fin = models.DateField(default=(timezone.now() + timedelta(days=365)).date())
    

    def __str__(self):
        return str(self.nombre + " " + self.apellido)
    
    def dias_restantes(self):
        if self.fecha_fin:
            dias_restantes = (self.fecha_fin - timezone.now().date()).days
            return dias_restantes if dias_restantes >= 0 else 0
        return 0
    
    def save(self, *args, **kwargs):
        # Generar la imagen del código QR
        self.nombre = self.nombre.upper()
        self.apellido = self.apellido.upper()

        qr_img_path = generar_codigo_qr(self.id_usuario)

        # Verificar si la fecha de inicio está proporcionada antes de calcular la fecha de fin
        if self.fecha_inicio_gym:
            if self.plan:
                # Calcular la fecha de fin basándose en el tipo de plan
                if self.plan.tipo_plan == 'M':  # Mensual
                    days_to_add = 31
                elif self.plan.tipo_plan == 'T':  # Trimestral
                    days_to_add = 90
                elif self.plan.tipo_plan == 'S':  # Semanal
                    days_to_add = 7
                elif self.plan.tipo_plan == 'S3':  # Semanal
                    days_to_add = 21
                elif self.plan.tipo_plan == 'S2':  # Semanal
                    days_to_add = 14
                elif self.plan.tipo_plan == 'A':  # Anual
                    days_to_add = 365
                elif self.plan.tipo_plan == 'D':
                    days_to_add = 1
                else:
                    # Otros tipos de plan, no realizar ningún cálculo
                    days_to_add = 0

                # Calcular la fecha de fin
                fecha_fin = self.fecha_inicio_gym + timedelta(days=days_to_add)

                # Establecer la fecha_fin solo si se ha calculado
                self.fecha_fin = fecha_fin

        super().save(*args, **kwargs)





class Asistencia(models.Model):
    usuario = models.ForeignKey(Usuario_gym, on_delete=models.CASCADE)
    fecha = models.DateField(default=timezone.now)
    presente = models.BooleanField(default=True)
    def __str__(self):
        return f"Asistencia de {self.usuario} el {self.fecha}"

