import mysql.connector

def tratarConexion():
    try: 
        conexion = mysql.connector.connect(
            user = 'ux8tdoxqchjuxlw3', 
            password = 'KeVnDkWjhNRh8j1bj9cu', 
            host='bakmkys5zfkxrgkxfmki-mysql.services.clever-cloud.com', 
            database = 'bakmkys5zfkxrgkxfmki', port = '3306'
        )
        return conexion
    except mysql.connector.Error as err:
        print(f"Error de conexion: {err}")
        return None
    
##print(tratarConexion())
##*Nueva funcion para crear la tabla
def crearTablaUsuarios():
    """
    Crea la tabla 'usuarios' si no existe, con las columnas
    name, lastname, y number.
    """
    # 1. Conexión
    con = tratarConexion()
    if con is None:
        print('Error: No se pudo conectar a la base de datos para crear la tabla.')
        return False

    # 2. Sentencia SQL CREATE TABLE
    # Usamos IF NOT EXISTS para evitar un error si la tabla ya existe
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        lastname VARCHAR(255),
        number VARCHAR(50)
    ) ENGINE=InnoDB;
    """
    
    # 3. Preparar y ejecutar la consulta
    cursor = con.cursor()
    try:
        cursor.execute(create_table_sql)
        con.commit() # Confirma los cambios
        print("Tabla 'usuarios' verificada/creada exitosamente.")
        return True
    except mysql.connector.Error as err:
        print(f"Error al crear la tabla 'usuarios': {err}")
        con.rollback()
        return False
    finally:
        # 4. Cerrar recursos
        cursor.close()
        con.close()
##* Nueva funcion guardar datos de usuario
def guardarUsuario(nombre,apellido,numero):
    ##Conexion
    con = tratarConexion()
    if con is None:
        print('Error no se puede conectar a ala base de datos')
        return False
    
    ##Se prepara la consulta
    cursor = con.cursor()
    sql_query = """ 
    insert into usuarios (name, lastname, number)
    values (%s,%s,%s)          
    """
    datosInsertar = (nombre, apellido, numero)
    ##Ejecutar y guardar 
    try:
        cursor.execute(sql_query, datosInsertar)
        con.commit()
        print(f"Usuario {nombre} guardado en la DB con éxito.")
        return True
    except mysql.connector.Error as err:
        print(f"Error al insertar en la BD: {err}")
        con.rollback()
        return False
    finally:
        cursor.close()
        con.close()

##*Funcion actualizar dias menta
##def actualizarMenta():
    print("Conectando para actualizar Menta...")
    con = tratarConexion()
    if con is None:
        return

    cursor = con.cursor()
    # SQL para poner 80 días específicamente a la Menta
    sql = "UPDATE plant_types SET harvest_days = 80 WHERE name = 'Menta';"
    
    try:
        cursor.execute(sql)
        con.commit() # Importante para guardar los cambios
        
        # Verificamos cuántas filas se cambiaron
        if cursor.rowcount > 0:
            print("¡ÉXITO! La Menta ahora tiene 80 días de cosecha.")
        else:
            print("No se encontró ninguna planta llamada 'Menta' para actualizar.")
            
    except mysql.connector.Error as err:
        print(f"Error al actualizar: {err}")
    finally:
        cursor.close()
        con.close()##
# --- EJECUTAR ---
# Descomenta la siguiente línea, guarda y corre el archivo una vez:
#actualizarMenta()