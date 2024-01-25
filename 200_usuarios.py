import sqlite3
from faker import Faker

# Conéctate a tu base de datos SQLite3 (o crea una nueva)
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Usa Faker para generar datos ficticios
fake = Faker()

# Número de usuarios que deseas generar
num_usuarios = 400

# Inserta datos en la tabla de usuarios
for i in range(1, num_usuarios + 1):
    nombre = fake.first_name()
    apellido = fake.last_name()
    tipo_id = fake.random_element(elements=('cedula', 'ti', 'ce', 'pasaporte', 'pep'))
    id_usuario = fake.random_int(min=1, max=1000)
    tipo_plan = fake.random_element(elements=('Mensual', 'Anual', 'Diario'))
    fecha_inicio_gym = fake.date_between(start_date='-1y', end_date='today')
    fecha_fin = fake.date_between(start_date='today', end_date='+1y')

    # Sentencia SQL para la inserción
    # sql = "INSERT INTO gymapp_usuario_gym (nombre, apellido, tipo_id, id_usuario, plan_id, fecha_inicio_gym, fecha_fin) VALUES (?, ?, ?, ?, ?, ?, ?)"
    sql = "DELETE FROM usuarios WHERE rowid = (SELECT rowid FROM usuarios ORDER BY RANDOM() LIMIT 1)"
    # valores = (nombre, apellido, tipo_id, id_usuario, tipo_plan, fecha_inicio_gym, fecha_fin)

    cursor.execute(sql)

# Guarda los cambios y cierra la conexión
conn.commit()
conn.close()

# print(f'Se han creado {num_usuarios} usuarios')
print(f'Se han eliminado {num_usuarios} usuarios')
