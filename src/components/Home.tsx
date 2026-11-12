import { useCallback, useState } from 'react';
import { ArrowRight } from 'lucide-react';
import { apiClient } from '../services/api';
import type { Me, QueueItem, TriageLevel } from '../types';
import { usePolling } from '../lib/usePolling';
import { cn } from '../lib/cn';
import { LevelBadge } from './Badges';
import { cardClass, pageClass, pageSubtitle, pageTitle, primaryButton } from './ui';

interface HomeProps {
  me: Me;
  onGetStarted: () => void;
}

const LEVELS: TriageLevel[] = ['ALTA', 'MEDIA', 'BAJA'];

function greeting(): string {
  const h = new Date().getHours();
  if (h < 12) return 'Buenos días';
  if (h < 20) return 'Buenas tardes';
  return 'Buenas noches';
}

function formatWaiting(hours: number): string {
  if (hours < 1) return `${Math.round(hours * 60)} min`;
  if (hours < 48) return `${hours.toFixed(1).replace('.', ',')} h`;
  return `${(hours / 24).toFixed(1).replace('.', ',')} días`;
}

export default function Home({ me, onGetStarted }: HomeProps) {
  const [queue, setQueue] = useState<QueueItem[] | null>(null);

  const load = useCallback(async () => {
    const r = await apiClient.getQueue(true);
    if (r.data) setQueue(r.data);
  }, []);
  usePolling(load, 60000);

  const counts = LEVELS.map((level) => {
    const items = queue?.filter((q) => q.level === level) ?? [];
    return { level, n: items.length, oldest: items.length ? Math.max(...items.map((q) => q.waiting_hours)) : null };
  });
  const urgent = (queue ?? []).filter((q) => q.level === 'ALTA').slice(0, 4);

  return (
    <div className={pageClass}>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className={pageTitle}>
            {greeting()}, {me.full_name.split(' ')[0]}
          </h1>
          <p className={pageSubtitle}>
            {queue === null
              ? 'Cargando…'
              : queue.length === 0
                ? 'No hay casos pendientes.'
                : `${queue.length} ${queue.length === 1 ? 'caso pendiente' : 'casos pendientes'}`}
          </p>
        </div>
        <button onClick={onGetStarted} className={primaryButton}>
          Abrir la cola de triage
          <ArrowRight aria-hidden className="w-4 h-4" />
        </button>
      </div>

      <div className="mt-8 grid xl:grid-cols-2 gap-6 items-start">
        <section aria-labelledby="pending-title" className={cn(cardClass, 'p-6')}>
          <h2 id="pending-title" className="text-base font-bold">Pendientes por prioridad</h2>
          <table className="mt-4 w-full">
            <caption className="sr-only">Casos pendientes por nivel</caption>
            <thead>
              <tr className="text-xs text-muted-foreground">
                <th scope="col" className="text-left font-semibold pb-2">Nivel</th>
                <th scope="col" className="text-right font-semibold pb-2">Casos</th>
                <th scope="col" className="text-right font-semibold pb-2">Espera más antigua</th>
              </tr>
            </thead>
            <tbody>
              {counts.map(({ level, n, oldest }) => (
                <tr key={level} className="border-t border-border">
                  <th scope="row" className="py-3 text-left"><LevelBadge level={level} /></th>
                  <td className="py-3 text-right text-lg font-extrabold tabular-nums">{queue === null ? '—' : n}</td>
                  <td className="py-3 text-right text-muted-foreground tabular-nums">{oldest === null ? '—' : formatWaiting(oldest)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <section aria-labelledby="urgent-title" className={cn(cardClass, 'p-6')}>
          <h2 id="urgent-title" className="text-base font-bold">Prioridad alta en espera</h2>
          {urgent.length === 0 ? (
            <p className="mt-4 text-sm text-muted-foreground">Ninguno por ahora.</p>
          ) : (
            <ul className="mt-3">
              {urgent.map((q) => (
                <li key={q.code} className="flex items-center justify-between gap-4 py-3 border-t border-border">
                  <span className="font-bold tabular-nums">{q.code}</span>
                  <span className="flex items-center gap-6">
                    <LevelBadge level={q.level} />
                    <span className="w-20 text-right text-sm text-muted-foreground tabular-nums">
                      {formatWaiting(q.waiting_hours)}
                    </span>
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}
