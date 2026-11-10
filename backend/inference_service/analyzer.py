"""Ejecuta la CNN (probabilidad de malignidad) y YOLO (ubicación de masas) sobre una mamografía."""

import os
import threading
import time

import torch
import torch.nn as nn
from torchvision import models
from ultralytics import YOLO

from preprocessing import for_cnn, for_yolo, read_image

WEIGHTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weights")
CNN_PATH = os.path.join(WEIGHTS_DIR, "cnn_proporcion.pt")
YOLO_PATH = os.path.join(WEIGHTS_DIR, "yolo_masas.pt")

CNN_THRESHOLD = 0.35  # punto de operación: sensibilidad 0,849 en el conjunto de prueba
YOLO_CONF = 0.25  # confianza mínima para entregar una caja
YOLO_MASS_CLASS = 0  # el modelo tiene dos clases (masa, calcificación); solo se usa masa
MODEL_VERSION = "cnn-resnet18-672x1024+yolo11s-masa-1280"

DEVICE = os.environ.get("INFERENCE_DEVICE") or ("cuda:0" if torch.cuda.is_available() else "cpu")


class GrayResNet(nn.Module):
    """Misma arquitectura que en entrenar_cnn.py; los nombres internos deben coincidir con los pesos."""

    def __init__(self):
        super().__init__()
        self.base = models.resnet18(weights=None)
        self.base.conv1 = nn.Conv2d(1, 64, 7, stride=2, padding=3, bias=False)
        self.base.fc = nn.Sequential(nn.Dropout(0.4), nn.Linear(self.base.fc.in_features, 1))

    def forward(self, x):
        return self.base(x.float() / 255.0).squeeze(1)


class Analyzer:
    def __init__(self):
        self.cnn = GrayResNet()
        self.cnn.load_state_dict(torch.load(CNN_PATH, map_location=DEVICE))
        self.cnn.to(DEVICE).eval()
        self.yolo = YOLO(YOLO_PATH)
        self.lock = threading.Lock()  # el modelo de Ultralytics no es seguro entre hilos

    def analyze(self, content: bytes) -> dict:
        start = time.perf_counter()
        gray = read_image(content)
        yolo_img = for_yolo(gray)

        with self.lock:
            x = torch.from_numpy(for_cnn(gray))[None, None].to(DEVICE)
            with torch.no_grad():
                probability = torch.sigmoid(self.cnn(x)).item()
            result = self.yolo.predict(
                yolo_img, imgsz=1280, conf=YOLO_CONF, classes=[YOLO_MASS_CLASS],
                device=DEVICE, verbose=False,
            )[0]

        height, width = yolo_img.shape[:2]
        detections = []
        for (x1, y1, x2, y2), conf in zip(result.boxes.xyxy.tolist(), result.boxes.conf.tolist()):
            w, h = (x2 - x1) / width, (y2 - y1) / height
            detections.append({
                "x": round(x1 / width, 4),
                "y": round(y1 / height, 4),
                "width": round(w, 4),
                "height": round(h, 4),
                "confidence": round(conf, 4),
                "class_name": "masa",
                "relative_area": round(w * h, 4),
            })
        detections.sort(key=lambda d: d["confidence"], reverse=True)

        detected = probability >= CNN_THRESHOLD
        position = "sobre" if detected else "bajo"
        message = (
            f"Probabilidad de malignidad {probability * 100:.1f}% "
            f"({position} el umbral de {CNN_THRESHOLD * 100:.0f}%). "
        )
        message += f"Masas marcadas: {len(detections)}." if detections else "No se marcaron masas."

        return {
            "detected": detected,
            "confidence": round(probability * 100, 2),
            "probability": round(probability, 4),
            "threshold": CNN_THRESHOLD,
            "detections": detections,
            "processing_time_ms": int((time.perf_counter() - start) * 1000),
            "model_version": MODEL_VERSION,
            "is_simulated": False,
            "message": message,
        }
