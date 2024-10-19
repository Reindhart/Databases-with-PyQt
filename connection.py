import mysql.connector

def create_connection():
    """ Crea una conexión a la base de datos MariaDB """
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
    )

def create_database(db_name):
    """ Crea una base de datos si no existe """
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`;")
    connection.commit()
    cursor.close()
    connection.close()

def drop_database(db_name):
    """ Elimina una base de datos """
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS `{db_name}`;")
    connection.commit()
    cursor.close()
    connection.close()

def get_databases():
    """ Obtiene la lista de bases de datos """
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SHOW DATABASES;")
    databases = cursor.fetchall()
    cursor.close()
    connection.close()
    return [db[0] for db in databases]

def get_databases_with_tables():
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        
        valid_databases = []
        for (database_name,) in databases:
            cursor.execute(f"USE `{database_name}`;")
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            if tables:  # Solo agregar si hay tablas
                valid_databases.append(database_name)
        
        return valid_databases
    except Exception as err:
        print(f"Error: {err}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def connect_to_database(dabase_name):
    print("hola")

def get_tables(database_name):
    """Obtiene las tablas de la base de datos especificada."""
    # Conectar a la base de datos y ejecutar la consulta
    connection = connect_to_database(database_name)  # Implementa tu lógica de conexión
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES;")  # Comando para MySQL

    tables = [table[0] for table in cursor.fetchall()]  # Obtener nombres de las tablas
    cursor.close()
    connection.close()
    return tables
