# Guion del video: Administración, instalador y nube (parte de Felipe)

Duración objetivo: **6 a 7 minutos** (unas 950 palabras habladas, a ritmo tranquilo). Cada bloque indica qué se ve
en pantalla y qué se dice. Los tiempos son aproximados; si falta tiempo, se acorta el bloque 4.

**Antes de grabar**
- Entrar a https://demo.auroracare.cl como ADMIN, en una ventana limpia (sin otras pestañas ni marcadores personales).
- Tener abiertos: la consola de AWS en **EC2** (us-east-2) y **Route 53 → auroracare.cl**, y `aurora-admin-windows.exe`.
- No mostrar en pantalla: `deploy/.env`, Parameter Store con valores, la clave de operador ni contraseñas reales.
- Para la contraseña generada, usar un usuario de prueba (por ejemplo, el «Dr. Andrés Piloto», RUT 39000002-2).
- El instalador **aún no se ha probado de punta a punta**: probarlo antes con una institución `prueba` y grabar ese
  bloque solo si funciona. Si no, mostrar el menú y explicar el flujo (versión B del bloque 5).

---

## 1. Presentación (0:00 – 0:30)

**En pantalla:** landing de demo.auroracare.cl → «Ingresar» → inicio de sesión como administrador.

**Dice:**
> Hola, soy Felipe Campos. En esta parte les voy a mostrar Aurora Care desde el rol de administrador: cómo se
> gestiona la plataforma día a día, cómo está montada en la nube y cómo podemos instalar una copia nueva para otra
> institución en pocos minutos.
>
> Lo primero: todo lo que ven está publicado de verdad, en **demo.auroracare.cl**, con conexión segura. Los datos
> son ficticios, para cuidar la privacidad.

## 2. Vista de administración: resumen (0:30 – 1:40)

**En pantalla:** Administración → pestaña **Resumen**. Recorrer de arriba hacia abajo.

**Dice:**
> Al entrar, el administrador ve un resumen del sistema. Arriba está el estado general: si el servidor responde, si
> el modelo de inteligencia artificial está conectado y qué versión está corriendo.
>
> Luego viene «Requiere atención». Aquí la plataforma le avisa de lo que debe revisar: cuentas bloqueadas por
> intentos fallidos, personas que todavía no cambian su contraseña temporal o cuentas que llevan tiempo sin uso. La
> idea es que el administrador no tenga que buscar los problemas; los problemas aparecen solos.
>
> Más abajo vemos los ingresos de los últimos días, la actividad reciente y el equipo por rol. Con esto, en un
> vistazo, se sabe si la plataforma se está usando y si algo anda mal.

## 3. Usuarios y contraseñas (1:40 – 2:50)

**En pantalla:** pestaña **Usuarios** → filtrar por «Médico» → buscar por nombre → abrir un médico → bloque
«Restablecer contraseña» → **Generar** → **Copiar** → **Restablecer**. Mostrar también «Nuevo usuario».

**Dice:**
> En Usuarios están todas las cuentas. Se pueden filtrar por rol, por estado o buscar por nombre o RUT.
>
> Cada persona tiene su propia página, con su rol, el estado de su contraseña y su actividad reciente. Desde aquí se
> cambia el rol, se desactiva una cuenta o se restablece la contraseña.
>
> Para crear o restablecer una cuenta, el administrador no tiene que inventar una clave: presiona «Generar» y la
> plataforma crea una contraseña segura al azar, fácil de dictar, que se copia con un clic. Esa clave es temporal: en
> su primer ingreso la persona está obligada a cambiarla. Así el administrador nunca conoce la contraseña definitiva
> de nadie.
>
> Además, la sesión se cierra sola tras un rato sin actividad, con un aviso previo, para que un computador olvidado
> en un box no quede con la sesión abierta.

## 4. Bitácora y errores (2:50 – 3:40)

**En pantalla:** pestaña **Bitácora** → filtro «Seguridad» → mostrar un par de filas → «Descargar CSV». Luego
pestaña **Errores** un momento.

**Dice:**
> Como trabajamos con datos de salud, todo queda registrado. La bitácora muestra quién hizo qué y cuándo, escrito en
> lenguaje simple: quién inició sesión, quién revisó un caso, quién vio la ficha de un paciente. Se puede filtrar,
> por ejemplo, solo los eventos de seguridad, y exportar a CSV para una auditoría.
>
> Esta bitácora no se puede borrar desde la plataforma, ni siquiera siendo administrador. Y si algo falla, en
> Errores queda el detalle técnico con un código, para que el equipo pueda encontrar el problema rápido.

## 5. El instalador: una institución nueva (3:40 – 5:10)

**En pantalla:** abrir `aurora-admin-windows.exe` → clave de operador (escribirla fuera de cámara) → menú.

**Dice:**
> Ahora, ¿qué pasa si otro hospital o un CESFAM quiere usar Aurora? Para eso construimos **aurora-admin**, un
> ejecutable que se descarga desde nuestro repositorio y no necesita instalar nada más que la herramienta de AWS.
>
> Al abrirlo pide una clave de operador, que solo conoce el responsable del equipo. Luego muestra un menú simple:
> inscribir una institución, ver las que existen, actualizarlas, respaldarlas, pausarlas o darlas de baja.

**Versión A (si la prueba funcionó):** opción **1. Inscribir** → identificador `prueba` → datos del primer ADMIN
(ficticios) → cortar el video mientras espera → mostrar la dirección `prueba.auroracare.cl` abierta → opción
**2. Ver instituciones**.

**Versión B (si no):** mostrar el menú y la opción **2. Ver instituciones** o **9. Versiones**.

**Dice:**
> Con «Inscribir», escribo un identificador, por ejemplo «hospital-norte», y los datos del primer administrador. Con
> eso, la herramienta crea sola todo lo que esa institución necesita: su propio servidor, su base de datos, su
> espacio cifrado para las imágenes, sus claves y su propia dirección, **hospital-norte.auroracare.cl**. En unos
> 15 a 20 minutos la plataforma está lista y con conexión segura.
>
> Lo importante es que cada institución queda **completamente separada**: los datos de un hospital nunca se mezclan
> con los de otro. Y el primer administrador recibe una contraseña temporal que debe cambiar al entrar.
>
> Desde el mismo menú se actualizan todas las instituciones a la versión nueva, se hace un respaldo inmediato o se
> da de baja una institución, guardando antes un respaldo final.

## 6. Cómo funciona en la nube (5:10 – 6:20)

**En pantalla:** consola de AWS → EC2 (`aurora-prod`) → Route 53 (zona `auroracare.cl`, registro `demo`). Opcional:
un diagrama simple (navegador → dominio → servidor → base de datos e imágenes cifradas).

**Dice:**
> Por detrás, Aurora vive en Amazon Web Services, en un servidor en Ohio. Dentro del servidor corren tres partes:
> la base de datos, el motor de la aplicación y el sitio web, cada una en su propio contenedor.
>
> Las imágenes de las mamografías se guardan cifradas dos veces: primero por la propia aplicación y luego por AWS. El
> almacenamiento no es público, y el servidor no tiene acceso remoto abierto: lo administramos por una conexión
> segura de AWS, sin contraseñas expuestas.
>
> La base de datos se respalda todos los días de madrugada, los registros se guardan 30 días y tenemos un
> presupuesto con alertas, para que el costo no se nos escape. Hoy cuesta unos 11 dólares al mes.
>
> Sobre el dominio: compramos **auroracare.cl** en NIC Chile y lo administramos en AWS. Eso nos permite crear
> subdominios como **demo.auroracare.cl** o uno por cada hospital, y el certificado de seguridad se renueva solo.
>
> Y el modelo de inteligencia artificial corre aparte, en un computador con tarjeta gráfica, conectado por una red
> privada. Si en algún momento no está disponible, la plataforma sigue funcionando y lo indica claramente con el
> sello «IA simulada».

## 7. Cierre (6:20 – 6:50)

**En pantalla:** volver al resumen de Administración o a la landing.

**Dice:**
> En resumen: el administrador tiene todo a la vista y con trazabilidad; la plataforma está en la nube, segura y con
> respaldos; y podemos llevar Aurora a una nueva institución en minutos, con sus datos aislados.
>
> Recordemos que Aurora **apoya, no reemplaza**, el criterio médico. Gracias.
