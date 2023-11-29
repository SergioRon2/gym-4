from datetime import datetime, timedelta
from faker import Faker
from gymapp.models import Usuario_gym, Planes_gym
import random

# Configuración de la base de datos
fake = Faker()

# Crear 200 usuarios
for _ in range(200):
    nombre = fake.first_name()
    apellido = fake.last_name()
    tipo_id = random.choice([choice[0] for choice in Usuario_gym.tipos_id_choice])
    id_usuario = fake.random_int(min=1000, max=9999)

    # Seleccionar un plan aleatorio
    plan = Planes_gym.objects.order_by('?').first()

    # Calcular la fecha de inicio (puedes ajustar esto según tus necesidades)
    fecha_inicio = datetime.now() - timedelta(days=random.randint(1, 365))

    # Crear el usuario
    usuario = Usuario_gym(
        nombre=nombre,
        apellido=apellido,
        tipo_id=tipo_id,
        id_usuario=id_usuario,
        plan=plan,
        fecha_inicio_gym=fecha_inicio
    )

    # Guardar el usuario en la base de datos
    usuario.save()

print("Se han creado 200 usuarios en la base de datos.")
