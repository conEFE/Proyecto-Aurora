---
title: "Manual de instalación de Aurora"
subtitle: "Instalación local en Windows (versión de prueba) e instalación en Amazon Web Services (AWS) desde la consola"
author: "Equipo Proyecto Aurora · Proyecto de título, INACAP"
date: "Versión 1.0 · 27-11-2026 · Aurora 2.12.0 (local) y 2.11.0 (AWS)"
lang: es-CL
---

# Antes de empezar

## Qué es Aurora y qué instala este manual

Aurora es una plataforma web que apoya la priorización (triage) de casos con sospecha de cáncer de mama. Es un
**prototipo académico**: apoya, y no reemplaza, el criterio médico.

Este manual explica, paso a paso y sin conocimientos previos, dos formas de instalarla:

| | **A. Local en Windows** | **B. En AWS (internet)** |
|---|---|---|
| Para qué sirve | Recorrer el flujo en un PC, a modo de prueba | Tener Aurora en internet, con dirección `https://` propia |
| Quién puede entrar | Solo quien usa ese PC | Cualquier persona con usuario, desde cualquier lugar |
| Qué se necesita | PC con Windows 10 u 11 y conexión a internet | Una cuenta de AWS con tarjeta de crédito |
| Costo | Gratis | Unos USD 10 a 12 al mes mientras esté creada |
| Tiempo | 30 a 45 minutos (la primera vez) | 30 a 40 minutos |
| Inteligencia artificial | **Simulada** | **Simulada** |

> **Importante.** En ambas instalaciones la inteligencia artificial es **SIMULADA**: los resultados aparecen
> marcados «IA SIMULADA», no provienen del modelo real y **no son resultados clínicos**. Use **solo datos ficticios**
> y RUT de prueba. **La plataforma real, con el modelo de IA conectado, está en <https://demo.auroracare.cl>.**
> Si solo quiere ver Aurora funcionando, no necesita instalar nada: abra esa dirección.

## Palabras que aparecen en el manual

| Palabra | Qué significa |
|---|---|
| Docker Desktop | Programa gratuito que permite ejecutar Aurora en Windows. Se instala una vez. |
| Instalador | El archivo `AuroraSetup-2.12.0.exe` que instala Aurora en Windows. |
| AWS | Amazon Web Services: servicio de Amazon para arrendar servidores en internet. |
| Consola de AWS | El sitio web de AWS (<https://console.aws.amazon.com>) donde se administra todo. |
| CloudFormation | Servicio de AWS que crea todo lo necesario a partir de un archivo (la «plantilla»). |
| Plantilla | El archivo `aurora-aws.yaml`, que describe el servidor de Aurora. |
| Pila (stack) | Lo que CloudFormation crea a partir de la plantilla. Borrar la pila borra el servidor. |
| RUT de prueba | Un RUT válido pero ficticio, por ejemplo `11111111-1`. |
| Contraseña temporal | Contraseña inicial que Aurora obliga a cambiar en el primer ingreso. |

# Parte A. Instalación local en Windows (versión de prueba)

## A.1 Requisitos

- Windows 10 (versión 22H2) o Windows 11, de 64 bits.
- 8 GB de memoria RAM (mínimo 4 GB) y 20 GB libres en el disco.
- Conexión a internet durante la instalación.
- Poder instalar programas en el PC (en un PC del trabajo puede necesitar al encargado de informática).

> **¿Cómo sé si mi Windows es de 64 bits?** Presione la tecla **Windows**, escriba **Acerca de**, abra
> **Acerca de tu PC** y mire **Tipo de sistema**: debe decir «sistema operativo de 64 bits».

## A.2 Paso 1: instalar Docker Desktop

Aurora funciona dentro de Docker Desktop. Si ya lo tiene instalado y abierto, pase a A.3.

1. Abra el navegador y entre a <https://www.docker.com/products/docker-desktop/>.
2. Haga clic en **Download for Windows – AMD64** (en PCs con procesador ARM, **Windows – ARM64**).
3. Abra el archivo descargado (`Docker Desktop Installer.exe`). Si Windows pregunta «¿Desea permitir que esta
   aplicación haga cambios?», responda **Sí**.
4. En la ventana de configuración deje marcada la opción **Use WSL 2 instead of Hyper-V (recommended)** y haga clic
   en **OK**. Espere a que termine (unos 5 minutos).
5. Haga clic en **Close and restart** (cerrar y reiniciar). El PC se reinicia.
6. Después del reinicio, abra **Docker Desktop** desde el menú Inicio.
7. Acepte las condiciones de servicio (**Accept**). Si pide iniciar sesión o crear una cuenta, puede elegir
   **Skip** (omitir) o **Continue without signing in**. Las encuestas también se pueden omitir.
8. Espere hasta que, abajo a la izquierda, aparezca **Engine running** en verde. Ya puede seguir.

> **Si aparece un error de «virtualization» o «WSL».** La virtualización del procesador está desactivada.
> Abra el menú Inicio, escriba **Activar o desactivar las características de Windows**, marque
> **Plataforma de máquina virtual** y **Subsistema de Windows para Linux**, acepte y reinicie. Si el error sigue,
> la virtualización se activa en la configuración del equipo (BIOS/UEFI, opción «Intel VT-x», «AMD-V» o «SVM»);
> busque las instrucciones de la marca de su PC o pida ayuda.

> **Atajo.** Si se salta este paso, el instalador de Aurora detecta que falta Docker Desktop y ofrece
> instalarlo por usted. Igual tendrá que reiniciar y hacer los pasos 6 a 8.

## A.3 Paso 2: descargar el instalador de Aurora

1. Entre a <https://github.com/conEFE/Proyecto-Aurora/releases/tag/instalador-windows>.
2. En la sección **Assets**, haga clic en **AuroraSetup-2.12.0.exe**. Se descarga a la carpeta **Descargas**.

## A.4 Paso 3: ejecutar el instalador

1. Abra **AuroraSetup-2.12.0.exe** desde la carpeta Descargas.
2. **Aviso de Windows.** Es probable que aparezca una ventana azul que dice **«Windows protegió su PC»**. Ocurre
   porque el instalador es de un proyecto académico y no tiene firma digital comercial. Haga clic en
   **Más información** y luego en **Ejecutar de todas formas**.
3. **Aviso de Aurora.** Lea el aviso: explica que es una versión **de prueba**, con **IA simulada**, y que la
   plataforma real está en demo.auroracare.cl. Marque **Acepto el acuerdo** y haga clic en **Siguiente**.
4. **Carpeta de instalación.** Deje la que propone y haga clic en **Siguiente**.
5. **Tareas adicionales.** Deje marcado **Crear un acceso directo en el escritorio** y haga clic en **Siguiente**.
6. **Primer administrador.** Esta es la cuenta con la que entrará por primera vez. Complete:
   - **RUT:** un RUT de prueba, sin puntos y con guion, por ejemplo `11111111-1`.
   - **Nombre:** por ejemplo `Administrador Aurora`.
   - **Correo:** cualquier correo, por ejemplo `admin@ejemplo.cl`.
   - **Contraseña temporal:** al menos 10 caracteres, con letras y números, por ejemplo `Prueba2026x`.
     **Anótela**: la necesitará en unos minutos.

   Haga clic en **Siguiente**.
7. **Puerto.** Deje `8080` y haga clic en **Siguiente**. (Solo cámbielo si otro programa ya usa ese número.)
8. Haga clic en **Instalar**.
9. Se abrirá una **ventana azul (PowerShell)** que construye e inicia Aurora. **La primera vez tarda entre 5 y 15
   minutos.** No la cierre; verá mensajes que empiezan con `==>`. Si Docker Desktop no estaba abierto, el
   instalador lo abre y espera.
10. Al terminar, se abre el navegador en **http://localhost:8080** y el asistente muestra que Aurora (versión local de
    prueba) quedó instalada. Haga clic en **Finalizar**.

## A.5 Paso 4: primer ingreso

1. En el navegador, en <http://localhost:8080>, haga clic en **Ingresar**.
2. Escriba el **RUT** y la **contraseña temporal** del paso A.4.6.
3. Aurora le pedirá **cambiar la contraseña**. Escriba la temporal y luego una nueva (al menos 10 caracteres, con
   letras y números) dos veces. Esta será su contraseña de ahora en adelante.
4. Listo: está dentro de Aurora como **Administrador**.

## A.6 Crear usuarios para probar el flujo completo

El flujo clínico lo hacen otros roles (personal administrativo y médico). Para probarlo:

1. Entre al menú **Administración** y haga clic en **Nuevo usuario**.
2. Complete la ficha: nombre, apellidos, RUT de prueba (por ejemplo `22222222-2`), correo y **rol** (Médico,
   Administrativo o Jefatura y finanzas; al médico se le pide la especialidad).
3. En **Acceso inicial**, elija **Asignar una contraseña temporal** y escriba una. (La opción de enviar un link por
   correo no sirve en la versión local: los correos no se envían.)
4. Haga clic en crear. Cierre sesión con el botón **Salir** (arriba a la derecha) e ingrese con el nuevo RUT y la
   contraseña temporal. Aurora pedirá cambiarla.

> **Si usó la opción de link por correo:** el link no llega al correo, pero queda en los registros. Abra
> **Inicio → Aurora → Registros de Aurora** y busque la línea que dice `Email (console)`; copie el link que aparece
> debajo (empieza con `http://localhost:8080/activar`) y péguelo en el navegador.

Un recorrido de prueba sugerido: el **administrativo** registra un paciente ficticio con su consentimiento, crea
un caso y carga una imagen; Aurora calcula la prioridad con **IA simulada**; el **médico** abre la cola
priorizada, revisa el caso, valida el resultado de la IA, registra su evaluación y firma el reporte PDF; la
**jefatura** revisa el dashboard y el comparador de médicos.

## A.7 Uso diario

En el menú Inicio, carpeta **Aurora**:

| Acceso directo | Para qué sirve |
|---|---|
| **Abrir Aurora** (y el ícono del escritorio) | Inicia Aurora (y Docker Desktop si hace falta) y abre el navegador |
| **Detener Aurora** | Apaga Aurora. Los datos se conservan |
| **Plataforma real (demo.auroracare.cl)** | Abre la plataforma real, con el modelo de IA conectado |
| **Registros de Aurora** | Muestra los mensajes técnicos (útil si algo falla, y para los links de activación) |
| **Reparar Aurora** | Vuelve a construir e iniciar Aurora sin borrar datos |
| **Terminar configuración de Aurora** | Solo si la instalación quedó a medias (por ejemplo, porque se instaló Docker Desktop y había que reiniciar) |
| **Desinstalar Aurora** | Quita Aurora del PC |

Docker Desktop debe estar abierto para que Aurora funcione. Al apagar el PC, Aurora se detiene; al encenderlo, use
**Abrir Aurora**.

## A.8 Desinstalar

1. Menú Inicio → **Aurora** → **Desinstalar Aurora** (o **Configuración → Aplicaciones**, buscar **Aurora**).
2. El desinstalador pregunta si quiere **borrar también la base de datos y las imágenes**. **Sí** borra todo lo que
   se registró (no se puede deshacer); **No** los conserva para una futura instalación.
3. Docker Desktop no se desinstala; si ya no lo necesita, quítelo desde **Configuración → Aplicaciones**.

## A.9 Problemas frecuentes (local)

| Qué pasa | Qué hacer |
|---|---|
| «Windows protegió su PC» | **Más información → Ejecutar de todas formas** (ver A.4.2) |
| «No se encontró Docker» | Instale Docker Desktop (A.2) y luego use **Terminar configuración de Aurora** |
| «Docker no respondió» | Abra Docker Desktop, espere **Engine running** y vuelva a intentar |
| «Falló la construcción» | Revise la conexión a internet y use **Reparar Aurora** |
| El navegador dice «No se puede acceder a este sitio» | Espere 1 minuto y recargue. Si sigue, use **Abrir Aurora** |
| No recuerdo la contraseña del administrador | Desinstale borrando los datos y vuelva a instalar (es una versión de prueba) |
| El puerto 8080 está ocupado | Reinstale y elija otro puerto en el paso A.4.7, por ejemplo `8090` |

# Parte B. Instalación en Amazon Web Services (AWS) desde la consola

Con esta parte, Aurora queda en un servidor de AWS con una dirección `https://` (con candado) a la que se puede entrar
desde cualquier computador o celular. Todo se hace desde el navegador, sin programas adicionales.

## B.1 Qué se crea y cuánto cuesta

La plantilla crea, en su cuenta de AWS:

| Recurso | Para qué | Costo aproximado |
|---|---|---|
| Servidor EC2 `t4g.micro` (1 GB, disco cifrado de 12 GB) | Ejecuta Aurora (base de datos, API y sitio web) | USD 7 al mes |
| IP pública fija | La dirección del servidor en internet | USD 3,6 al mes |
| Bucket S3 cifrado | Imágenes cifradas y respaldo diario de la base de datos | Centavos al mes |
| Registros en CloudWatch | Mensajes técnicos de Aurora (30 días) | Centavos al mes |
| Rol y grupo de seguridad | Permisos mínimos; solo abre los puertos web 80 y 443 (sin acceso SSH) | Sin costo |

**Total: unos USD 10 a 12 al mes** mientras la pila exista. Las cuentas nuevas de AWS suelen tener créditos
gratuitos que cubren varios meses. Detener el servidor reduce el costo, pero la IP y el disco siguen cobrando;
para no pagar nada, elimine la pila (B.9).

## B.2 Paso 1: crear una cuenta de AWS (si no tiene)

1. Entre a <https://aws.amazon.com> y haga clic en **Crear una cuenta de AWS** (o **Create an AWS Account**).
2. Siga los pasos: correo, nombre de la cuenta, contraseña, datos de contacto, **tarjeta de crédito o débito**
   (AWS hace un cargo de verificación que luego devuelve) y verificación por SMS.
3. Si le ofrece elegir plan, el **plan gratuito** (Free) basta para esta instalación.
4. Al terminar, entre a la consola: <https://console.aws.amazon.com>.

> **Región.** AWS tiene centros de datos en varias regiones del mundo. Arriba a la derecha de la consola aparece
> el nombre de la región (por ejemplo **Ohio** o **São Paulo**). Use siempre la misma. En las cuentas de la
> «nueva experiencia de AWS» (proyectos) la región queda fija al crear el proyecto: puede verla en
> **AWS Settings → View all projects → Overview → Additional Info → Region**. Use esa.

## B.3 Paso 2 (recomendado): alerta de presupuesto

Así AWS le avisa por correo si el gasto se acerca a un monto.

1. En la barra de búsqueda de la consola (arriba), escriba **Budgets** y abra **AWS Budgets**
   (dentro de *Billing and Cost Management*).
2. Haga clic en **Create budget** (Crear presupuesto).
3. Elija **Use a template (simplified)** y la plantilla **Monthly cost budget**.
4. En **Budgeted amount** escriba `15` (dólares). En **Email recipients**, su correo.
5. Haga clic en **Create budget**. AWS avisará al llegar al 85 % y al 100 %.

## B.4 Paso 3: descargar la plantilla

1. Entre a <https://github.com/conEFE/Proyecto-Aurora/releases/tag/aws-consola>.
2. En **Assets**, haga clic en **aurora-aws.yaml**. Se descarga a la carpeta Descargas.
   No hace falta abrirlo.

## B.5 Paso 4: crear la pila en CloudFormation

1. En la consola de AWS, confirme la **región** (arriba a la derecha; ver B.2).
2. En la barra de búsqueda escriba **CloudFormation** y ábralo.
3. Haga clic en **Crear pila** (**Create stack**) y, si pregunta, **Con recursos nuevos (estándar)**.
4. **Paso «Especificar plantilla»:**
   - En **Preparar plantilla**, deje **Elegir una plantilla existente**.
   - En **Origen de la plantilla**, elija **Cargar un archivo de plantilla**.
   - Haga clic en **Elegir archivo**, seleccione **aurora-aws.yaml** de la carpeta Descargas y haga clic en
     **Siguiente**.
5. **Paso «Especificar los detalles de la pila»:**
   - **Nombre de la pila:** escriba `aurora` (minúsculas, sin espacios).
   - **Primer administrador:** RUT de prueba (por ejemplo `11111111-1`), nombre, correo y una **contraseña
     temporal** (al menos 10 caracteres, con letras y números, sin comillas). **Anótela.**
   - **Opciones:** deje todo como está. (*Tamaño del servidor*: `t4g.micro` basta para probar. *Dominio propio*:
     déjelo vacío; ver B.8.)
   - Haga clic en **Siguiente**.
6. **Paso «Configurar opciones de la pila»:** no cambie nada. Al final de la página, **marque la casilla**
   **«Reconozco que AWS CloudFormation podría crear recursos de IAM»** (es el permiso mínimo del servidor) y haga
   clic en **Siguiente**.
7. **Paso «Revisar y crear»:** haga clic en **Enviar** (**Submit**).

## B.6 Paso 5: esperar la instalación

1. Se abre la página de la pila **aurora** con el estado **CREATE_IN_PROGRESS** (creación en curso).
2. Espere entre **10 y 20 minutos**. Puede hacer clic en el botón de recarga (flecha circular) de vez en cuando.
   En la pestaña **Eventos** se ve el avance.
3. Cuando el estado cambie a **CREATE_COMPLETE** (en verde), la instalación terminó.
4. Abra la pestaña **Salidas** (**Outputs**). La fila **DireccionAurora** tiene la dirección de su Aurora, por
   ejemplo `https://3.145.10.20.sslip.io`. **Guárdela.**

> **Si el estado es ROLLBACK_IN_PROGRESS o ROLLBACK_COMPLETE**, algo falló y AWS deshizo lo creado. En la pestaña
> **Eventos** busque la primera fila en rojo (**CREATE_FAILED**) y lea la columna **Motivo del estado**; la tabla
> de B.10 explica los casos comunes. Luego elimine la pila (**Eliminar**) y repita B.5.

## B.7 Paso 6: primer ingreso

1. Abra en el navegador la dirección de **DireccionAurora**.
   - Si el navegador muestra un error de seguridad o de certificado, espere **1 a 2 minutos** y recargue: el
     certificado HTTPS se emite automáticamente en ese momento.
2. Haga clic en **Ingresar**, escriba el **RUT** y la **contraseña temporal** del paso B.5.5 y cambie la contraseña
   cuando Aurora lo pida.
3. Para crear más usuarios, siga **A.6** (es igual). En AWS los correos tampoco se envían: use **Asignar una
   contraseña temporal**. Si usa el link por correo, el link queda en los registros: en la consola abra
   **CloudWatch → Grupos de registros → /aurora/aurora**, entre al flujo que contiene **backend** y busque
   `Email (console)`.

## B.8 Opcional: usar un dominio propio

Si tiene un dominio (por ejemplo `aurora.miclinica.cl`):

1. Cree la pila como en B.5, pero escriba el dominio en **Dominio propio**.
2. Cuando termine, copie la **IpPublica** de la pestaña **Salidas**.
3. En el sitio donde administra su dominio (NIC Chile, Route 53, etc.), cree un registro **A** con el nombre del
   dominio y esa IP.
4. Espere a que el registro se propague (entre minutos y unas horas) y entre a `https://` + su dominio.

## B.9 Detener, reanudar o eliminar Aurora

- **Detener (pagar menos):** consola → **EC2 → Instancias** → seleccione **aurora-aurora** → **Estado de la
  instancia → Detener instancia**. Para volver a usarla: **Iniciar instancia** (Aurora arranca sola en 1 a 2
  minutos). Mientras está detenida, la IP y el disco siguen cobrando (unos USD 4,5 al mes).
- **Eliminar todo (dejar de pagar):**
  1. **CloudFormation → Pilas** → seleccione **aurora** → **Eliminar** → confirme. Se borran el servidor, la IP y
     los permisos.
  2. El **bucket S3** (imágenes y respaldos) se conserva a propósito, para no perder datos por error. Si quiere
     borrarlo: **S3 → Buckets** → el bucket cuyo nombre empieza con `aurora-databucket` → **Vaciar** (escriba
     *eliminar de forma permanente* para confirmar) → luego **Eliminar** (escriba el nombre del bucket).

## B.10 Problemas frecuentes (AWS)

| Qué pasa | Qué hacer |
|---|---|
| Al subir la plantilla aparece un error de parámetros | Revise el RUT (sin puntos, con guion), el correo y la contraseña (10 caracteres, letras y números, sin comillas ni `$`) |
| CREATE_FAILED en **Instance** con «not supported» o «Unsupported» | La región no ofrece ese tamaño de servidor. Repita B.5 eligiendo `t4g.small` o use otra región |
| CREATE_FAILED con «No default VPC» o «VPC» | La cuenta no tiene la red por defecto. Abra **VPC → Sus VPC → Acciones → Crear VPC predeterminada** y repita B.5 |
| CREATE_FAILED en **Instance** por «timeout» o «signal» | La instalación del servidor no terminó en 30 minutos. Vuelva a intentarlo; si se repite, vea los detalles abajo |
| La pila no se puede crear por permisos («not authorized») | Su usuario no tiene permisos para crear servidores o roles. Pida al administrador de la cuenta los permisos o que siga este manual |
| El navegador muestra error de certificado por más de 10 minutos | Revise que la dirección sea exactamente la de **Salidas** (con `https://`) |
| La página no carga después de iniciar una instancia detenida | Espere 2 minutos y recargue |
| De pronto todo da «Access Denied» | Puede que la cuenta llegó a un límite de gasto: revise **AWS Settings → Billing** o **Billing and Cost Management** |

> **Ver el detalle de la instalación (avanzado).** Consola → **EC2 → Instancias** → seleccione el servidor →
> **Conectar** → pestaña **Session Manager** → **Conectar**. Se abre una terminal en el navegador; escriba
> `sudo tail -n 50 /var/log/aurora-bootstrap.log` y presione Enter. Las últimas líneas indican en qué paso se
> detuvo.

## B.11 Seguridad y límites de esta instalación

- Las claves de la base de datos y de cifrado se generan dentro del servidor y no salen de él. El disco y el bucket
  están cifrados, y el servidor no acepta conexiones SSH (se administra con Session Manager).
- La contraseña temporal del administrador queda en la configuración de arranque del servidor, visible para
  quien administre la cuenta de AWS. Por eso Aurora obliga a cambiarla en el primer ingreso.
- La base de datos se respalda todos los días a las 03:15 (hora de Chile) en el bucket S3 (se guardan 35 días).
  La clave de cifrado de las imágenes está solo en el servidor: si se elimina la pila, las imágenes guardadas en
  el bucket ya no se podrán abrir.
- La IA es **simulada** y los correos no se envían. Es una instalación para pruebas y demostraciones con
  **datos ficticios**; **no** está preparada para datos reales de pacientes.

## B.12 Para el equipo de Aurora: instituciones en auroracare.cl

El equipo administra instituciones con dirección `<institución>.auroracare.cl` (por ejemplo
`hospital-x.auroracare.cl`) con la herramienta **aurora-admin**, que usa el proyecto de AWS del equipo y su
dominio:

1. Descargue `aurora-admin-windows.exe` desde
   <https://github.com/conEFE/Proyecto-Aurora/releases/tag/aurora-admin>.
2. Instale el AWS CLI desde <https://aws.amazon.com/cli/> (instalador para Windows, **Siguiente** en todo).
3. Abra `aurora-admin-windows.exe`. Si no hay sesión, ofrece iniciarla y abre el navegador para entrar con la
   cuenta del proyecto.
4. Ingrese la **clave de operador** (la primera vez, se define).
5. Elija **1. Inscribir una institución nueva**, escriba el identificador (por ejemplo `hospital-x`) y los datos
   del primer administrador, y confirme. Tarda entre 15 y 20 minutos.
6. La contraseña temporal del administrador se ve con la opción **7**. Entréguela por un canal privado.

El detalle de cada opción está en `deploy/aurora-admin/README.md`.

# Anexo: resumen en una página

**Local (Windows, prueba, IA simulada):** instalar Docker Desktop → descargar `AuroraSetup-2.12.0.exe` → «Más
información → Ejecutar de todas formas» → aceptar el aviso → RUT, nombre, correo y contraseña temporal → Instalar →
esperar 5 a 15 minutos → <http://localhost:8080> → Ingresar → cambiar la contraseña.

**AWS (consola, IA simulada):** crear la cuenta → (alerta de presupuesto) → descargar `aurora-aws.yaml` →
CloudFormation → Crear pila → Cargar archivo → nombre `aurora` y datos del administrador → marcar «Reconozco…» →
Enviar → esperar CREATE_COMPLETE (10 a 20 minutos) → pestaña Salidas → abrir **DireccionAurora** → Ingresar →
cambiar la contraseña. Para dejar de pagar: eliminar la pila y el bucket.

**La plataforma real, con el modelo de IA conectado: <https://demo.auroracare.cl>.**
