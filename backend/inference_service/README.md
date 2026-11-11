# Servicio de inferencia de Aurora (prototipo)

Servicio aparte del backend que analiza una mamografía con dos modelos y le devuelve el resultado
al backend, en lugar de la IA simulada.

- **CNN (ResNet18):** calcula la probabilidad de malignidad. Si es 0,35 o más, la imagen se marca como
  sospechosa (`detected = true`). Esta probabilidad es la que usa el triage.
- **YOLO (yolo11s):** ubica las masas y entrega su caja. No detecta calcificaciones.

No es un modelo clínico validado: es un prototipo para probar el flujo completo de la plataforma. Por eso cada
resultado lleva `clinically_validated = false` y la plataforma lo muestra con el aviso
**«MODELO PROTOTIPO — NO VALIDADO»**, en pantalla y en el PDF.

**Dónde corre:** en el PC de un integrante con GPU, y la plataforma en AWS lo alcanza por Tailscale (opción B,
`docs/inferencia_remota.md`). El mismo contenedor corre en AWS con CPU: para moverlo solo cambia `INFERENCE_URL`.

## Cómo encaja con la plataforma

La plataforma no necesita cambios de código. El backend ya trae un cliente para este servicio
(`backend/app/inference/providers.py`); solo hay que activarlo en el `.env`.

```
Frontend (5173)  →  Backend (8000)  →  Servicio de inferencia (8080)
```

Cuando se sube una mamografía a un caso, el backend le manda la imagen al servicio, guarda la respuesta en
`inference_results` y recalcula la prioridad del caso.

## Requisitos

- Windows, Python 3.12.
- El backend ya instalado y funcionando con su entorno `backend\venv`.
- GPU NVIDIA con el driver actualizado (opcional: sin GPU funciona en CPU, más lento).

## 1. Instalar (una sola vez)

En una terminal (cmd), desde la carpeta del proyecto:

```
cd backend
venv\Scripts\activate
pip install torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu124
pip install -r inference_service\requirements.txt
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

La última línea debe mostrar `2.6.0+cu124 True`.

Sin GPU NVIDIA, cambia la primera línea `pip install` por esta (instala la versión para CPU):

```
pip install torch==2.6.0 torchvision==0.21.0
```

## 2. Configurar el backend (una sola vez)

Genera un token (el mismo valor va en la plataforma y en el servicio):

```
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Abre `backend\.env` y busca la línea `INFERENCE_PROVIDER`. Viene en `simulated` (así está en `.env.example`).
Cámbiala a `http`. Modifica las líneas que ya existen, no agregues otras. Debe quedar así:

```
INFERENCE_PROVIDER=http
INFERENCE_URL=http://localhost:8080
INFERENCE_API_TOKEN=<el token>
INFERENCE_FALLBACK_SIMULATED=true
```

Antes de levantar el servicio (terminal 1), define el mismo token en esa terminal: `set INFERENCE_API_TOKEN=<el token>`.
Con `INFERENCE_FALLBACK_SIMULATED=true`, si el servicio está apagado la plataforma usa la IA simulada (marcada) y el
médico puede volver a analizar la imagen después con el botón «Analizar con el modelo».

Para volver a la IA simulada, deja `INFERENCE_PROVIDER=simulated` y reinicia el backend.

## 3. Levantar todo (cada vez que se prueba)

Se necesitan tres terminales y el orden importa: el servicio tiene que estar arriba antes de subir imágenes.

**Terminal 1, servicio de inferencia:**

```
cd backend
venv\Scripts\activate
cd inference_service
uvicorn app:app --host 0.0.0.0 --port 8080
```

`--host 0.0.0.0` permite que la plataforma en AWS llegue por Tailscale. Protege el puerto con la regla del firewall
de `docs/guia_modelo_juan.md` (paso 4): solo direcciones de Tailscale (`100.64.0.0/10`).

Espera a que aparezca `Application startup complete` y abre <http://localhost:8080/health>.
Debe mostrar `"device": "cuda:0"` (o `"cpu"` si no hay GPU).

**Terminal 2, backend:**

```
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

Si el backend ya estaba corriendo antes de cambiar el `.env`, ciérralo (Ctrl+C) y vuelve a levantarlo.
El `.env` solo se lee al arrancar y `--reload` no reacciona a cambios en el `.env`.

**Terminal 3, frontend:**

```
npm run dev
```

## 4. Probar

1. Entra a la plataforma con un usuario médico, abre un caso (o crea uno) y sube una mamografía.
2. El análisis toma alrededor de un segundo con GPU y el resultado aparece en el caso.
3. Para confirmar que analizó el modelo real, mira la terminal 1: por cada imagen subida debe aparecer una línea
   `POST /predict` con `200 OK`. Si no aparece, el backend sigue en modo simulado: revisa el paso 2 y reinicia
   el backend. El aviso "IA SIMULADA" del frontend no sirve para esto, porque aparece siempre
   (ver pendientes del frontend).

Cada análisis queda en la tabla `inference_results` con `is_simulated = false` y
`model_version = cnn-resnet18-672x1024+yolo11s-masa-1280`.

También se puede probar el servicio solo, sin la plataforma: en <http://localhost:8080/docs>, abre
`POST /predict`, presiona "Try it out", elige una imagen y presiona "Execute".

### Qué imágenes usar

- Usar mamografías **originales** en PNG o JPEG. El backend todavía no acepta DICOM, aunque el servicio sí lo lee.
- No usar imágenes ya procesadas con CLAHE: el servicio lo aplica y quedaría aplicado dos veces.
- Las imágenes de los datasets no se suben al repositorio.

### Importante

- **Si el servicio estaba apagado al subir la imagen**, la plataforma usa la IA simulada (marcada). Cuando el servicio
  vuelva, el médico usa **«Analizar con el modelo»** en la imagen (`POST /cases/{id}/images/{id}/inference/retry`).
  No se reemplazan resultados que el médico ya validó.
- `GET /inference/status` en la plataforma dice si el modelo está conectado (sin datos de pacientes).

## Qué responde el servicio

| Campo | Contenido |
|---|---|
| `detected` | `true` si la probabilidad de la CNN es 0,35 o más |
| `confidence` | probabilidad de la CNN, de 0 a 100 (la usa el triage como factor IA) |
| `probability` | la misma probabilidad, de 0 a 1 |
| `detections` | cajas de masa de YOLO: `x`, `y` (esquina superior izquierda), `width`, `height` (de 0 a 1 respecto a la imagen), `confidence`, `class_name`, `relative_area` |
| `model_version`, `processing_time_ms`, `is_simulated`, `message` | datos del análisis |
| `clinically_validated` | `false`: el modelo no tiene validación clínica (la plataforma muestra el aviso de prototipo) |

`GET /health` responde `status`, `model_version`, `device` y `clinically_validated`. Ambas rutas exigen
`Authorization: Bearer <INFERENCE_API_TOKEN>` cuando el token está definido.

## Si algo falla

| Síntoma | Causa y solución |
|---|---|
| `ModuleNotFoundError` al levantar el servicio | El entorno no está activado: `venv\Scripts\activate` desde `backend`. |
| `/health` muestra `cpu` teniendo GPU NVIDIA | Se instaló torch sin CUDA. Repite la línea de torch del paso 1 (con `--index-url`). |
| Se sube una imagen y en la terminal 1 no aparece `POST /predict` | `INFERENCE_PROVIDER` sigue en `simulated` o no se reinició el backend (paso 2 y terminal 2). |
| La imagen queda sin resultado | El servicio estaba apagado al subirla. Levántalo y sube la imagen de nuevo. |
| El servicio responde 415 | El formato del archivo no es una imagen que pueda leer (usar PNG o JPEG). |

## Rendimiento medido (conjunto de prueba, división por paciente)

- **CNN:** AUC 0,838 (CBIS-DDSM 0,841; CMMD 0,807). Con umbral 0,35: sensibilidad 0,849, especificidad 0,641.
- **YOLO, masas:** mAP50 0,538.

## Con Docker (misma imagen en el PC con GPU y en AWS con CPU)

En el PC con GPU NVIDIA (Docker Desktop con WSL2 en Windows), desde `backend/inference_service`, con un archivo
`.env` que tenga `INFERENCE_API_TOKEN=<el token>`:

```
docker compose -f docker-compose.gpu.yml --env-file .env up -d --build
```

En AWS (CPU) se usa la imagen `-inference` que publica GitHub Actions y el perfil `inference` del
`docker-compose.yml` de la raíz (ver `docs/inferencia_remota.md`, «Mover el modelo a AWS»).

## Resuelto en la plataforma (2.6.0)

- Las cajas se dibujan sobre la imagen real (el contenedor se ajusta a la mamografía), y también cuando la CNN no
  supera el umbral: YOLO marca masas aparte.
- Textos actualizados: la carga indica si el modelo está conectado, y los resultados llevan «IA SIMULADA» o
  «MODELO PROTOTIPO — NO VALIDADO» según su origen.
- Reintento del análisis cuando el modelo estaba apagado.

## Limitaciones conocidas

- Entrenado con CBIS-DDSM y CMMD, que no tienen mamografías sanas: prioriza entre casos con hallazgo.
- YOLO no detecta calcificaciones; en esos casos la prioridad sale solo de la CNN.
