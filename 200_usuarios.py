import sqlite3
from faker import Faker

# Conéctate a tu base de datos SQLite3 (o crea una nueva)
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Crea la tabla de usuarios si aún no existe
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS gymapp_usuario_gym (
#         id INTEGER PRIMARY KEY,
#         nombre TEXT,
#         apellido TEXT,
#         tipo_id TEXT,
#         id_usuario TEXT,
#         plan_id TEXT,
#         fecha_inicio_gym TEXT,
#         fecha_fin TEXT
#     )
# ''')

# Utiliza Faker para generar datos ficticios
fake = Faker()

# Número de usuarios que deseas generar
num_usuarios = 2000

# Inserta datos en la tabla de usuarios
for i in range(1, num_usuarios + 1):
    nombre = fake.first_name()
    apellido = fake.last_name()
    tipo_id = fake.random_element(elements=('cedula', 'ti', 'ce', 'pasaporte', 'pep'))  # Reemplaza con tus opciones reales
    id_usuario = fake.random_int(min=1, max=1000)
    plan_id = fake.random_int(min=1, max=7)  # Reemplaza con el rango real de IDs de planes
    fecha_inicio_gym = fake.date_between(start_date='-1y', end_date='today')
    fecha_fin = fake.date_between(start_date='today', end_date='+1y')

    # Sentencia SQL para la inserción
    sql = "INSERT INTO gymapp_usuario_gym (nombre, apellido, tipo_id, id_usuario, plan_id, fecha_inicio_gym, fecha_fin) VALUES (?, ?, ?, ?, ?, ?, ?)"
    valores = (nombre, apellido, tipo_id, id_usuario, plan_id, fecha_inicio_gym, fecha_fin)
    cursor.execute(sql, valores)

# Guarda los cambios y cierra la conexión
conn.commit()
conn.close()

print(f'Se han creado {num_usuarios} usuarios en la tabla gymapp_usuario_gym')
