"""
Script para crear el usuario de PostgreSQL si no existe.
"""
import os
import sys
from urllib.parse import urlparse, unquote
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), ".env")
if not os.path.exists(env_path):
    print("No se encontro el archivo .env")
    sys.exit(1)

load_dotenv(env_path, encoding='utf-8')

def get_db_config():
    dsn = os.getenv("DB_DSN")
    if not dsn:
        raise ValueError("DB_DSN no encontrado en .env")
    
    dsn_clean = dsn.replace('postgresql+psycopg2://', 'postgresql://')
    parsed = urlparse(dsn_clean)
    
    return {
        'user': unquote(parsed.username) if parsed.username else None,
        'password': unquote(parsed.password) if parsed.password else None,
        'host': parsed.hostname or 'localhost',
        'port': parsed.port or 5432,
    }

def generate_sql_script(username, password):
    sql_file = os.path.join(os.path.dirname(__file__), "create_user.sql")
    with open(sql_file, 'w', encoding='utf-8') as f:
        f.write(f'-- Script generado automaticamente\n')
        f.write(f'-- Ejecuta con: psql -U postgres -f create_user.sql\n\n')
        f.write(f'CREATE USER "{username}" WITH PASSWORD \'{password}\';\n')
        f.write(f'ALTER USER "{username}" CREATEDB;\n')
    print(f"Script SQL generado: {sql_file}")
    print(f"Ejecuta: psql -U postgres -f {sql_file}")

def create_user_if_not_exists():
    try:
        config = get_db_config()
    except ValueError as e:
        print(f"Error: {e}")
        return False
    
    username = config['user']
    password = config['password']
    host = str(config['host'])
    port = int(config['port'])
    
    if not username or not password:
        print("Usuario o contrasena no especificados en DB_DSN")
        return False
    
    print("Este script necesita conectarse como superusuario (postgres)")
    print("Si falla, se generara un script SQL para ejecutar manualmente")
    print()
    
    postgres_password = os.getenv("POSTGRES_PASSWORD")
    if not postgres_password:
        print("Tip: Agrega POSTGRES_PASSWORD a tu .env para automatizar esto")
        postgres_password = input("Ingresa la contrasena de postgres: ")
        if not postgres_password:
            generate_sql_script(username, password)
            return False
    
    try:
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    except ImportError:
        print("psycopg2 no esta instalado")
        generate_sql_script(username, password)
        return False
    
    try:
        print("Conectando a PostgreSQL...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            user='postgres',
            password=postgres_password,
            database='postgres',
            connect_timeout=5
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM pg_user WHERE usename = %s", (username,))
        exists = cursor.fetchone()
        
        if exists:
            print(f"El usuario '{username}' ya existe")
            cursor.execute('ALTER USER "{}" WITH PASSWORD %s'.format(username), (password,))
            print("Contrasena actualizada")
        else:
            print(f"Creando usuario '{username}'...")
            cursor.execute('CREATE USER "{}" WITH PASSWORD %s'.format(username), (password,))
            print("Usuario creado exitosamente")
        
        cursor.execute('ALTER USER "{}" CREATEDB'.format(username))
        print("Permisos CREATEDB asignados")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error al conectar con psycopg2: {error_msg}")
        print()
        print("Generando script SQL alternativo...")
        generate_sql_script(username, password)
        print()
        print("Ejecuta el script SQL manualmente o usa estos comandos:")
        print(f'psql -U postgres')
        print(f'CREATE USER "{username}" WITH PASSWORD \'{password}\';')
        print(f'ALTER USER "{username}" CREATEDB;')
        return False

if __name__ == "__main__":
    print("Inicializando usuario de PostgreSQL...\n")
    if create_user_if_not_exists():
        print("\nUsuario listo. Ejecuta: python init_db.py")
        sys.exit(0)
    else:
        print("\nUsa el script SQL generado o ejecuta los comandos manualmente")
        sys.exit(1)