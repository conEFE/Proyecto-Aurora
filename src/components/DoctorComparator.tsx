import { useCallback, useEffect, useMemo, useState } from 'react';
import { ArrowDown, ArrowUp, FileSpreadsheet, Users } from 'lucide-react';
import { apiClient } from '../services/api';
import type { DoctorComparison, DoctorStats, Specialty } from '../types';
import { SPECIALTY_LABELS } from '../types';
import { cn } from '../lib/cn';
import { ListHeader, Segmented } from './PageHeader';
import { EmptyState, ErrorMessage, Loading } from './Feedback';
import { cardClass, inputClass, labelClass, pageClass, pageSubtitle, secondaryButton, sectionTitle, tdClass, thClass } from './ui';

type PeriodKey = '30' | '90' | '365' | 'todo';
const PERIODS: Array<{ value: PeriodKey; label: string }> = [
  { value: '30', label: '30 días' },
  { value: '90', label: '90 días' },
  { value: '365', label: '12 meses' },
  { value: 'todo', label: 'Todo' },
];

const MAX_SELECTED = 4;

type MetricKey = Exclude<keyof DoctorStats, 'id' | 'full_name' | 'specialty' | 'is_active'>;

interface Metric {
  key: MetricKey;
  label: string;
  /** Texto corto para la cabecera de la tabla. */
  short: string;
  kind: 'count' | 'rate' | 'hours' | 'decimal';
  /** true: un valor más bajo es mejor (tiempos, atrasos). */
  lowerIsBetter?: boolean;
  help: string;
}

const METRICS: Metric[] = [
  { key: 'reviews', label: 'Revisiones', short: 'Revisiones', kind: 'count', help: 'Casos revisados en el período' },
  { key: 'reviews_per_week', label: 'Revisiones por semana', short: 'Rev./sem.', kind: 'decimal', help: 'Promedio semanal del período' },
  { key: 'reports_signed', label: 'Reportes firmados', short: 'Firmados', kind: 'count', help: 'Reportes con firma del médico' },
  { key: 'cases_closed', label: 'Casos cerrados', short: 'Cerrados', kind: 'count', help: 'Casos asignados o revisados que se cerraron' },
  { key: 'avg_review_hours', label: 'Tiempo medio hasta revisar', short: 'T. medio', kind: 'hours', lowerIsBetter: true, help: 'Desde el primer triage hasta la revisión' },
  { key: 'p95_review_hours', label: 'Tiempo p95 hasta revisar', short: 'T. p95', kind: 'hours', lowerIsBetter: true, help: 'El 95 % de las revisiones tardó menos que esto' },
  { key: 'open_assigned', label: 'Casos abiertos asignados', short: 'Abiertos', kind: 'count', help: 'Carga actual, sin importar el período' },
  { key: 'alta_late', label: 'ALTA atrasados', short: 'ALTA atras.', kind: 'count', lowerIsBetter: true, help: 'Casos ALTA abiertos sobre el umbral de horas' },
  { key: 'overrides', label: 'Ajustes de triage', short: 'Ajustes', kind: 'count', help: 'Veces que cambió el nivel calculado' },
  { key: 'ai_agreement_rate', label: 'Concordancia con la IA', short: 'Conc. IA', kind: 'rate', help: 'Imágenes en que coincidió con la IA (sin las no evaluables)' },
  { key: 'triage_agreement_rate', label: 'Triage apropiado', short: 'Triage OK', kind: 'rate', help: 'Revisiones que evaluaron el triage como apropiado' },
];

const CHART_METRICS: MetricKey[] = ['reviews', 'reviews_per_week', 'cases_closed', 'avg_review_hours', 'open_assigned', 'alta_late'];

function format(value: number | null, kind: Metric['kind']): string {
  if (value === null || value === undefined) return '—';
  if (kind === 'rate') return `${Math.round(value * 100)} %`;
  if (kind === 'hours') return value < 1 ? `${Math.round(value * 60)} min` : `${value.toFixed(1).replace('.', ',')} h`;
  if (kind === 'decimal') return value.toFixed(1).replace('.', ',');
  return value.toLocaleString('es-CL');
}

const isoDay = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;

function rangeOf(period: PeriodKey): { from?: string; to?: string } {
  if (period === 'todo') return {};
  const start = new Date();
  start.setDate(start.getDate() - (Number(period) - 1));
  return { from: `${isoDay(start)}T00:00:00`, to: `${isoDay(new Date())}T23:59:59` };
}

const specialtyLabel = (s: Specialty | null) => (s ? SPECIALTY_LABELS[s] : 'Sin especialidad');

/** Exporta la tabla a CSV (separador «;» para que Excel en español la abra en columnas). */
function exportCsv(rows: DoctorStats[], team: DoctorStats | null, period: string) {
  const header = ['Médico', 'Especialidad', ...METRICS.map((m) => m.label)];
  const line = (d: DoctorStats) => [
    d.full_name,
    d.id === 0 ? '' : specialtyLabel(d.specialty),
    ...METRICS.map((m) => {
      const v = d[m.key] as number | null;
      if (v === null) return '';
      return m.kind === 'rate' ? String(Math.round(v * 100)) : String(v).replace('.', ',');
    }),
  ];
  const all = [header, ...rows.map(line), ...(team ? [line(team)] : [])];
  const csv = all.map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(';')).join('\r\n');
  const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `comparador-medicos-${period}-${isoDay(new Date())}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

/** Barras horizontales de una métrica para los médicos seleccionados, con la marca del promedio del equipo. */
function MetricBars({ metric, doctors, team }: { metric: Metric; doctors: DoctorStats[]; team: DoctorStats | null }) {
  const values = doctors.map((d) => (d[metric.key] as number | null) ?? null);
  const teamValue = team ? ((team[metric.key] as number | null) ?? null) : null;
  const max = Math.max(...values.map((v) => v ?? 0), teamValue ?? 0, metric.kind === 'rate' ? 1 : 0) || 1;
  const present = values.filter((v): v is number => v !== null);
  const best = present.length > 1 ? (metric.lowerIsBetter ? Math.min(...present) : Math.max(...present)) : null;
  return (
    <div className={cn(cardClass, 'p-4')}>
      <div className="flex items-baseline justify-between gap-2">
        <h3 className="text-sm font-bold">{metric.label}</h3>
        {teamValue !== null && <span className="text-xs text-muted-foreground">Equipo: {format(teamValue, metric.kind)}</span>}
      </div>
      <p className="text-xs text-muted-foreground">{metric.help}</p>
      <ul className="mt-3 space-y-2">
        {doctors.map((d, i) => {
          const v = values[i];
          const isBest = v !== null && best !== null && v === best;
          return (
            <li key={d.id}>
              <div className="flex justify-between gap-2 text-xs">
                <span className="truncate">{d.full_name}</span>
                <span className={cn('tabular-nums', isBest && 'font-bold')}>
                  {format(v, metric.kind)}
                  {isBest && <span className="sr-only"> (mejor del grupo)</span>}
                </span>
              </div>
              <div className="relative mt-1 h-2.5 rounded-full bg-muted">
                <div
                  className={cn('h-full rounded-full', isBest ? 'bg-brand' : 'bg-brand/45')}
                  style={{ width: `${!v ? 0 : Math.max(2, (v / max) * 100)}%` }}
                />
                {teamValue !== null && (
                  <span
                    aria-hidden
                    className="absolute -top-1 h-[18px] w-0.5 bg-foreground/70"
                    style={{ left: `${(teamValue / max) * 100}%` }}
                  />
                )}
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export default function DoctorComparator() {
  const [period, setPeriod] = useState<PeriodKey>('90');
  const [specialty, setSpecialty] = useState<Specialty | ''>('');
  const [data, setData] = useState<DoctorComparison | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<number[]>([]);
  const [sort, setSort] = useState<{ key: MetricKey | 'full_name'; desc: boolean }>({ key: 'reviews', desc: true });

  const load = useCallback(async () => {
    setLoading(true);
    const r = await apiClient.compareDoctors({ ...rangeOf(period), specialty: specialty || undefined });
    setLoading(false);
    if (r.data) {
      setData(r.data);
      setError(null);
      setSelected((prev) => {
        const ids = new Set(r.data!.doctors.map((d) => d.id));
        const kept = prev.filter((id) => ids.has(id));
        // Primera carga: los dos con más revisiones, para que la comparación no parta vacía
        if (kept.length || prev.length) return kept;
        return [...r.data!.doctors].sort((a, b) => b.reviews - a.reviews).slice(0, 2).map((d) => d.id);
      });
    } else setError(r.error || 'No se pudo cargar el comparador.');
  }, [period, specialty]);

  useEffect(() => {
    load();
  }, [load]);

  const rows = useMemo(() => {
    const list = [...(data?.doctors ?? [])];
    list.sort((a, b) => {
      if (sort.key === 'full_name') return a.full_name.localeCompare(b.full_name, 'es') * (sort.desc ? -1 : 1);
      const av = (a[sort.key] as number | null) ?? -Infinity;
      const bv = (b[sort.key] as number | null) ?? -Infinity;
      return (av - bv) * (sort.desc ? -1 : 1);
    });
    return list;
  }, [data, sort]);

  const chosen = rows.filter((d) => selected.includes(d.id));

  const toggle = (id: number) =>
    setSelected((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : prev.length >= MAX_SELECTED ? prev : [...prev, id]));

  const sortBy = (key: MetricKey | 'full_name') =>
    setSort((s) => (s.key === key ? { key, desc: !s.desc } : { key, desc: key !== 'full_name' }));

  const SortIcon = sort.desc ? ArrowDown : ArrowUp;

  return (
    <div className={pageClass}>
      <ListHeader
        title="Comparador de médicos"
        actions={
          <button type="button" className={secondaryButton} disabled={!data?.doctors.length}
            onClick={() => data && exportCsv(rows, data.team, period)}>
            <FileSpreadsheet aria-hidden className="w-4 h-4" /> Exportar CSV
          </button>
        }
      />
      <p className={pageSubtitle}>
        Productividad, tiempos de respuesta, carga actual y concordancia de cada médico. Sirve para la gestión y
        planificación del equipo; no evalúa la calidad clínica de un diagnóstico.
      </p>

      <div className="mt-6 flex flex-wrap items-end gap-4">
        <Segmented label="Período" value={period} onChange={setPeriod} options={PERIODS} />
        <div>
          <label htmlFor="cmp-specialty" className={labelClass}>Especialidad</label>
          <select id="cmp-specialty" className={cn(inputClass, 'h-9 w-56')} value={specialty}
            onChange={(e) => setSpecialty(e.target.value as Specialty | '')}>
            <option value="">Todas</option>
            {(Object.keys(SPECIALTY_LABELS) as Specialty[]).map((s) => (
              <option key={s} value={s}>{SPECIALTY_LABELS[s]}</option>
            ))}
          </select>
        </div>
      </div>

      <ErrorMessage className="mt-4">{error}</ErrorMessage>

      {loading && !data ? (
        <Loading className="mt-10" label="Cargando médicos…" />
      ) : data && data.doctors.length === 0 ? (
        <div className="mt-8">
          <EmptyState title="No hay médicos activos con ese filtro" icon={<Users aria-hidden className="w-6 h-6" />}>
            Cambie la especialidad o registre médicos desde Administración.
          </EmptyState>
        </div>
      ) : data ? (
        <>
          <section aria-labelledby="cmp-chart" className="mt-8">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <h2 id="cmp-chart" className={sectionTitle}>Comparación lado a lado</h2>
              <p className="text-xs text-muted-foreground">
                Elija hasta {MAX_SELECTED} médicos en la tabla. La línea vertical marca el promedio del equipo.
              </p>
            </div>
            {chosen.length < 2 ? (
              <p className="mt-3 text-sm text-muted-foreground">Seleccione al menos dos médicos en la tabla para compararlos.</p>
            ) : (
              <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                {CHART_METRICS.map((k) => (
                  <MetricBars key={k} metric={METRICS.find((m) => m.key === k)!} doctors={chosen} team={data.team} />
                ))}
              </div>
            )}
          </section>

          <section aria-labelledby="cmp-table" className="mt-8">
            <h2 id="cmp-table" className={sectionTitle}>Todos los médicos</h2>
            <p className="text-xs text-muted-foreground">
              {data.weeks.toLocaleString('es-CL', { maximumFractionDigits: 1 })} semanas en el período · ALTA atrasado = más
              de {data.alta_pending_threshold_hours} h sin cerrar
            </p>
            <div className={cn(cardClass, 'mt-3 overflow-x-auto')}>
              <table className="w-full">
                <caption className="sr-only">Indicadores por médico; seleccione filas para compararlas arriba</caption>
                <thead>
                  <tr>
                    <th className={cn(thClass, 'w-10')}><span className="sr-only">Comparar</span></th>
                    <th className={thClass} aria-sort={sort.key === 'full_name' ? (sort.desc ? 'descending' : 'ascending') : undefined}>
                      <button type="button" className="inline-flex items-center gap-1" onClick={() => sortBy('full_name')}>
                        Médico {sort.key === 'full_name' && <SortIcon aria-hidden className="w-3 h-3" />}
                      </button>
                    </th>
                    {METRICS.map((m) => (
                      <th key={m.key} className={cn(thClass, 'text-right')} title={m.help}
                        aria-sort={sort.key === m.key ? (sort.desc ? 'descending' : 'ascending') : undefined}>
                        <button type="button" className="inline-flex items-center gap-1" onClick={() => sortBy(m.key)}>
                          {m.short} {sort.key === m.key && <SortIcon aria-hidden className="w-3 h-3" />}
                        </button>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((d) => {
                    const on = selected.includes(d.id);
                    const disabled = !on && selected.length >= MAX_SELECTED;
                    return (
                      <tr key={d.id} className={cn(on && 'bg-brand/5')}>
                        <td className={tdClass}>
                          <input type="checkbox" className="w-4 h-4 accent-[hsl(var(--brand))]" checked={on} disabled={disabled}
                            aria-label={`Comparar a ${d.full_name}`} onChange={() => toggle(d.id)} />
                        </td>
                        <td className={tdClass}>
                          <span className="font-semibold">{d.full_name}</span>
                          {!d.is_active && <span className="ml-2 text-xs text-muted-foreground">(inactivo)</span>}
                          <span className="block text-xs text-muted-foreground">{specialtyLabel(d.specialty)}</span>
                        </td>
                        {METRICS.map((m) => (
                          <td key={m.key} className={cn(tdClass, 'text-right tabular-nums',
                            m.key === 'alta_late' && d.alta_late > 0 && 'text-alta font-bold')}>
                            {format(d[m.key] as number | null, m.kind)}
                          </td>
                        ))}
                      </tr>
                    );
                  })}
                  {data.team && (
                    <tr className="bg-muted/50">
                      <td className={tdClass} />
                      <td className={cn(tdClass, 'font-bold')}>Promedio del equipo</td>
                      {METRICS.map((m) => (
                        <td key={m.key} className={cn(tdClass, 'text-right tabular-nums font-semibold')}>
                          {format(data.team![m.key] as number | null, m.kind)}
                        </td>
                      ))}
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>
        </>
      ) : null}
    </div>
  );
}
