# Servicio de inferencia (CNN + YOLO). La misma imagen sirve para el PC con GPU y para AWS con CPU:
#   GPU (CUDA 12.4): docker build --build-arg TORCH_INDEX=https://download.pytorch.org/whl/cu124 -t aurora-inference:gpu .
#   CPU (AWS):       docker build -t aurora-inference:cpu .
FROM public.ecr.aws/docker/library/python:3.12.16-slim

ARG TORCH_INDEX=https://download.pytorch.org/whl/cpu
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1 \
    YOLO_CONFIG_DIR=/tmp/ultralytics

# Bibliotecas que necesita OpenCV en modo headless
RUN apt-get update && apt-get install -y --no-install-recommends libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN pip install torch==2.6.0 torchvision==0.21.0 --index-url "$TORCH_INDEX"
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY analyzer.py app.py preprocessing.py ./
COPY weights ./weights

RUN useradd --system --uid 10002 --home /app inference && chown -R inference:inference /app
USER inference

ENV ENABLE_API_DOCS=false
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import os,urllib.request,sys; r=urllib.request.Request('http://127.0.0.1:8080/health', headers={'Authorization': 'Bearer ' + os.environ.get('INFERENCE_API_TOKEN','')}); sys.exit(0 if urllib.request.urlopen(r, timeout=4).status == 200 else 1)"
# Un solo worker: los modelos se cargan una vez en memoria (cada worker los cargaría de nuevo)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1", "--no-server-header"]
