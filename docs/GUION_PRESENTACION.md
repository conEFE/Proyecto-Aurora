# Guion de presentación de Aurora Care (≈ 20 minutos)

Sitio: https://demo.auroracare.cl. Todos los datos son ficticios.

**Antes de empezar (5 minutos antes):**
- PC de Juan encendido, sin suspensión, con Tailscale y el servicio del modelo arriba. Si no, la plataforma usa la IA
  simulada (badge «IA SIMULADA») y se dice en voz alta.
- Tres pestañas con sesión iniciada: **ADMIN**, **ADMINISTRATIVO** y el **médico de prueba** (`11111111-1`, que tiene
  los casos de demostración). Las contraseñas no van en este documento.
- Dos imágenes de prueba a mano: una masa benigna (`03_benigna_masa_…`) y una de calcificación (`07`–`10`).

| Min | Bloque | Quién habla |
|---|---|---|
| 0–2 | El problema y la idea | |
| 2–4 | Landing e ingreso | |
| 4–7 | Administración: usuarios y roles | |
| 7–11 | Admisión: paciente, consentimiento y caso con imágenes | |
| 11–16 | Médico: cola, caso, IA, revisión y firma | |
| 16–18 | Dashboard e informe de gestión | |
| 18–20 | Privacidad, seguridad y cierre | |

## 0–2 · El problema
- En atención primaria, una mamografía sospechosa puede esperar en la misma fila que un control de rutina.
- Aurora Care **ordena la espera por riesgo**, explica cada prioridad y **deja la decisión al médico**.

## 2–4 · Landing e ingreso
- Landing: el titular, la cola de triage y el carrusel de funciones (prioridad explicada, IA supervisada, lámina bilateral).
- «Ingresar»: RUT y contraseña. Mencionar el bloqueo tras 5 intentos y el cambio de contraseña obligatorio en el primer
  ingreso.

## 4–7 · Administración (pestaña ADMIN)
- Crear un usuario ADMINISTRATIVO con contraseña temporal. Mostrar que el ADMIN **no ve pacientes** (mínimo privilegio).
- Pestañas Auditoría (cada acción queda registrada) y Errores.

## 7–11 · Admisión (pestaña ADMINISTRATIVO)
- Pacientes → «Nuevo paciente»: RUT validado y consentimiento informado obligatorio.
- En la ficha: «Nuevo caso» → síntomas, BI-RADS informado e imágenes (varias a la vez; el lado se deduce del nombre).
- Al guardar, el caso entra a la cola **ya priorizado**. El administrativo ve solo código, nivel y espera.

## 11–16 · Médico (pestaña médico de prueba)
- **Cola de triage:** los ALTA arriba; el aviso del caso fuera de plazo; filtros por nivel.
- Abrir el caso recién creado (o uno de demostración):
  - Lámina bilateral D/I con las vistas de cada lado; la imagen con las cajas de la IA.
  - Resultado de la IA: probabilidad de malignidad de la CNN y masa marcada por YOLO, con badge **PROTOTIPO**.
  - «Por qué tiene este nivel»: regla de escalamiento o puntaje por factores.
- Flujo de revisión: «Tomar caso» → validar el resultado de IA de cada imagen (concordante / falso positivo / no
  evaluable) → registrar la revisión (BI-RADS final y recomendación) → firmar → descargar el reporte PDF.
- Opcional: «Cambiar nivel» con motivo (queda en la historia y en la auditoría).
- Pacientes → la ficha muestra la **historia**: registro, consentimiento, casos, revisión y cierre.

## 16–18 · Dashboard
- Indicadores con meta (creación → triage, ALTA pendientes > 24 h, tiempo de respuesta), casos por nivel y por semana.
- Calidad de las decisiones: concordancia IA–médico y aprobación del triage.
- «Exportar informe PDF»: el informe de gestión con relato.

## 18–20 · Privacidad, seguridad y cierre
- Privacidad: consentimiento, bloqueo y solicitudes de los titulares (Leyes 19.628 y 21.719).
- Seguridad: imágenes cifradas, bitácora de solo agregar, HTTPS con dominio propio y despliegue en AWS.
- Cierre: **la plataforma apoya, no reemplaza, el criterio médico**. Próximos pasos: validación clínica del modelo,
  pruebas de carga y DICOM.

## Si algo falla
- El modelo no responde: el resultado sale con «IA SIMULADA»; explicarlo como el respaldo previsto.
- La subida es lenta: el modelo va por un relay de Tailscale (~15 s por imagen). Usar un caso de demostración ya
  analizado.
