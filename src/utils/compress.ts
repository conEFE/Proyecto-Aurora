/**
 * Compresión opcional en el cliente (mitigación de INC-04: mamografías > 50 MB en redes lentas).
 *
 * Desactivada por defecto: re-codificar a JPEG pierde información. Se activa con
 * VITE_CLIENT_COMPRESSION=true y solo actúa sobre archivos mayores a VITE_COMPRESSION_THRESHOLD_MB.
 */

const ENABLED = import.meta.env.VITE_CLIENT_COMPRESSION === 'true';
const THRESHOLD_MB = Number(import.meta.env.VITE_COMPRESSION_THRESHOLD_MB || 20);
const MAX_SIDE = 4096;
const QUALITY = 0.92;

export const compressionEnabled = ENABLED;

export interface PreparedFile {
  blob: Blob;
  filename: string;
  compressed: boolean;
}

function loadImage(file: File): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      URL.revokeObjectURL(url);
      resolve(img);
    };
    img.onerror = (e) => {
      URL.revokeObjectURL(url);
      reject(e);
    };
    img.src = url;
  });
}

export async function prepareForUpload(file: File): Promise<PreparedFile> {
  if (!ENABLED || file.size <= THRESHOLD_MB * 1024 * 1024) {
    return { blob: file, filename: file.name, compressed: false };
  }
  const img = await loadImage(file);
  const scale = Math.min(1, MAX_SIDE / Math.max(img.width, img.height));
  const canvas = document.createElement('canvas');
  canvas.width = Math.round(img.width * scale);
  canvas.height = Math.round(img.height * scale);
  const ctx = canvas.getContext('2d');
  if (!ctx) return { blob: file, filename: file.name, compressed: false };
  ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
  const blob = await new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, 'image/jpeg', QUALITY));
  if (!blob || blob.size >= file.size) return { blob: file, filename: file.name, compressed: false };
  return { blob, filename: file.name.replace(/\.[^.]+$/, '') + '.jpg', compressed: true };
}
