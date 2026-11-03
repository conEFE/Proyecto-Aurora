import type { TriageLevel } from './types';

export const LEVEL_STYLES: Record<TriageLevel, string> = {
  ALTA: 'bg-red-500/15 text-red-400 border-red-500/30',
  MEDIA: 'bg-orange-500/15 text-orange-400 border-orange-500/30',
  BAJA: 'bg-green-500/15 text-green-400 border-green-500/30',
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
