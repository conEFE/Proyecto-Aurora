import type { CaseStatus, TriageLevel } from '../types';
import { CASE_STATUS_LABELS } from '../types';
import { LEVEL_STYLES } from '../constants';

const STATUS_STYLES: Record<CaseStatus, string> = {
  ABIERTO: 'bg-slate-500/10 text-slate-300 border-slate-500/30',
  PRIORIZADO: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  EN_REVISION: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
  CERRADO: 'bg-green-500/10 text-green-400 border-green-500/20',
};


export function StatusBadge({ status }: { status: CaseStatus }) {
  return (
    <span className={`px-2 py-0.5 text-[10px] font-semibold rounded border ${STATUS_STYLES[status]}`}>
      {CASE_STATUS_LABELS[status]}
    </span>
  );
}

export function LevelBadge({ level }: { level?: TriageLevel | null }) {
  if (!level) return <span className="text-[10px] text-muted-foreground">Sin triage</span>;
  return (
    <span className={`px-2 py-0.5 text-[10px] font-bold rounded border ${LEVEL_STYLES[level]}`}>{level}</span>
  );
}

/** Marca obligatoria en todo resultado del proveedor de IA simulado. */
export function SimulatedBadge() {
  return (
    <span
      className="inline-flex items-center px-2 py-0.5 text-[10px] font-bold rounded border bg-amber-500/15 text-amber-300 border-amber-500/40 tracking-wide"
      title="Resultado generado por un proveedor simulado. No es un resultado clínico real."
    >
      IA SIMULADA
    </span>
  );
}
