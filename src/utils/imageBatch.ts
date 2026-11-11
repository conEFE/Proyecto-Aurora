import { apiClient } from '../services/api';
import type { ExamType, Laterality } from '../types';
import { compressionEnabled, prepareForUpload } from './compress';

export const MAX_UPLOAD_MB = Number(import.meta.env.VITE_MAX_UPLOAD_MB || 60);

export interface PendingImage {
  key: string;
  file: File;
  laterality: Laterality | '';
  examType: ExamType;
}

/** Deduce el lado desde nombres habituales: R_CC, LMLO, derecha, izq, right, left… */
export function guessLaterality(filename: string): Laterality | '' {
  const name = ` ${filename.toUpperCase().replace(/\.[A-Z0-9]+$/, '').replace(/[^A-Z0-9]+/g, ' ')} `;
  if (/ (R|D|RCC|RMLO|DER|DERECHA|RIGHT) |(^| )R(CC|MLO)/.test(name)) return 'R';
  if (/ (L|I|LCC|LMLO|IZQ|IZQUIERDA|LEFT) |(^| )L(CC|MLO)/.test(name)) return 'L';
  return '';
}

let counter = 0;

export function toPending(files: FileList | File[], examType: ExamType = 'MAMOGRAFIA'): {
  items: PendingImage[];
  rejected: string[];
} {
  const items: PendingImage[] = [];
  const rejected: string[] = [];
  for (const file of Array.from(files)) {
    if (!['image/png', 'image/jpeg'].includes(file.type)) rejected.push(`${file.name}: use PNG o JPEG`);
    else if (!compressionEnabled && file.size > MAX_UPLOAD_MB * 1024 * 1024)
      rejected.push(`${file.name}: supera ${MAX_UPLOAD_MB} MB`);
    else items.push({ key: `${Date.now()}-${counter++}`, file, laterality: guessLaterality(file.name), examType });
  }
  return { items, rejected };
}

/** Sube las imágenes una por una al caso. Devuelve los nombres que fallaron. */
export async function uploadBatch(
  caseId: number,
  items: PendingImage[],
  onProgress: (index: number, percent: number) => void,
): Promise<string[]> {
  const failed: string[] = [];
  for (const [i, item] of items.entries()) {
    const prepared = await prepareForUpload(item.file);
    const r = await apiClient.uploadImage(
      caseId,
      prepared.blob,
      prepared.filename,
      { exam_type: item.examType, laterality: item.laterality || null },
      (p) => onProgress(i, p),
    );
    if (!r.data) failed.push(`${item.file.name}: ${r.error || 'error al subir'}`);
  }
  return failed;
}
