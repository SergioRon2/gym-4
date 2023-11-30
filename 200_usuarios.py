# import sqlite3
# from faker import Faker

# # Conéctate a tu base de datos SQLite3 (o crea una nueva)
# conn = sqlite3.connect('db.sqlite3')
# cursor = conn.cursor()

# # Crea la tabla de usuarios si aún no existe
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS usuarios (
#         id INTEGER PRIMARY KEY,
#         nombre TEXT,
#         apellido TEXT,
#         tipoID TEXT,
#         IDusuario TEXT,
#         plan_id TEXT,
#         fecha_inicio_gym TEXT,
#         fecha_fin TEXT
#     )
# ''')
# sql = "INSERT INTO usuarios (nombre, apellido, tipoID, IDusuario, plan_id, fecha_inicio_gym, fecha_fin) VALUES (?, ?, ?, ?, ?, ?,?)"
# valores = ('Johan', 'Melo', '32', '42', '23', '30', '19')

# # Usa Faker para generar datos ficticios
# # fake = Faker()

# # Número de usuarios que deseas generar
# num_usuarios = 200

# # Inserta datos en la tabla de usuarios
# # for i in range(1, num_usuarios + 1):
# #     nombre = fake.first_name()
# #     apellido = fake.last_name()
# #     tipo_id = fake.random_element(elements=('cedula', 'ti', 'ce', 'pasaporte', 'pep'))  # Reemplaza con tus opciones reales
# #     print(tipo_id)
# #     id_usuario = fake.random_int(min=1, max=1000)
# #     print(id_usuario)
# #     plan_id = fake.random_int(min=1, max=7)  # Reemplaza con el rango real de IDs de planes
# #     fecha_inicio_gym = fake.date_between(start_date='-1y', end_date='today')
# #     fecha_fin = fake.date_between(start_date='today', end_date='+1y')

# #     # Sentencia SQL para la inserción


# cursor.execute(sql, valores)

# #Guarda los cambios y cierra la conexión
# conn.commit()
# conn.close()


# print(f'Se han creado {num_usuarios} usuarios')