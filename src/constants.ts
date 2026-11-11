import type { TriageLevel } from './types';

/** Color del timbre de cada nivel (texto y anillo). Una sola escala en toda la app. */
export const LEVEL_TEXT: Record<TriageLevel, string> = {
  ALTA: 'text-alta',
  MEDIA: 'text-media',
  BAJA: 'text-baja',
};

/** Grosor del anillo del timbre: más grueso cuanto más urgente. */
export const LEVEL_RING: Record<TriageLevel, string> = {
  ALTA: 'border-[3.5px]',
  MEDIA: 'border-[2.5px]',
  BAJA: 'border-[1.5px]',
};

export const LEVEL_FILL: Record<TriageLevel, string> = {
  ALTA: 'bg-alta',
  MEDIA: 'bg-media',
  BAJA: 'bg-baja',
};

export const LEVEL_LABELS: Record<TriageLevel, string> = {
  ALTA: 'Alta',
  MEDIA: 'Media',
  BAJA: 'Baja',
};

export const BIRADS_LABELS: Record<number, string> = {
  0: '0 — Incompleto',
  1: '1 — Negativo',
  2: '2 — Benigno',
  3: '3 — Probablemente benigno',
  4: '4 — Sospechoso',
  5: '5 — Altamente sugestivo de malignidad',
  6: '6 — Malignidad confirmada por biopsia',
};
