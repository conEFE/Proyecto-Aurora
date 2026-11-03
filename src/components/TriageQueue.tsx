import { useCallback, useEffect, useState } from 'react';
import { ListOrdered, Loader2, RefreshCw } from 'lucide-react';
import { apiClient } from '../services/api';
import type { Me, QueueItem, TriageLevel } from '../types';
import { LevelBadge, StatusBadge } from './Badges';
import { cardClass, errorBox, secondaryButton, tdClass, thClass } from './ui';

const ROW_ACCENT: Record<TriageLevel, string> = {
  ALTA: 'border-l-4 border-l-red-500',
  MEDIA: 'border-l-4 border-l-orange-500',
  BAJA: 'border-l-4 border-l-green-500',
};

function formatWaiting(hours: number): string {
  if (hours < 1) return `${Math.round(hours * 60)} min`;
  if (hours < 48) return `${hours.toFixed(1)} h`;
  return `${(hours / 24).toFixed(1)} días`;
}

interface TriageQueueProps {
  me: Me;
  onOpenCase: (caseId: number) => void;
}

export default function TriageQueue({ me, onOpenCase }: TriageQueueProps) {
  const [items, setItems] = useState<QueueItem[] | null>(null);
  const [includeInReview, setIncludeInReview] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const isMedico = me.role === 'MEDICO';

  const load = useCallback(async () => {
    const r = await apiClient.getQueue(includeInReview);
    if (r.data) {
      setItems(r.data);
      setError(null);
    } else setError(r.error || 'Error al cargar la cola');
  }, [includeInReview]);

  useEffect(() => {
    load();
    const timer = window.setInterval(load, 30000);
    return () => window.clearInterval(timer);
  }, [load]);

  const counts = (items ?? []).reduce(
    (acc, i) => ({ ...acc, [i.level]: acc[i.level] + 1 }),
    { ALTA: 0, MEDIA: 0, BAJA: 0 } as Record<TriageLevel, number>
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-foreground flex items-center gap-2">
            <ListOrdered className="w-5 h-5 text-primary" /> Cola de triage
          </h2>
          <p className="mt-0.5 text-xs text-muted-foreground">
            Orden: nivel (ALTA → BAJA), puntaje y antigüedad. Se actualiza cada 30 segundos.
          </p>
        </div>
        <button className={secondaryButton} onClick={load}>
          <RefreshCw className="w-3.5 h-3.5" /> Actualizar
        </button>
      </div>

      <div className="grid grid-cols-3 gap-3">
        {(['ALTA', 'MEDIA', 'BAJA'] as TriageLevel[]).map((lvl) => (
          <div key={lvl} className={`${cardClass} p-3 ${ROW_ACCENT[lvl]}`}>
            <p className="text-xl font-bold text-foreground">{counts[lvl]}</p>
            <p className="text-[10px] text-muted-foreground">Prioridad {lvl}</p>
          </div>
        ))}
      </div>

      <label className="flex items-center gap-2 text-xs text-muted-foreground">
        <input type="checkbox" checked={includeInReview} onChange={(e) => setIncludeInReview(e.target.checked)} />
        Incluir casos en revisión
      </label>

      {error && <div className={errorBox}>{error}</div>}

      <div className={`${cardClass} overflow-hidden`}>
        {items === null ? (
          <div className="py-8 text-center"><Loader2 className="w-6 h-6 mx-auto animate-spin text-primary" /></div>
        ) : items.length === 0 ? (
          <p className="py-8 text-center text-xs text-muted-foreground">No hay casos en la cola.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-secondary/50 border-b border-border">
                <tr>
                  <th className={thClass}>#</th>
                  <th className={thClass}>Código</th>
                  <th className={thClass}>Nivel</th>
                  <th className={thClass}>Estado</th>
                  <th className={thClass}>Espera</th>
                  {isMedico && (
                    <>
                      <th className={thClass}>Puntaje</th>
                      <th className={thClass}>Regla</th>
                      <th className={thClass}>Paciente</th>
                      <th className={thClass}></th>
                    </>
                  )}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {items.map((item, idx) => (
                  <tr key={item.code} className={`${ROW_ACCENT[item.level]} hover:bg-secondary/30`}>
                    <td className={`${tdClass} text-muted-foreground`}>{idx + 1}</td>
                    <td className={`${tdClass} font-mono text-foreground`}>{item.code}</td>
                    <td className={tdClass}><LevelBadge level={item.level} /></td>
                    <td className={tdClass}><StatusBadge status={item.status} /></td>
                    <td className={`${tdClass} text-muted-foreground`}>{formatWaiting(item.waiting_hours)}</td>
                    {isMedico && (
                      <>
                        <td className={`${tdClass} text-foreground`}>
                          {item.score?.toFixed(2)}
                          {item.overridden && <span className="ml-1 text-[10px] text-blue-300" title="Nivel ajustado por médico">✎</span>}
                        </td>
                        <td className={`${tdClass} text-muted-foreground`}>{item.escalation_rule ?? '—'}</td>
                        <td className={`${tdClass} text-muted-foreground`}>{item.patient_name}</td>
                        <td className={tdClass}>
                          {item.case_id && (
                            <button className="text-primary text-xs font-medium" onClick={() => onOpenCase(item.case_id!)}>
                              Abrir
                            </button>
                          )}
                        </td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      {!isMedico && (
        <p className="text-[10px] text-muted-foreground">
          Vista administrativa: solo código, nivel, estado y antigüedad. El detalle clínico lo ve el personal médico.
        </p>
      )}
    </div>
  );
}
