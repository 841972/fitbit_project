import psycopg2
from psycopg2 import sql
from config import DB_CONFIG

def connect_to_db():
    """
    Conecta a la base de datos PostgreSQL.
    """
    try:
        connection = psycopg2.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=DB_CONFIG["port"],
            dbname=DB_CONFIG["database"]
        )
        print("Conexión exitosa a la base de datos.")
        return connection
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def init_db():
    """
    Inicializa la base de datos creando las tablas si no existen.
    """
    connection = connect_to_db()
    if connection:
        try:
            with connection.cursor() as cursor:
                # Borrar tablas existentes (si las hay)
                cursor.execute("DROP TABLE IF EXISTS fitbit_data;")
                cursor.execute("DROP TABLE IF EXISTS users;")
                connection.commit()
                # Crear tabla de usuarios
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255),
                        email VARCHAR(255) NOT NULL,
                        linked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        access_token TEXT,
                        refresh_token TEXT
                    );
                """)

                # Crear tabla de datos Fitbit
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS fitbit_data (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        date DATE NOT NULL,
                        steps INTEGER,
                        heart_rate INTEGER,
                        sleep_minutes INTEGER,
                        calories INTEGER,
                        distance FLOAT,
                        floors INTEGER,
                        elevation FLOAT,
                        active_minutes INTEGER,
                        sedentary_minutes INTEGER,
                        nutrition_calories INTEGER,
                        water FLOAT,
                        weight FLOAT,
                        bmi FLOAT,
                        fat FLOAT,
                        oxygen_saturation FLOAT,
                        respiratory_rate FLOAT,
                        temperature FLOAT
                    );
                """)

                connection.commit()
                print("Tablas creadas (si no existían).")
        except Exception as e:
            print(f"Error al inicializar la base de datos: {e}")
        finally:
            connection.close()

def add_user(name, email, access_token=None, refresh_token=None):
    """
    Añade un nuevo usuario a la base de datos.

    Args:
        name (str): Nombre del usuario.
        email (str): Correo electrónico del usuario.
        access_token (str): Token de acceso de Fitbit.
        refresh_token (str): Token de actualización de Fitbit.

    Returns:
        int: ID del usuario recién insertado.
    """
    connection = connect_to_db()
    if connection:
        try:
            with connection.cursor() as cursor:
                # Insertar usuario en la tabla users
                insert_query = """
                INSERT INTO users (name, email, access_token, refresh_token)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """
                cursor.execute(insert_query, (name, email, access_token, refresh_token))
                user_id = cursor.fetchone()[0]  # Obtener el ID del usuario recién insertado
                connection.commit()
                print(f"Usuario {email} añadido exitosamente con ID {user_id}.")
                return user_id
        except Exception as e:
            print(f"Error al añadir usuario: {e}")
        finally:
            connection.close()

def save_to_db(user_id, date, **data):
    """
    Guarda los datos de Fitbit en la base de datos.

    Args:
        user_id (int): ID del usuario.
        date (str): Fecha de los datos (YYYY-MM-DD).
        data (dict): Diccionario con los datos de Fitbit.
    """
    connection = connect_to_db()
    if connection:
        try:
            with connection.cursor() as cursor:
                # Insertar datos en la tabla fitbit_data
                insert_query = """
                INSERT INTO fitbit_data (
                    user_id, date, steps, heart_rate, sleep_minutes,
                    calories, distance, floors, elevation, active_minutes,
                    sedentary_minutes, nutrition_calories, water, weight,
                    bmi, fat, oxygen_saturation, respiratory_rate, temperature
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                );
                """
                cursor.execute(insert_query, (
                    user_id, date,
                    data.get("steps"),
                    data.get("heart_rate"),
                    data.get("sleep_minutes"),
                    data.get("calories"),
                    data.get("distance"),
                    data.get("floors"),
                    data.get("elevation"),
                    data.get("active_minutes"),
                    data.get("sedentary_minutes"),
                    data.get("nutrition_calories"),
                    data.get("water"),
                    data.get("weight"),
                    data.get("bmi"),
                    data.get("fat"),
                    data.get("oxygen_saturation"),
                    data.get("respiratory_rate"),
                    data.get("temperature")
                ))
                connection.commit()
                print(f"Datos de usuario {user_id} guardados exitosamente.")
        except Exception as e:
            print(f"Error al guardar los datos: {e}")
        finally:
            connection.close()

def get_user_history(user_id):
    """
    Obtiene el historial completo de un usuario.

    Args:
        user_id (int): ID del usuario.

    Returns:
        list: Lista de tuplas con el historial del usuario.
    """
    connection = connect_to_db()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM fitbit_data
                    WHERE user_id = %s
                    ORDER BY date;
                """, (user_id,))
                history = cursor.fetchall()
                return history
        except Exception as e:
            print(f"Error al obtener el historial: {e}")
        finally:
            connection.close()

def get_email_history(email):
    """
    Obtiene el historial completo de un email (puede tener múltiples usuarios).

    Args:
        email (str): Correo electrónico del usuario.

    Returns:
        list: Lista de tuplas con el historial del email.
    """
    connection = connect_to_db()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT u.name, f.*
                    FROM users u
                    JOIN fitbit_data f ON u.id = f.user_id
                    WHERE u.email = %s
                    ORDER BY u.linked_at, f.date;
                """, (email,))
                history = cursor.fetchall()
                return history
        except Exception as e:
            print(f"Error al obtener el historial: {e}")
        finally:
            connection.close()

def run_tests():
    """
    Ejecuta pruebas de inserción y consulta para verificar el funcionamiento de la base de datos.
    """

    # Caso 1: Inserción de un nuevo usuario y sus mediciones
    user_id_1 = add_user(
        name="Juan Pérez",
        email="juan@example.com",
        access_token="token_juan",
        refresh_token="refresh_juan"
    )
    save_to_db(
        user_id=user_id_1,
        date="2023-12-01",
        steps=10000,
        heart_rate=75,
        sleep_minutes=420,
        calories=2000,
        distance=8.5,
        floors=10,
        elevation=100.5,
        active_minutes=60,
        sedentary_minutes=480,
        nutrition_calories=1800,
        water=2.5,
        weight=70.5,
        bmi=22.5,
        fat=18.5,
        oxygen_saturation=98.0,
        respiratory_rate=16.5,
        temperature=36.5
    )
    save_to_db(
        user_id=user_id_1,
        date="2023-12-02",
        steps=12000,
        heart_rate=80,
        sleep_minutes=400
    )

    # Caso 2: Inserción de múltiples mediciones para el mismo usuario
    save_to_db(
        user_id=user_id_1,
        date="2023-12-03",
        steps=11000,
        heart_rate=78,
        sleep_minutes=410,
        calories=2100,
        distance=9.0,
        floors=12,
        elevation=105.0,
        active_minutes=65,
        sedentary_minutes=470,
        nutrition_calories=1900,
        water=2.7,
        weight=71.0,
        bmi=22.7,
        fat=18.7,
        oxygen_saturation=98.2,
        respiratory_rate=16.7,
        temperature=36.6
    )

    # Caso 3: Inserción de un nuevo usuario con el mismo email (reasignación del dispositivo Fitbit)
    user_id_2 = add_user(
        name="María Gómez",
        email="juan@example.com",  # Mismo email que Juan
        access_token="token_maria",
        refresh_token="refresh_maria"
    )

    # Caso 4: Inserción de mediciones para el nuevo usuario con el mismo email
    save_to_db(
        user_id=user_id_2,
        date="2023-12-04",
        steps=9000,
        heart_rate=72,
        sleep_minutes=430,
        calories=1900,
        distance=7.5,
        floors=8,
        elevation=95.0,
        active_minutes=55,
        sedentary_minutes=490,
        nutrition_calories=1700,
        water=2.3,
        weight=69.0,
        bmi=22.0,
        fat=18.0,
        oxygen_saturation=97.8,
        respiratory_rate=16.0,
        temperature=36.4
    )

    # Caso 5: Consulta del historial completo de un usuario
    print("\nHistorial de Juan Pérez:")
    history_juan = get_user_history(user_id_1)
    for record in history_juan:
        print(record)

    print("\nHistorial de María Gómez:")
    history_maria = get_user_history(user_id_2)
    for record in history_maria:
        print(record)

    # Caso 6: Consulta del historial de un email (que puede tener múltiples usuarios)
    print("\nHistorial del email juan@example.com:")
    email_history = get_email_history("juan@example.com")
    for record in email_history:
        print(record)

if __name__ == "__main__":
      # Inicializar la base de datos
    init_db()
    add_user(
        name="",
        email="Wearable4LivelyAgeign@gmail.com",
        access_token="",
        refresh_token=""
    )
    #run_tests()