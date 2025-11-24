"""
Script de inicialización de base de datos.
Crea la base de datos si no existe antes de ejecutar las migraciones.
"""
import os
import sys
from urllib.parse import urlparse, unquote
from dotenv import load_dotenv

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
except ImportError:
    print("psycopg2 no está instalado. Instala con: pip install psycopg2-binary")
    sys.exit(1)


env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path, encoding='utf-8')

def get_db_config():
    """Extrae la configuración de la base de datos del DSN."""
    dsn = os.getenv("DB_DSN")
    if not dsn:
        raise ValueError("DB_DSN no encontrado en .env")
    
    # Parsear el DSN
    parsed = urlparse(dsn.replace('postgresql+psycopg2://', 'postgresql://'))
    
    return {
        'user': parsed.username,
        'password': parsed.password,
        'host': parsed.hostname or 'localhost',
        'port': parsed.port or 5432,
        'database': unquote(parsed.path[1:]) if parsed.path else None
    }

def create_database_if_not_exists():
    config = get_db_config()
    db_name = config['database']
    
    if not db_name:
        print("No se especificó nombre de base de datos en DB_DSN")
        return False
    
    # Conectar a PostgreSQL (sin especificar base de datos)
    admin_config = config.copy()
    admin_config['database'] = 'postgres'
    
    try:
        print(f"Conectando a PostgreSQL en {admin_config['host']}:{admin_config['port']}...")
        conn = psycopg2.connect(**admin_config)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Verificar si la base de datos existe
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_name,)
        )
        exists = cursor.fetchone()
        
        if exists:
            print(f"La base de datos '{db_name}' ya existe")
        else:
            print(f"Creando base de datos '{db_name}'...")
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"Base de datos '{db_name}' creada exitosamente")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"Error de conexión: {e}")
        print("Verifica que PostgreSQL esté corriendo y las credenciales sean correctas")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Inicializando base de datos...\n")
    if create_database_if_not_exists():
        print("\n✅ Base de datos lista. Ejecuta: alembic upgrade head")
        sys.exit(0)
    else:
        print("No se pudo inicializar la base de datos")
        sys.exit(1)