# aurora-admin

Inscribe y administra instituciones: una instancia de Aurora Care por hospital o CESFAM, cada una con su servidor,
base de datos, bucket cifrado y dominio `<institución>.auroracare.cl`.

## Usarlo

1. Descargue el ejecutable de su sistema desde el release **aurora-admin** del repositorio
   (`aurora-admin-windows.exe`, `aurora-admin-macos` o `aurora-admin-linux`). No hace falta el repositorio ni Python.
2. Instale una vez el **AWS CLI** (https://aws.amazon.com/cli/). Se usa solo para iniciar sesión en el proyecto de AWS.
3. Abra el ejecutable. Si no hay sesión de AWS, ofrece iniciarla (se abre el navegador).
4. La primera vez pide definir la **clave de operador** (mínimo 12 caracteres). Solo usted debe conocerla; en AWS
   queda solo su huella. Después la pide al abrir.
5. Elija en el menú:

| Opción | Qué hace |
|---|---|
| 1. Inscribir | Pide identificador, dominio y datos del primer ADMIN; crea todo con la última versión publicada (15–20 min) |
| 2. Ver instituciones | Estado de cada una, versión y dirección |
| 3. Actualizar | Pasa una institución, o todas, a la última versión publicada |
| 4. Respaldar | Respaldo inmediato de la base al bucket de la institución |
| 5/6. Pausar o reactivar | Detiene o enciende el servidor (la IP y el disco siguen cobrando) |
| 7. Contraseña del ADMIN | La contraseña temporal del primer ADMIN; entréguela por un canal privado |
| 8. Dar de baja | Respaldo final y borrado; opcionalmente, también las imágenes y los respaldos |
| 9. Versiones | Versiones de Aurora publicadas (la primera es la que se instala) |

**Versión de Aurora:** cada commit de `main` publica imágenes `sha-<commit>`. La herramienta instala la más reciente;
la opción 9 las lista.

**Costo:** unos USD 10 al mes por institución (EC2 t4g.micro, IP pública y almacenamiento).

## Para desarrollo

`aurora_admin.py` también se ejecuta con Python (`pip install boto3 "botocore[crt]"`) y acepta comandos
(`--help`). El workflow `.github/workflows/aurora-admin.yml` compila los ejecutables con PyInstaller e incluye
`institucion.yaml`, la plantilla de CloudFormation de cada institución.
