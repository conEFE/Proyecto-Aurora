# Guion del video: Administración, instalador y nube (parte de Felipe)

Duración: **7 minutos**. Está calculado a **unas 5 palabras por segundo** (la introducción original, de 70 palabras,
se leyó en 15 segundos). Cada bloque indica cuántas palabras tiene y cuántos segundos son **pausas**: momentos en que
no se habla y solo se hace clic o se deja ver la pantalla.

Cómo leerlo:
- **[PAUSA X s]**: callar y hacer lo que dice el corchete. Contar mentalmente.
- Si un bloque se adelanta, alargar la pausa siguiente recorriendo la pantalla con el mouse, sin hablar.
- Leído tal cual da unos 6:45.
- Si falta tiempo, se acorta el bloque 4 (Parámetros).

**Antes de grabar**
- Entrar a https://demo.auroracare.cl como ADMIN, en una ventana limpia (sin otras pestañas ni marcadores personales).
- Tener abiertos: la consola de AWS en **EC2** (us-east-2) y **Route 53 → auroracare.cl**, y `aurora-admin-windows.exe`.
- No mostrar en pantalla: `deploy/.env`, Parameter Store con valores, la clave de operador ni contraseñas reales.
- Para crear la cuenta, usar datos ficticios (por ejemplo, «Dra. Inés Muestra», RUT 39000003-0).
- El instalador **aún no se ha probado de punta a punta**: probarlo antes con una institución `prueba` y grabar ese
  bloque solo si funciona. Si no, mostrar el menú (versión B del bloque 6).

| # | Bloque | Tiempo | Habla | Pausas |
|---|---|---|---|---|
| 1 | Presentación e ingreso | 0:00 – 0:35 | ≈ 115 palabras | 10 s |
| 2 | Resumen de Administración | 0:35 – 1:50 | ≈ 310 palabras | 15 s |
| 3 | Usuarios: crear una cuenta | 1:50 – 3:10 | ≈ 230 palabras | 30 s |
| 4 | Parámetros del triage | 3:10 – 3:50 | ≈ 140 palabras | 10 s |
| 5 | Bitácora y errores | 3:50 – 4:35 | ≈ 165 palabras | 10 s |
| 6 | Instalador aurora-admin | 4:35 – 5:40 | ≈ 245 palabras | 15 s |
| 7 | Nube y dominio | 5:40 – 6:30 | ≈ 220 palabras | 5 s |
| 8 | Cierre | 6:30 – 6:45 | ≈ 50 palabras | — |

---

## 1. Presentación (0:00 – 0:35)

**En pantalla:** landing de demo.auroracare.cl.

> Hola, soy Felipe Campos, y en esta parte del video les voy a mostrar Aurora Care desde el rol de administrador.
> Vamos a ver tres cosas: primero, cómo se gestiona la plataforma en el día a día; segundo, cómo está montada en la
> nube y cómo funciona el dominio; y tercero, cómo podemos instalar una copia completamente nueva de Aurora para
> otra institución, como un hospital o un CESFAM, en pocos minutos.
>
> Lo que van a ver está publicado en internet, en la dirección demo punto auroracare punto c-l, con conexión
> segura. Todos los pacientes y casos que aparecen son ficticios, para cuidar la privacidad. Para empezar, entro con
> mi cuenta de administrador.

**[PAUSA 10 s]** Clic en «Ingresar», escribir RUT y contraseña, y entrar.

## 2. Vista de administración: resumen (0:35 – 1:50)

**En pantalla:** Administración → pestaña **Resumen**.

> Al entrar como administrador, lo primero que aparece es este resumen. Está pensado para que, en menos de un
> minuto, la persona a cargo sepa si la plataforma está sana y si hay algo que necesite su atención. Es la
> primera pantalla que ve cada mañana, y está ordenada de lo más urgente a lo menos urgente: primero lo que puede
> estar fallando, después lo que hay que resolver y al final la actividad general.

**[PAUSA 5 s]** Pasar el mouse por la franja de estado de arriba.

> Arriba está el estado del sistema: qué versión de Aurora está instalada, si el modelo de inteligencia artificial
> está conectado o si se está usando el respaldo simulado, si el servidor ha tenido errores en los últimos siete
> días, y cuántos pacientes y casos hay registrados. Si algo de esto falla, se ve de inmediato, sin tener que entrar
> a ningún servidor ni pedirle nada a un técnico.
>
> Luego viene la sección «Requiere atención». Aquí la plataforma le avisa al administrador lo que debería revisar.
> Por ejemplo, cuentas bloqueadas por intentos fallidos de contraseña, que conviene confirmar con la persona antes
> de desbloquear; personas que todavía no ingresan por primera vez; cuentas que llevan mucho tiempo sin uso, por si
> esa persona ya no trabaja en el centro; o solicitudes de privacidad de pacientes que superan los treinta días.
> Incluso nos avisa si hay un solo administrador activo, porque si esa persona pierde el acceso, nadie más podría
> gestionar las cuentas.

**[PAUSA 5 s]** Bajar hasta el gráfico de ingresos y la actividad reciente.

> Más abajo vemos los ingresos a la plataforma de los últimos días, la actividad reciente y cómo está compuesto el
> equipo: cuántos médicos, cuántos administrativos y cuántos administradores hay. Cada elemento de esta pantalla
> es un acceso directo: si hago clic en una alerta, me lleva justo a la lista de cuentas o de eventos que tengo que
> revisar. Así, desde esta misma pantalla se llega a cada cosa que hay que atender, sin tener que buscarla en
> otra parte.

**[PAUSA 5 s]** Dejar ver la pantalla completa.

## 3. Usuarios: crear una cuenta (1:50 – 3:10)

**En pantalla:** pestaña **Usuarios**.

> En la pestaña Usuarios están todas las cuentas de la institución. Hay tres roles: el médico, que revisa y prioriza
> los casos; el administrativo, que registra pacientes y exámenes; y el administrador, que gestiona las cuentas.
> Cada rol ve solo las secciones que necesita.

**[PAUSA 5 s]** Clic en **Nuevo usuario**.

> Voy a crear la cuenta de una médica nueva. El formulario pide su RUT, que se valida al escribirlo, su nombre
> completo, su correo y el rol que tendrá en la plataforma.

**[PAUSA 10 s]** Escribir RUT, nombre y correo; dejar el rol «Médico».

> Falta la contraseña. El administrador puede escribirla, pero es más seguro que la genere la plataforma.

**[PAUSA 5 s]** Clic en **Generar**, luego en **Copiar**.

> Con «Generar» se crea una contraseña al azar de doce caracteres, en tres grupos, sin letras que se confundan con
> números. Con «Copiar» queda lista para entregarla a la persona por un canal privado. Es una contraseña temporal:
> en su primer ingreso, la plataforma le exige cambiarla por una propia, así que el administrador no conoce la
> contraseña definitiva de nadie.

**[PAUSA 5 s]** Clic en **Crear usuario**; aparece en la lista.

> La cuenta ya aparece en la lista, marcada con la contraseña temporal pendiente de cambio. Si abro su página, veo
> su rol, el estado de la cuenta y su actividad.

**[PAUSA 5 s]** Abrir la página de la nueva usuaria.

> Desde aquí se le puede cambiar el rol, desactivar la cuenta si deja de trabajar en el centro, o restablecer su
> contraseña con el mismo botón de generar. Por último, la sesión de cualquier usuario se cierra sola después de
> un rato sin actividad, con un aviso previo.

## 4. Parámetros del triage (3:10 – 3:50)

**En pantalla:** menú **Parámetros**.

> El administrador también puede consultar las reglas con que Aurora prioriza los casos. Aquí están los pesos del
> puntaje, como el antecedente familiar, el cáncer previo o el tiempo de espera, y los umbrales que separan la
> prioridad alta de la media y la baja. También se define qué hallazgos escalan un caso directamente a prioridad
> alta, por ejemplo cierto BI-RADS informado, y cuántos días como máximo debería esperar un caso antes de ser
> atendido.

**[PAUSA 5 s]** Recorrer los campos con el mouse, sin cambiar nada.

> Ojo, el administrador las ve en modo de solo lectura: por diseño, solo el equipo médico puede modificarlas. Cada
> cambio exige escribir un motivo, y queda guardado como una versión nueva, con quién lo hizo y cuándo. Así,
> si un caso se priorizó de cierta forma, siempre se puede saber con qué reglas se calculó en ese momento. Estas
> reglas las define el equipo clínico; la plataforma solo las aplica de forma consistente, igual para todos los
> pacientes, sin importar quién esté de turno.

**[PAUSA 5 s]** Mostrar el historial de versiones.

## 5. Bitácora y errores (3:50 – 4:35)

**En pantalla:** Administración → pestaña **Bitácora**.

> Como trabajamos con datos de salud, todo lo que pasa en la plataforma queda registrado. La bitácora muestra quién
> hizo qué y cuándo, escrito en lenguaje simple: quién inició sesión, quién revisó un caso, quién abrió la ficha de
> un paciente o quién cambió una contraseña. Esto responde a lo que exige la ley chilena sobre datos de salud:
> cada acceso a la información de un paciente tiene que poder justificarse y rastrearse.

**[PAUSA 5 s]** Elegir el filtro «Alertas de seguridad».

> Puedo filtrar, por ejemplo, solo los eventos de seguridad, y exportar todo a un archivo CSV para entregarlo en una
> auditoría. Esta bitácora no se puede borrar desde la plataforma, ni siquiera siendo administrador.
>
> Y en la pestaña Errores, si algo falla, queda el detalle técnico con un código. Ese mismo código le aparece a la
> persona en pantalla, así que basta con que nos lo envíe para encontrar el problema exacto. Y por diseño, en
> estos errores nunca se guardan datos de pacientes, solo la información técnica necesaria para corregirlos.

**[PAUSA 5 s]** Abrir la pestaña **Errores** un momento.

## 6. El instalador: una institución nueva (4:35 – 5:40)

**En pantalla:** abrir `aurora-admin-windows.exe`.

> Ahora, pensemos en el crecimiento. ¿Qué pasa si otro hospital o un CESFAM quiere usar Aurora? No queremos mezclar
> sus datos con los de otra institución, y tampoco queremos configurar un servidor a mano cada vez. Para eso
> construimos **aurora-admin**: un ejecutable para Windows, Mac o Linux, que se descarga desde nuestro repositorio y
> solo necesita la herramienta de línea de comandos de AWS para iniciar sesión.

**[PAUSA 5 s]** Escribir la clave de operador (fuera de cámara) y llegar al menú.

> Al abrirlo, pide una clave de operador, que solo conoce el responsable del equipo. Luego muestra un menú con
> todo lo necesario: inscribir una institución, ver las que existen, actualizarlas, respaldarlas, pausarlas o
> darlas de baja. Cada opción hace unas pocas preguntas y luego ejecuta los pasos en AWS.

**Versión A (si la prueba funcionó):** opción **1. Inscribir** → identificador `prueba` → datos ficticios del primer
ADMIN → cortar mientras espera → mostrar `prueba.auroracare.cl` abierta → opción **2. Ver instituciones**.
**Versión B (si no):** mostrar la opción **2. Ver instituciones** o **9. Versiones**.

**[PAUSA 5 s]** Elegir la opción 1 (o la 2 en la versión B).

> Con «Inscribir», escribo un identificador, por ejemplo «hospital-norte», y los datos del primer administrador de
> esa institución. Con eso, la herramienta crea sola todo lo que necesita: su propio servidor, su base de datos, su
> espacio cifrado para las imágenes, sus propias claves secretas y su propia dirección, hospital-norte punto
> auroracare punto c-l. En unos quince a veinte minutos la plataforma está lista, con la última versión y con
> conexión segura.
>
> Cada institución queda separada de las demás: tiene su propio servidor y su propia base de datos. Desde el mismo menú se pueden actualizar todas las instituciones a la versión nueva, hacer
> un respaldo inmediato, o dar de baja una institución, guardando antes un respaldo final. Cada institución cuesta
> unos diez dólares al mes de infraestructura.

**[PAUSA 5 s]** Dejar ver el resultado o el menú.

## 7. Cómo funciona en la nube y el dominio (5:40 – 6:30)

**En pantalla:** consola de AWS → EC2 (`aurora-prod`), luego Route 53 (zona `auroracare.cl`, registro `demo`).

> Por detrás, Aurora vive en Amazon Web Services, en un servidor ubicado en Ohio, Estados Unidos. Dentro de ese
> servidor corren tres partes separadas: la base de datos, el motor de la aplicación y el sitio web, cada una en su
> propio contenedor. Así, si actualizamos una parte, las otras no se ven afectadas.
>
> Las imágenes de las mamografías se guardan cifradas dos veces: primero por la propia aplicación, y luego por AWS.
> El almacenamiento no es público, y el servidor no tiene ningún acceso remoto abierto: lo administramos por una
> conexión segura de AWS. La base de datos se respalda automáticamente todos los días de madrugada, los registros
> se guardan treinta días, y tenemos un presupuesto con alertas para que el costo no se nos escape. Hoy cuesta
> alrededor de once dólares al mes.

**[PAUSA 5 s]** Cambiar a Route 53.

> Sobre el dominio: compramos auroracare punto c-l en NIC Chile y lo administramos desde AWS. Eso nos permite crear
> subdominios, como demo punto auroracare punto c-l, o uno por cada hospital. El certificado de seguridad se renueva
> solo. El modelo de inteligencia artificial corre en otro equipo, conectado por una red privada; si no responde,
> la plataforma usa un resultado simulado y lo marca como «IA simulada». Antes de instalar una versión nueva, el
> código pasa por pruebas automáticas y se respalda la base de datos.

## 8. Cierre (6:30 – 6:45)

**En pantalla:** volver al resumen de Administración o a la landing.

> En resumen: el administrador tiene todo a la vista y con trazabilidad; la plataforma está en la nube, protegida y
> con respaldos diarios; y podemos llevar Aurora a una nueva institución en minutos, con sus datos aislados.
> Recordemos que Aurora apoya, pero no reemplaza, el criterio médico. Muchas gracias.
