import type { ReactNode } from 'react';
import { ChevronLeft } from 'lucide-react';
import { cn } from '../lib/cn';
import { ghostButton, pageTitle } from './ui';

/** Encabezado de una lista (como Casos y Pacientes): título a la izquierda y acción principal a la derecha. */
export function ListHeader({ title, actions }: { title: string; actions?: ReactNode }) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-4">
      <h1 className={pageTitle}>{title}</h1>
      {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
    </div>
  );
}

interface DetailHeaderProps {
  /** Texto del enlace para volver (p. ej., «Pacientes»). Sin él, no se muestra. */
  backLabel?: string;
  onBack?: () => void;
  title: ReactNode;
  /** Estado junto al título (texto corto con color). */
  status?: ReactNode;
  /** Línea de datos bajo el título. */
  meta?: ReactNode;
  actions?: ReactNode;
}

/** Encabezado de una ficha o página propia: volver, título grande, estado, datos y acciones, cerrado por una regla. */
export function DetailHeader({ backLabel, onBack, title, status, meta, actions }: DetailHeaderProps) {
  return (
    <>
      {backLabel && onBack && (
        <button className={cn(ghostButton, '-ml-3 mb-4')} onClick={onBack}>
          <ChevronLeft aria-hidden className="w-4 h-4" /> {backLabel}
        </button>
      )}
      <div className="flex flex-wrap items-start justify-between gap-4 pb-6 border-b border-border">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-x-5 gap-y-2">
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight break-words">{title}</h1>
            {status}
          </div>
          {meta && <p className="mt-2 text-muted-foreground tabular-nums">{meta}</p>}
        </div>
        {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
      </div>
    </>
  );
}

interface SegmentedProps<T extends string> {
  label: string;
  value: T;
  options: ReadonlyArray<{ value: T; label: ReactNode; count?: number | null }>;
  onChange: (value: T) => void;
  className?: string;
}

/** Grupo segmentado de filtros o vistas, igual al de Casos. */
export function Segmented<T extends string>({ label, value, options, onChange, className }: SegmentedProps<T>) {
  return (
    <div role="group" aria-label={label} className={cn('inline-flex max-w-full overflow-x-auto p-1 rounded-lg bg-muted', className)}>
      {options.map((o) => {
        const on = o.value === value;
        return (
          <button
            key={o.value}
            type="button"
            aria-pressed={on}
            onClick={() => onChange(o.value)}
            className={cn(
              'inline-flex shrink-0 items-center gap-2 h-8 px-3 rounded-md text-sm transition-colors whitespace-nowrap',
              on ? 'bg-card text-foreground font-bold ring-1 ring-border' : 'text-muted-foreground hover:text-foreground',
            )}
          >
            {o.label}
            {o.count !== undefined && <span className="tabular-nums text-muted-foreground font-normal">{o.count ?? '—'}</span>}
          </button>
        );
      })}
    </div>
  );
}
