import type { CaseStatus, TriageLevel } from '../types';
import { CASE_STATUS_LABELS } from '../types';
import { LEVEL_FILL, LEVEL_LABELS, LEVEL_RING, LEVEL_TEXT } from '../constants';
import { cn } from '../lib/cn';

const STATUS_DOT: Record<CaseStatus, string> = {
  ABIERTO: 'bg-muted-foreground',
  PRIORIZADO: 'bg-info',
  EN_REVISION: 'bg-media',
  CERRADO: 'bg-baja',
};

export function StatusBadge({ status }: { status: CaseStatus }) {
  return (
    <span className="inline-flex items-center gap-1.5 text-sm text-foreground">
      <span aria-hidden className={cn('w-2 h-2 rounded-full', STATUS_DOT[status])} />
      {CASE_STATUS_LABELS[status]}
    </span>
  );
}

/** Timbre de prioridad: anillo cuyo grosor sube con la urgencia, más el nombre del nivel. */
export function LevelBadge({ level, size = 'md' }: { level?: TriageLevel | null; size?: 'md' | 'lg' }) {
  if (!level) return <span className="text-sm text-muted-foreground">Sin triage</span>;
  return (
    <span
      className={cn(
        'relative inline-flex items-center gap-1.5 font-extrabold tracking-wide',
        size === 'lg' ? 'text-base' : 'text-xs',
        LEVEL_TEXT[level],
      )}
    >
      <span
        aria-hidden
        className={cn('rounded-full border-current', size === 'lg' ? 'w-5 h-5' : 'w-3.5 h-3.5', LEVEL_RING[level])}
      />
      {level}
      <span className="sr-only">(prioridad {LEVEL_LABELS[level].toLowerCase()})</span>
    </span>
  );
}

/** Marca obligatoria en todo resultado de un modelo real sin validación clínica (prototipo). */
export function PrototypeBadge() {
  return (
    <span
      className="inline-flex shrink-0 whitespace-nowrap items-center px-2 py-0.5 text-xs font-extrabold rounded-md border border-proto/50 bg-[hsl(var(--proto-bg))] text-proto tracking-wide"
      title="Resultado de un modelo de IA en etapa de prototipo, sin validación clínica. No es un diagnóstico."
    >
      MODELO PROTOTIPO — NO VALIDADO
    </span>
  );
}

/** Badge según el origen del resultado: IA simulada o modelo prototipo (un modelo validado no lleva marca). */
export function AiOriginBadge({ isSimulated, clinicallyValidated }: { isSimulated: boolean; clinicallyValidated?: boolean }) {
  if (isSimulated) return <SimulatedBadge />;
  if (!clinicallyValidated) return <PrototypeBadge />;
  return null;
}

/** Marca obligatoria en todo resultado del proveedor de IA simulado. */
export function SimulatedBadge() {
  return (
    <span
      className="inline-flex shrink-0 whitespace-nowrap items-center px-2 py-0.5 text-xs font-extrabold rounded-md border border-sim/50 bg-[hsl(var(--sim-bg))] text-sim tracking-wide"
      title="Resultado generado por un proveedor simulado. No es un resultado clínico real."
    >
      IA SIMULADA
    </span>
  );
}

/** Barra de puntaje sobre la escala fija 0–100. */
export function ScoreBar({ score, level }: { score?: number | null; level?: TriageLevel | null }) {
  if (score == null) return <span className="text-muted-foreground">—</span>;
  const pct = Math.max(0, Math.min(100, score));
  return (
    <span className="inline-flex items-center gap-2.5">
      <span aria-hidden className="relative w-24 h-1.5 rounded-full bg-muted overflow-hidden">
        <span
          className={cn('absolute inset-y-0 left-0 rounded-full', level ? LEVEL_FILL[level] : 'bg-brand')}
          style={{ width: `${pct}%` }}
        />
      </span>
      <span className="tabular-nums font-semibold">{Math.round(score)}</span>
    </span>
  );
}
