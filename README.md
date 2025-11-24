# PROYECTO AURORA - Sistema de Detección Temprana de Cáncer de Mama

Sistema de inteligencia artificial basado en YOLO para análisis automatizado de imágenes médicas.

## Requisitos Previos

Antes de comenzar, asegúrese de tener instalado:

1. **Python 3.10 o superior**
   - Descarga disponible en: https://www.python.org/downloads/
   - Durante la instalación, marque la opción "Add Python to PATH"

2. **Node.js 18 o superior y npm**
   - Descarga disponible en: https://nodejs.org/
   - npm se instala automáticamente con Node.js
   - Verifique la instalación ejecutando en la terminal:
    
     python --version
     node --version
     npm --version
     3. **PostgreSQL 14 o superior**
   - Descarga disponible en: https://www.postgresql.org/download/windows/
   - Durante la instalación, recuerde la contraseña configurada para el usuario `postgres`
   - Asegúrese de que el servicio de PostgreSQL esté en ejecución

## Instalación Paso a Paso

### Paso 1: Clonar o Descargar el Proyecto

Si tiene el proyecto en un repositorio Git:
git clone <url-del-repositorio>
cd Proyecto-Integracion
Si ya tiene el proyecto descargado, navegue a la carpeta:
cd "Proyecto-Integracion"### Paso 2: Crear el Entorno Virtual de Python

Abra una terminal (PowerShell o CMD) en la carpeta del proyecto y ejecute:

**Windows (PowerShell):**ll
python -m venv venv**Windows (CMD):**
python -m venv venv**Si tiene Python 3 específicamente:**
python3 -m venv venv### Paso 3: Activar el Entorno Virtual

**Windows (PowerShell):**ershell
.\venv\Scripts\Activate.ps1Si PowerShell muestra un error de política de ejecución, ejecute primero:shell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser**Windows (CMD):**
venv\Scripts\activate.bat
**Linux/Mac:**
source venv/bin/activateDebería ver `(venv)` al inicio de su línea de comandos, indicando que el entorno virtual está activo.

### Paso 4: Instalar Dependencias de Python

Con el entorno virtual activado, navegue a la carpeta `backend` e instale las dependencias:

cd backend
pip install -r requirements.txtSi `pip` no funciona, intente con:
python -m pip install -r requirements.txt### Paso 5: Instalar Dependencias de Node.js

Abra una nueva terminal (sin activar el venv) en la raíz del proyecto y ejecute:

npm installEsto instalará todas las dependencias del frontend (React, Vite, Tailwind CSS, etc.).

### Paso 6: Configurar PostgreSQL

#### 6.1. Crear el Usuario de la Base de Datos

Abra pgAdmin o una terminal de PostgreSQL y ejecute:

CREATE USER "Aurora" WITH PASSWORD 'tu_contraseña_segura';
ALTER USER "Aurora" CREATEDB;**O utilice el script automatizado:**

1. Cree un archivo `.env` en la carpeta `backend` con el siguiente contenido:

# Configuración de PostgreSQL
# Reemplace 'tu_contraseña_postgres' con la contraseña del usuario postgres
DB_DSN=postgresql+psycopg2://postgres:tu_contraseña_postgres@localhost:5432/postgres

# Clave de encriptación (genere una nueva con el script generate_key.py)
ENCRYPTION_KEY=tu_clave_de_encriptacion_aqui

# URL de la API (para desarrollo)
VITE_API_URL=http://localhost:80002. Con el entorno virtual activado, ejecute:
cd backend
python init_user.pyCuando se le solicite la contraseña de `postgres`, ingrésela.

#### 6.2. Crear la Base de Datos

Actualice el `.env` en `backend` con la conexión al usuario `Aurora`:

# Configuración de PostgreSQL
DB_DSN=postgresql+psycopg2://Aurora:tu_contraseña_segura@localhost:5432/postgres

# Clave de encriptación
ENCRYPTION_KEY=tu_clave_de_encriptacion_aqui

# URL de la API
VITE_API_URL=http://localhost:8000Luego ejecute:
python init_db.py### Paso 7: Generar Clave de Encriptación (Opcional pero Recomendado)

Para generar una clave de encriptación segura para las imágenes:
sh
cd backend
python generate_key.pyCopie la clave generada y actualícela en el archivo `.env`:
ENCRYPTION_KEY=la_clave_generada_aqui### Paso 8: Ejecutar Migraciones de la Base de Datos

Con el entorno virtual activado y en la carpeta `backend`, ejecute:

alembic upgrade headEsto creará todas las tablas necesarias en la base de datos.

### Paso 9: Configurar el Frontend

Asegúrese de que el archivo `.env` en `backend` tenga la URL correcta:

VITE_API_URL=http://localhost:8000Si el frontend está en un puerto diferente, actualice esta variable.

## Ejecutar la Aplicación

### Terminal 1: Backend (FastAPI)

Abra una terminal, active el entorno virtual y ejecute:

# Activar venv (si no está activo)
.\venv\Scripts\Activate.ps1  # PowerShell
# o
venv\Scripts\activate.bat     # CMD

# Navegar a backend
cd backend

# Ejecutar el servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Debería ver algo como:
```
INFO:     Will watch for changes in these directories: ['C:\\...\\backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Terminal 2: Frontend (React + Vite)

Abra una nueva terminal (sin activar el venv) en la raíz del proyecto y ejecute:

```bash
npm run dev
```

Debería ver algo como:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Acceder a la Aplicación

1. **Frontend:** Abra su navegador y vaya a `http://localhost:5173`
2. **Backend API:** La API estará disponible en `http://localhost:8000`
3. **Documentación de la API:** `http://localhost:8000/docs` (Swagger UI)

## Prueba de Funcionalidades

Esta sección describe cómo probar las principales funcionalidades del sistema.

### Prueba 1: Registro de Usuario

1. En la pantalla de login, haga clic en "Crear cuenta" o "Sign up"
2. Complete el formulario de registro:
   - **RUT:** Ingrese un RUT válido sin puntos ni guión (ejemplo: `123456789`)
   - **Email:** Ingrese un correo electrónico válido
   - **Contraseña:** Ingrese una contraseña (mínimo 6 caracteres)
   - **Confirmar Contraseña:** Repita la contraseña
   - **Rol:** Seleccione `MEDICO` o `ADMIN`
3. Haga clic en "Registrarse"
4. Debería ver un mensaje de éxito y ser redirigido al login

**Resultado esperado:** Usuario creado exitosamente en la base de datos.

### Prueba 2: Inicio de Sesión

1. En la pantalla de login, ingrese:
   - **RUT:** El RUT que utilizó en el registro
   - **Contraseña:** La contraseña que configuró
2. Haga clic en "Iniciar Sesión"
3. Debería ser redirigido a la página principal (Home)

**Resultado esperado:** Sesión iniciada correctamente, acceso al sistema.

### Prueba 3: Crear un Paciente

1. Una vez autenticado, haga clic en "Subir Imagen" en el menú superior
2. En la sección "Información del Paciente", haga clic en "Seleccionar o Crear Paciente"
3. En el modal que aparece, haga clic en "Crear Nuevo Paciente"
4. Complete el formulario:
   - **RUT:** Ingrese un RUT único (ejemplo: `987654321`)
   - **Nombre:** Ingrese el nombre del paciente
   - **Apellido:** Ingrese el apellido del paciente
   - **Fecha de Nacimiento:** Seleccione una fecha
   - **Sexo:** Seleccione M, F u O
   - **Historial Médico:** (Opcional) Ingrese información relevante
5. Haga clic en "Crear Paciente"
6. El paciente debería aparecer seleccionado en el formulario

**Resultado esperado:** Paciente creado y asociado al caso.

### Prueba 4: Crear un Caso Clínico

1. En la página "Subir Imagen", asegúrese de tener un paciente seleccionado (creado en la Prueba 3)
2. En el campo "Código Anónimo del Paciente", ingrese un código único (ejemplo: `CASE-001`)
3. Haga clic en "Crear Caso"
4. Debería ver un mensaje de confirmación y el caso debería crearse

**Resultado esperado:** Caso clínico creado exitosamente.

### Prueba 5: Subir una Imagen

1. Con un caso creado (Prueba 4), en la sección "Subir Imagen":
   - Haga clic en el área de carga o arrastre una imagen
   - Seleccione un archivo de imagen (JPG, PNG, formato médico recomendado)
2. La imagen debería aparecer en la vista previa
3. Haga clic en "Subir Imagen"
4. Debería ver un mensaje de confirmación

**Resultado esperado:** Imagen subida y guardada encriptada en el servidor.

### Prueba 6: Procesar Imagen (Inferencia)

1. Después de subir una imagen (Prueba 5), haga clic en "Procesar Imagen"
2. Debería ver:
   - Una barra de progreso animada
   - Mensajes de estado ("Procesando imagen...", "Ejecutando modelo...", etc.)
   - El porcentaje de confianza inicial en 0%
3. Espere 2-4 segundos mientras se simula el procesamiento
4. Al finalizar, debería ver:
   - Un porcentaje de confianza (entre 85% y 99%)
   - Un mensaje indicando si se detectó una lesión o no
   - Detalles de las detecciones (si aplica)

**Resultado esperado:** Resultados de inferencia generados y guardados en la base de datos.

### Prueba 7: Ver Casos Clínicos

1. En el menú superior, haga clic en "Casos Clínicos"
2. Debería ver una tabla con todos los casos creados
3. Haga clic en un caso de la lista
4. En el panel derecho, debería ver:
   - Información del caso (código, fecha de creación)
   - Información del paciente (si está asociado)
   - Lista de imágenes subidas
   - Resultados de inferencia para cada imagen

**Resultado esperado:** Visualización correcta de casos y sus detalles.

### Prueba 8: Generar Reporte PDF

1. En "Casos Clínicos", seleccione un caso que tenga imágenes procesadas
2. En el panel de detalles, haga clic en "Generar Reporte PDF"
3. El navegador debería descargar automáticamente un archivo PDF
4. Abra el PDF y verifique que contenga:
   - Información del caso
   - Información del paciente (si está disponible)
   - Resultados de inferencia
   - Imágenes procesadas
   - Detalles de las detecciones

**Resultado esperado:** PDF generado correctamente con toda la información del caso.

### Prueba 9: Ver Reportes y Estadísticas

1. En el menú superior, haga clic en "Reportes"
2. Debería ver:
   - Tarjetas con estadísticas generales:
     - Total de casos
     - Casos positivos
     - Casos negativos
     - Confianza promedio
     - Tiempo promedio de procesamiento
     - Total de detecciones
   - Un gráfico con datos mensuales
3. Los datos deberían reflejar los casos reales creados en el sistema

**Resultado esperado:** Estadísticas correctas basadas en los datos de la base de datos.

### Prueba 10: Panel de Usuario (Médico)

1. En el menú superior, haga clic en "Panel de Usuario" (si su rol es MEDICO)
2. Debería ver tres secciones:
   - **Información del Usuario:** Muestra su RUT, email y rol
   - **Pacientes Asociados:** Lista de pacientes vinculados a sus casos
   - **Tickets de Soporte:** Lista de tickets de soporte (actualmente mock)

**Resultado esperado:** Información del usuario y pacientes asociados correctamente.

### Prueba 11: Panel de Administración (Admin)

1. Inicie sesión con un usuario que tenga rol `ADMIN`
2. En el menú superior, haga clic en "Panel de Administración"
3. Debería ver:
   - **Estadísticas del Sistema:**
     - Total de usuarios
     - Total de casos
     - Total de pacientes
     - Sesiones activas
   - **Usuarios Recientes:** Lista de los últimos usuarios registrados

**Resultado esperado:** Panel de administración con estadísticas del sistema.

### Prueba 12: Buscar Paciente Existente

1. En "Subir Imagen", haga clic en "Seleccionar o Crear Paciente"
2. En el modal, en el campo de búsqueda, ingrese parte del RUT o nombre de un paciente existente
3. Debería aparecer una lista filtrada con los pacientes que coincidan
4. Haga clic en un paciente de la lista para seleccionarlo

**Resultado esperado:** Búsqueda y selección de pacientes existentes funcionando.

### Prueba 13: Ver Imágenes de un Caso

1. En "Casos Clínicos", seleccione un caso
2. En la lista de imágenes, haga clic en una imagen
3. La imagen debería mostrarse en el visor
4. Verifique que la imagen se cargue correctamente (está encriptada y se descifra automáticamente)

**Resultado esperado:** Visualización correcta de imágenes encriptadas.

### Prueba 14: Validación de Formularios

Pruebe los siguientes casos de validación:

1. **Registro con RUT duplicado:**
   - Intente crear un usuario con un RUT ya existente
   - Debería mostrar un error

2. **Registro con contraseñas que no coinciden:**
   - En el formulario de registro, ingrese contraseñas diferentes
   - Debería mostrar un error antes de enviar

3. **Login con credenciales incorrectas:**
   - Intente iniciar sesión con RUT o contraseña incorrectos
   - Debería mostrar un mensaje de error

4. **Crear caso sin paciente:**
   - Intente crear un caso sin seleccionar un paciente
   - El botón "Procesar Imagen" debería estar deshabilitado

**Resultado esperado:** Validaciones funcionando correctamente en todos los formularios.

### Verificación en Base de Datos

Para verificar que los datos se están guardando correctamente:

1. Abra pgAdmin o una herramienta de administración de PostgreSQL
2. Conéctese a la base de datos `BD-Aurora`
3. Verifique las siguientes tablas:
   - `users`: Debería contener los usuarios registrados
   - `patients`: Debería contener los pacientes creados
   - `cases`: Debería contener los casos clínicos
   - `images`: Debería contener las imágenes subidas
   - `inference_results`: Debería contener los resultados de inferencia

**Resultado esperado:** Todos los datos persisten correctamente en la base de datos.

## Crear un Usuario

1. Inicie sesión con un usuario que tenga rol `ADMIN`
2. En el menú superior, haga clic en "Panel de Administración"
3. En la sección "Usuarios", haga clic en "Crear Usuario"
4. Complete el formulario:
   - **RUT:** Ingrese un RUT único (ejemplo: `111111111`)
   - **Email:** Ingrese un correo electrónico válido
   - **Contraseña:** Ingrese una contraseña (mínimo 6 caracteres)
   - **Confirmar Contraseña:** Repita la contraseña
   - **Rol:** Seleccione `MEDICO` o `ADMIN`
5. Haga clic en "Guardar Usuario"
6. El usuario debería aparecer en la lista de usuarios

**Resultado esperado:** Usuario creado exitosamente.