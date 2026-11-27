# Instalador de Aurora para Windows

`AuroraSetup-<versión>.exe` instala Aurora completa en un PC (PostgreSQL + API + sitio) en `http://localhost:8080`.
Prototipo académico: IA SIMULADA y solo datos ficticios.

## Usarlo

1. Descargue `AuroraSetup-<versión>.exe` del release **instalador-windows** del repositorio.
2. Ábralo. Si falta **Docker Desktop**, ofrece instalarlo con winget (después hay que reiniciar, abrir Docker Desktop
   y ejecutar «Terminar configuración de Aurora» en el menú Inicio).
3. Ingrese los datos del primer ADMIN (contraseña temporal) y el puerto.
4. Al terminar, construye Aurora (5 a 15 minutos la primera vez, con internet) y abre el navegador.

Menú Inicio → Aurora: **Abrir**, **Detener**, **Reparar** (reconstruye), **Registros** (también muestra los enlaces de
activación de cuentas, porque los correos van a la consola) y **Desinstalar** (pregunta si borrar los datos).

No requiere permisos de administrador (se instala en `%LOCALAPPDATA%\Aurora`). Los secretos se generan al instalar y
quedan en `.env` de esa carpeta, legible solo por el usuario.

## Compilarlo

El workflow `.github/workflows/instalador-windows.yml` prueba los scripts en Linux (pwsh + Docker), compila el .exe con
Inno Setup en Windows y lo publica en el release. A mano, en Windows con Inno Setup 6:

```
ISCC /DAppVersion=2.12.0 deploy\instalador-windows\aurora.iss
```
