# Traspaso: grabar los bloques 6, 7 y 8 del video de Aurora Care en el PC de Felipe

Eres un agente de Claude Code que corre **en el PC con Windows de Felipe**, dentro de su copia del repositorio
`conEFE/Proyecto-Aurora`. Tu tarea es grabar las partes del video que no se pudieron grabar desde la nube y unirlas
al video que ya existe. Habla con Felipe en español y con frases cortas.

## Contexto
- Aurora Care es una plataforma de triage de cáncer de mama (proyecto de título INACAP). Está publicada en
  https://demo.auroracare.cl, en AWS (proyecto `527518120225`, región **us-east-2**).
- El guion de la parte de Felipe está en **`docs/GUION_VIDEO_ADMIN_NUBE.md`**. Antes de empezar, ejecuta
  `git pull` en `main` y léelo completo.
- Los bloques 1 a 5 (la plataforma web) ya están grabados y unidos en **`aurora-admin-completo.mp4`**: 4:38,
  1920×1080, 30 fps, H.264, tema oscuro, **sin audio**. Pídele a Felipe la ruta donde lo guardó.
- Felipe pone su voz después, en un editor. Por eso cada clip debe durar lo que dura su texto, leído a
  **≈ 5 palabras por segundo**, y respetar las pausas marcadas.

## Qué falta grabar

### Bloque 6: el instalador aurora-admin (≈ 64 s)
En pantalla: `aurora-admin-windows.exe`, descargado de
https://github.com/conEFE/Proyecto-Aurora/releases/tag/aurora-admin. Necesita el AWS CLI y una sesión iniciada.

| Segundos | Qué pasa | En pantalla |
|---|---|---|
| 0 – 13 | Habla (por qué existe el instalador) | Abrir el .exe |
| 13 – 18 | Pausa | **Felipe** escribe la clave de operador; queda en el menú |
| 18 – 28 | Habla (la clave y el menú) | Menú visible; el cursor recorre las opciones |
| 28 – 33 | Pausa | Elegir la opción 1 (versión A) o la 2 (versión B) |
| 33 – 59 | Habla (qué crea «Inscribir») | Versión A: el formulario y el progreso. Versión B: el listado de instituciones o la opción 9 |
| 59 – 64 | Pausa | Dejar ver el resultado o el menú |

- **Versión A** (inscribir la institución `prueba`): crea recursos reales en AWS (≈ USD 10 al mes) y tarda 15–20 min.
  **Pide confirmación explícita a Felipe antes de ejecutar la opción 1.** Graba solo el inicio. Corta mientras
  espera. Luego graba `https://prueba.auroracare.cl` abierta y la opción 2. Al terminar, recuérdale **darla de baja
  con la opción 8**. Esta prueba nunca se ha hecho de punta a punta: si falla, no improvises arreglos en AWS. Anota
  el error para Felipe y usa la versión B.
- **Versión B** (sin crear nada): mostrar el menú y la opción 2 o la 9.
- Datos del primer ADMIN en la versión A: **solo ficticios** (por ejemplo, RUT `39000004-9`, «Admin Prueba»,
  `admin.prueba@aurora-demo.cl`).

### Bloque 7: la nube y el dominio (≈ 49 s)
En pantalla: la consola de AWS en us-east-2.

| Segundos | Qué pasa | En pantalla |
|---|---|---|
| 0 – 27 | Habla (servidor, contenedores, cifrado, respaldos, costo) | EC2 → Instancias → `aurora-prod`, con detalle y estado |
| 27 – 32 | Pausa | Cambiar a Route 53 |
| 32 – 49 | Habla (dominio, NIC Chile, subdominios, certificado, IA aparte) | Route 53 → zona `auroracare.cl` → registro `demo` |

### Bloque 8: cierre (≈ 10 s)
En pantalla: https://demo.auroracare.cl, la landing o el resumen de Administración. Un plano quieto con un leve
movimiento del cursor basta.

## Cómo grabar
- **Navegador (bloques 7 y 8):** usa Playwright con Chrome **visible** y un perfil persistente
  (`launchPersistentContext`).
  - Ventana de 1600×900 con `deviceScaleFactor: 1.2`, para obtener 1920×1080.
  - `colorScheme: 'dark'`. Para Aurora, además `localStorage.aurora_theme = 'dark'`.
  - **Felipe inicia sesión en AWS a mano en esa ventana.** Tú nunca escribes ni ves sus credenciales. Aurora usa su
    cuenta de administrador, que también ingresa él.
  - Captura los cuadros con CDP `Page.startScreencast` (JPEG, calidad 92, `maxWidth` 1920). Arma el video con
    ffmpeg usando la marca de tiempo de cada cuadro (concat con `duration`), a 30 fps, `libx264 -crf 18
    -pix_fmt yuv420p`.
  - Playwright no dibuja el mouse. Inyecta un cursor falso (un `div` fijo con una flecha blanca de borde negro que
    siga a `mousemove`) y mueve el mouse con `page.mouse.move(x, y, { steps })` para que se vea suave.
  - Sincroniza con **marcas absolutas**: espera hasta el segundo N del clip, no esperas relativas.
- **El .exe (bloque 6):** es una ventana de consola. Grábala con
  `ffmpeg -f gdigrab -framerate 30 -draw_mouse 1 -i title="<título de la ventana>"` (o la pantalla completa) y
  escala o rellena a 1920×1080. Pon la consola en fondo oscuro y con letra grande (≈ 20 pt). Felipe escribe la clave
  de operador; si se ve algo en pantalla al escribirla, corta ese tramo.

## Qué no debe verse en el video
- La clave de operador, contraseñas, `deploy/.env` o valores de Parameter Store (`/aurora/...`).
- El **ID de la cuenta de AWS** y el correo de Felipe en la barra superior de la consola: difumínalos con CSS
  (`filter: blur(7px)`) sobre esos elementos, o recorta.
- El RUT real de Felipe. En los bloques 1 a 5 se difuminó; mantén ese criterio.
- Datos reales de personas: solo datos ficticios.

## Entregables
1. `bloque-6-instalador.mp4`, `bloque-7-nube.mp4` y `bloque-8-cierre.mp4`, en 1920×1080, 30 fps, H.264, sin audio.
2. **`aurora-video-felipe-completo.mp4`**: `aurora-admin-completo.mp4` + los bloques 6, 7 y 8. Si los parámetros
   coinciden, únelos con `ffmpeg -f concat -c copy`; si no, re-codifica todo igual. Deberían ser ≈ 6:40.
3. Revisa cuadros de cada clip (extrae algunos con ffmpeg y míralos) antes de entregar. Confirma que no se vea
   nada de la lista anterior.

## Reglas del proyecto que aplican
- No cambies código ni infraestructura para el video. Si algo de AWS se ve mal o falla, avísale a Felipe.
- No subas los videos al repositorio. Guárdalos en una carpeta fuera de git, o en `video-guion/`, que ya está
  excluida.
- Commits, si los hay (por ejemplo, ajustes al guion): en `main`, con la autoría de Felipe y **sin coautoría de
  Claude**.
- Si la institución de prueba se creó, al final recuerda darla de baja (opción 8) para que no siga cobrando.
