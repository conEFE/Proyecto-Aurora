import { useCallback, useState } from 'react';
import { PenLine, RefreshCw } from 'lucide-react';
import { apiClient } from '../services/api';
import type { Me, QueueItem, TriageLevel } from '../types';
import { usePolling } from '../lib/usePolling';
import { cn } from '../lib/cn';
import { RULE_LABELS } from '../constants';
import { LevelBadge, ScoreBar, StatusBadge } from './Badges';
import { EmptyState, ErrorMessage, Loading } from './Feedback';
import { cardClass, pageClass, pageSubtitle, pageTitle, secondaryButton, tdClass, thClass } from './ui';

function formatWaiting(hours: number): string {
  if (hours < 1) return `${Math.round(hours * 60)} min`;
  if (hours < 48) return `${hours.toFixed(1).replace('.', ',')} h`;
  return `${(hours / 24).toFixed(1).replace('.', ',')} días`;
}

interface TriageQueueProps {
  me: Me;
  onOpenCase: (caseId: number) => void;
}

type Filter = 'TODOS' | TriageLevel;

export default function TriageQueue({ me, onOpenCase }: TriageQueueProps) {
  const [items, setItems] = useState<QueueItem[] | null>(null);
  const [includeInReview, setIncludeInReview] = useState(true);
  const [filter, setFilter] = useState<Filter>('TODOS');
  const [error, setError] = useState<string | null>(null);
  const [updatedAt, setUpdatedAt] = useState<Date | null>(null);
  const isMedico = me.role === 'MEDICO';

  const load = useCallback(async () => {
    const r = await apiClient.getQueue(includeInReview);
    if (r.data) {
      setItems(r.data);
      setError(null);
      setUpdatedAt(new Date());
    } else setError(r.error || 'No se pudo cargar la cola. Revise la conexión e intente de nuevo.');
  }, [includeInReview]);

  usePolling(load, 30000);

  const counts = (items ?? []).reduce(
    (acc, i) => ({ ...acc, [i.level]: acc[i.level] + 1 }),
    { ALTA: 0, MEDIA: 0, BAJA: 0 } as Record<TriageLevel, number>,
  );
  const visible = (items ?? []).filter((i) => filter === 'TODOS' || i.level === filter);

  const filters: Array<{ id: Filter; label: string; n: number }> = [
    { id: 'TODOS', label: 'Todos', n: items?.length ?? 0 },
    { id: 'ALTA', label: 'Alta', n: counts.ALTA },
    { id: 'MEDIA', label: 'Media', n: counts.MEDIA },
    { id: 'BAJA', label: 'Baja', n: counts.BAJA },
  ];

  return (
    <div className={pageClass}>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className={pageTitle}>Cola de triage</h1>
          <p className={pageSubtitle}>
            {updatedAt
              ? `Actualizada a las ${updatedAt.toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' })}`
              : 'Cargando…'}
          </p>
        </div>
        <button className={secondaryButton} onClick={load}>
          <RefreshCw aria-hidden className="w-4 h-4" /> Actualizar
        </button>
      </div>

      <div className="mt-6 flex flex-wrap items-center gap-x-6 gap-y-3">
        <div role="group" aria-label="Filtrar por nivel" className="inline-flex max-w-full overflow-x-auto p-1 rounded-lg bg-muted">
          {filters.map((f) => (
            <button
              key={f.id}
              onClick={() => setFilter(f.id)}
              aria-pressed={filter === f.id}
              className={cn(
                'inline-flex shrink-0 items-center gap-2 h-8 px-3 rounded-md text-sm transition-colors whitespace-nowrap',
                filter === f.id ? 'bg-card text-foreground font-bold ring-1 ring-border' : 'text-muted-foreground hover:text-foreground',
              )}
            >
              {f.id === 'TODOS' ? f.label : <LevelBadge level={f.id} />}
              <span className="tabular-nums text-muted-foreground">{items ? f.n : ''}</span>
            </button>
          ))}
        </div>
        <label className="inline-flex items-center gap-2 text-sm text-foreground">
          <input type="checkbox" checked={includeInReview} onChange={(e) => setIncludeInReview(e.target.checked)} />
          Incluir casos en revisión
        </label>
      </div>

      <ErrorMessage className="mt-4">{error}</ErrorMessage>

      <div className={cn(cardClass, 'mt-4 overflow-hidden')}>
        {items === null ? (
          <Loading label="Cargando la cola…" />
        ) : visible.length === 0 ? (
          <EmptyState title={items.length === 0 ? 'La cola está vacía' : 'No hay casos con este nivel'}>
            {items.length === 0 ? 'Los casos nuevos aparecen aquí apenas se calcula su triage.' : 'Pruebe con otro filtro.'}
          </EmptyState>
        ) : (
          <div className="relative overflow-x-auto">
            <table className="w-full">
              <caption className="sr-only">Casos pendientes ordenados por prioridad</caption>
              <thead className="bg-muted/60">
                <tr>
                  <th scope="col" className={cn(thClass, 'w-12 text-right')}>N.º</th>
                  <th scope="col" className={thClass}>Código</th>
                  <th scope="col" className={thClass}>Nivel</th>
                  {isMedico && <th scope="col" className={thClass}>Puntaje</th>}
                  <th scope="col" className={thClass}>Estado</th>
                  <th scope="col" className={cn(thClass, 'text-right')}>Espera</th>
                  {isMedico && (
                    <>
                      <th scope="col" className={thClass}>Escalamiento</th>
                      <th scope="col" className={thClass}>Paciente</th>
                    </>
                  )}
                </tr>
              </thead>
              <tbody>
                {visible.map((item, idx) => (
                  <tr key={item.code} className="hover:bg-accent/60 transition-colors">
                    <td className={cn(tdClass, 'text-right text-muted-foreground tabular-nums')}>{idx + 1}</td>
                    <td className={tdClass}>
                      {isMedico && item.case_id ? (
                        <button
                          className="font-bold tabular-nums text-foreground hover:text-brand hover:underline"
                          onClick={() => onOpenCase(item.case_id!)}
                          aria-label={`Abrir caso ${item.code}`}
                        >
                          {item.code}
                        </button>
                      ) : (
                        <span className="font-bold tabular-nums">{item.code}</span>
                      )}
                    </td>
                    <td className={tdClass}>
                      <span className="inline-flex items-center gap-2">
                        <LevelBadge level={item.level} />
                        {item.overridden && (
                          <span title="Nivel ajustado por un médico" className="inline-flex items-center gap-1 text-xs text-info">
                            <PenLine aria-hidden className="w-3.5 h-3.5" />
                            <span>ajustado</span>
                          </span>
                        )}
                      </span>
                    </td>
                    {isMedico && (
                      <td className={tdClass}>
                        <ScoreBar score={item.score} level={item.level} />
                      </td>
                    )}
                    <td className={tdClass}><StatusBadge status={item.status} /></td>
                    <td className={cn(tdClass, 'text-right tabular-nums text-muted-foreground')}>{formatWaiting(item.waiting_hours)}</td>
                    {isMedico && (
                      <>
                        <td className={cn(tdClass, 'text-muted-foreground')}>{item.escalation_rule ? (RULE_LABELS[item.escalation_rule] ?? item.escalation_rule) : '—'}</td>
                        <td className={cn(tdClass, 'text-muted-foreground')}>{item.patient_name ?? '—'}</td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
