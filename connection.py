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

def connect_to_database(db_name=None):
    """Conecta a MySQL y selecciona la base de datos especificada."""
    try:
        # Parámetros de conexión
        connection = create_connection()
        if connection.is_connected() and db_name:
            cursor = connection.cursor()
            cursor.execute(f"USE `{db_name}`;")  # Seleccionar la base de datos
            cursor.close()
        return connection
    except mysql.connector.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def get_tables(connection):
    """Obtiene las tablas de la base de datos especificada usando la conexión."""
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES;")  # Comando para MySQL
    tables = [table[0] for table in cursor.fetchall()]  # Obtener nombres de las tablas
    return tables

def get_attributes(connection, table_name):
    cursor = connection.cursor()
    cursor.execute(f"SHOW COLUMNS FROM {table_name};")
    attributes = []
    
    for column in cursor.fetchall():
        name = column[0]
        col_type = column[1]  # Tipo de dato (VARCHAR, INT, etc.)
        key = column[3]       # Aquí se encuentra si es PK o FK (PRI, MUL)
        
        # Revisar longitud si aplica
        length = ""
        if "(" in col_type:
            length = col_type[col_type.index("(") + 1:col_type.index(")")] # Extraer longitud
            col_type = col_type.split("(")[0]  # Eliminar longitud del tipo

        # Revisar si es auto_increment
        auto_increment = "Auto Increment" if "auto_increment" in column[5] else ""

        # Revisar valor por defecto
        default_value = f"Default: {column[4]}" if column[4] is not None else ""

        # Construir los extras
        extras = []
        if auto_increment:
            extras.append(auto_increment)
        if length:
            extras.append(f"Length: {length}")
        if default_value:
            extras.append(default_value)
        
        extras_str = ", ".join(extras)

        # Verificar si es clave primaria o foránea
        if key == "PRI":
            key_type = "PK"  # Clave primaria
        elif key == "MUL":
            key_type = "FK"  # Clave foránea
        else:
            key_type = "Regular"  # Ni PK ni FK

        attributes.append({
            "name": name,          # Nombre del atributo
            "key_type": key_type,  # Aquí asignamos correctamente la clave key_type
            "col_type": col_type,  # Tipo de dato
            "extras": extras_str   # Información adicional como longitud o auto_increment
        })

    cursor.close()
    return attributes

def create_table(db_name, sql):    
    
    no_error = False
    
    try:
        connection = connect_to_database(db_name)        
        cursor = connection.cursor()        
        cursor.execute(f"{sql}")
        connection.commit()
        cursor.close()
        connection.close()
        no_error = True
    except mysql.connector.Error as e:
        print(f"Error al crear la tabla: {e}")
        
    return

def delete_table(db_name, table_name):
    
    try:
        connection = connect_to_database(db_name)        
        cursor = connection.cursor()        
        cursor.execute(f"DROP TABLE {table_name}")
        connection.commit()
        cursor.close()
        connection.close()
        no_error = True
    except mysql.connector.Error as e:
        print(f"Error al eliminar la tabla {table_name}: {e}")
        
    return