"""Lectura y estandarización de la mamografía, idéntica a la usada en el entrenamiento."""

import io

import cv2
import numpy as np
import pydicom

CNN_WIDTH, CNN_HEIGHT = 672, 1024
YOLO_LONG_SIDE = 1280


def _clahe(img: np.ndarray) -> np.ndarray:
    return cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(img)


def read_image(content: bytes) -> np.ndarray:
    """Devuelve la imagen en escala de grises de 8 bits, venga en PNG, JPEG o DICOM."""
    img = cv2.imdecode(np.frombuffer(content, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
    if img is not None:
        return img
    try:
        ds = pydicom.dcmread(io.BytesIO(content), force=True)
        img = ds.pixel_array
    except Exception as exc:
        raise ValueError("El archivo no es una imagen PNG, JPEG ni DICOM válida") from exc
    if img.ndim != 2:
        raise ValueError("Solo se aceptan DICOM de una imagen en escala de grises")
    if str(getattr(ds, "PhotometricInterpretation", "")) == "MONOCHROME1":
        img = img.max() - img
    if img.dtype != np.uint8:
        img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return img


def for_cnn(gray: np.ndarray) -> np.ndarray:
    """CLAHE, ajuste a 672 x 1024 sin deformar y relleno negro centrado."""
    img = _clahe(gray)
    h, w = img.shape
    scale = min(CNN_WIDTH / w, CNN_HEIGHT / h)
    interp = cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR
    img = cv2.resize(img, (round(w * scale), round(h * scale)), interpolation=interp)
    canvas = np.zeros((CNN_HEIGHT, CNN_WIDTH), dtype=np.uint8)
    nh, nw = img.shape
    y0, x0 = (CNN_HEIGHT - nh) // 2, (CNN_WIDTH - nw) // 2
    canvas[y0:y0 + nh, x0:x0 + nw] = img
    return canvas


def for_yolo(gray: np.ndarray) -> np.ndarray:
    """CLAHE y lado mayor a 1280 sin deformar; YOLO recibe tres canales, como al entrenar."""
    img = _clahe(gray)
    h, w = img.shape
    scale = YOLO_LONG_SIDE / max(h, w)
    if scale < 1:
        img = cv2.resize(img, (round(w * scale), round(h * scale)), interpolation=cv2.INTER_AREA)
    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
