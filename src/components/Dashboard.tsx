import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { AlertTriangle, CheckCircle2, FileDown, Minus } from 'lucide-react';
import { apiClient } from '../services/api';
import type {
  AIVerdict,
  CaseStatus,
  DashboardMetrics,
  InferenceStatus,
  Me,
  ModelPerformanceReport,
  QueueItem,
  TriageAssessment,
  TriageLevel,
} from '../types';
import { AI_VERDICT_LABELS, CASE_STATUS_LABELS, TRIAGE_ASSESSMENT_LABELS } from '../types';
import { LEVEL_FILL, RULE_LABELS } from '../constants';
import { cn } from '../lib/cn';
import { LevelBadge, SimulatedBadge } from './Badges';
import { ErrorMessage, Loading } from './Feedback';
import { ListHeader, Segmented } from './PageHeader';
import { cardClass, ghostButton, secondaryButton, inputClass, pageClass, sectionTitle, tdClass, thClass } from './ui';

const LEVELS: TriageLevel[] = ['ALTA', 'MEDIA', 'BAJA'];

const dec = (n: number, d = 1) => n.toFixed(d).replace('.', ',');

function formatSeconds(s: number | null): string {
  if (s === null) return '—';
  if (s < 60) return `${s.toFixed(0)} s`;
  if (s < 3600) return `${dec(s / 60)} min`;
  return `${dec(s / 3600)} h`;
}

function pct(v: number | null): string {
  return v === null ? '—' : `${dec(v * 100)} %`;
}

function pctCi(v: number | null, ci: [number, number] | null): string {
  if (v === null) return '—';
  return ci ? `${pct(v)} (${(ci[0] * 100).toFixed(0)}–${(ci[1] * 100).toFixed(0)})` : pct(v);
}

function Status({ ok }: { ok: boolean | null }) {
  if (ok === null)
    return (
      <span className="inline-flex items-center gap-1.5 text-sm text-muted-foreground">
        <Minus aria-hidden className="w-4 h-4" /> Sin datos
      </span>
    );
  return ok ? (
    <span className="inline-flex items-center gap-1.5 text-sm font-semibold text-baja">
      <CheckCircle2 aria-hidden className="w-4 h-4" /> Cumple
    </span>
  ) : (
    <span className="inline-flex items-center gap-1.5 text-sm font-semibold text-media">
      <AlertTriangle aria-hidden className="w-4 h-4" /> Fuera de meta
    </span>
  );
}

function hoursText(h: number | null): string {
  if (h === null) return '—';
  return h < 48 ? `${dec(h)} h` : `${dec(h / 24)} días`;
}

// --- Período: rápido (7, 30 o 90 días), todo o un rango; queda en la dirección ---------------------

type PeriodKey = '7' | '30' | '90' | 'todo' | 'rango';
const PERIODS: Array<{ value: PeriodKey; label: string }> = [
  { value: '7', label: '7 días' },
  { value: '30', label: '30 días' },
  { value: '90', label: '90 días' },
  { value: 'todo', label: 'Todo' },
  { value: 'rango', label: 'Rango' },
];

interface Range {
  from?: string;
  to?: string;
}

const isoDay = (d: Date) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;

function addDays(day: string, n: number): string {
  const d = new Date(`${day}T12:00:00`);
  d.setDate(d.getDate() + n);
  return isoDay(d);
}

/** Rango del período y el período anterior de igual largo (para comparar). */
function periodRanges(period: PeriodKey, from: string, to: string): { current: Range; previous: Range | null; days: number | null } {
  const today = isoDay(new Date());
  if (period === 'todo') return { current: {}, previous: null, days: null };
  if (period === 'rango') {
    if (!from || !to || from > to) return { current: { from: from || undefined, to: to || undefined }, previous: null, days: null };
    const days = Math.round((new Date(`${to}T12:00:00`).getTime() - new Date(`${from}T12:00:00`).getTime()) / 86400000) + 1;
    return { current: { from, to }, previous: { from: addDays(from, -days), to: addDays(from, -1) }, days };
  }
  const days = Number(period);
  const start = addDays(today, -(days - 1));
  return { current: { from: start, to: today }, previous: { from: addDays(start, -days), to: addDays(start, -1) }, days };
}

const apiRange = (r: Range) => ({ from: r.from ? `${r.from}T00:00:00` : undefined, to: r.to ? `${r.to}T23:59:59` : undefined });

/** Variación frente al período anterior, en texto (el color no lleva el significado). */
function Delta({ now, before, kind = 'count' }: { now: number | null; before: number | null | undefined; kind?: 'count' | 'rate' | 'hours' }) {
  if (now === null || before === null || before === undefined) return null;
  let label: string;
  if (kind === 'rate') {
    const diff = (now - before) * 100;
    if (Math.abs(diff) < 0.5) label = 'igual que el período anterior';
    else label = `${diff > 0 ? '+' : '−'}${dec(Math.abs(diff), 0)} pts vs. período anterior`;
  } else {
    if (before === 0) return <span className="block text-xs text-muted-foreground">sin datos del período anterior</span>;
    const change = (now - before) / before;
    if (Math.abs(change) < 0.005) label = 'igual que el período anterior';
    else label = `${change > 0 ? '+' : '−'}${dec(Math.abs(change) * 100, 0)} % vs. período anterior`;
  }
  return <span className="block text-xs text-muted-foreground tabular-nums">{label}</span>;
}

function Panel({ title, children, className, aside }: { title: string; children: ReactNode; className?: string; aside?: ReactNode }) {
  return (
    <section className={cn(cardClass, 'p-6', className)}>
      <div className="mb-4 flex flex-wrap items-baseline justify-between gap-2">
        <h2 className={sectionTitle}>{title}</h2>
        {aside}
      </div>
      {children}
    </section>
  );
}

/** Barras por nivel; cada fila abre la lista de Casos filtrada por ese nivel. */
function LevelBars({ data }: { data: Record<TriageLevel, number> }) {
  const max = Math.max(1, ...LEVELS.map((l) => data[l]));
  return (
    <ul className="space-y-1">
      {LEVELS.map((l) => (
        <li key={l}>
          <Link
            to={`/casos?nivel=${l}`}
            className="grid grid-cols-[5.5rem_1fr_3rem] items-center gap-3 rounded-lg px-2 py-2 -mx-2 hover:bg-accent/60 transition-colors"
            aria-label={`${data[l]} casos ${l}: ver la lista`}
          >
            <LevelBadge level={l} />
            <span aria-hidden className="h-3 rounded-full bg-muted overflow-hidden">
              <span
                className={cn('block h-full rounded-full', LEVEL_FILL[l])}
                style={{ width: `${(data[l] / max) * 100}%`, minWidth: data[l] ? 6 : 0 }}
              />
            </span>
            <span className="text-right font-bold tabular-nums">{data[l]}</span>
          </Link>
        </li>
      ))}
    </ul>
  );
}

type WeekPoint = DashboardMetrics['cases_per_week'][number];

/** Columnas apiladas por nivel (ALTA abajo), con la escala fija de colores de nivel. */
function WeeklyColumns({ points }: { points: WeekPoint[] }) {
  const [hover, setHover] = useState<number | null>(null);
  if (points.length === 0) return <p className="text-sm text-muted-foreground">Sin casos en el período.</p>;
  const shown = points.slice(-16);
  const W = 640;
  const H = 200;
  const pad = { l: 28, r: 8, t: 12, b: 24 };
  const max = Math.max(1, ...shown.map((p) => p.cases));
  const niceMax = max <= 5 ? max : Math.ceil(max / 5) * 5;
  const plotW = W - pad.l - pad.r;
  const plotH = H - pad.t - pad.b;
  const slot = plotW / shown.length;
  const barW = Math.min(28, slot * 0.62);
  const y = (v: number) => pad.t + plotH * (1 - v / niceMax);
  const fmt = (d: string) => new Date(`${d}T00:00:00`).toLocaleDateString('es-CL', { day: '2-digit', month: 'short' });
  const every = Math.ceil(shown.length / 8);
  const desc = shown
    .map((p) => `semana del ${fmt(p.week_start)}: ${p.cases} casos` + (p.by_level ? ` (${LEVELS.map((l) => `${p.by_level![l] ?? 0} ${l}`).join(', ')})` : ''))
    .join('; ');

  return (
    <div className="relative">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-52" role="img" aria-label={`Casos creados por semana: ${desc}`} onMouseLeave={() => setHover(null)}>
        {[0, niceMax / 2, niceMax].map((t) => (
          <g key={t}>
            <line x1={pad.l} x2={W - pad.r} y1={y(t)} y2={y(t)} stroke="hsl(var(--border))" strokeWidth={1} />
            <text x={pad.l - 6} y={y(t) + 4} textAnchor="end" fontSize={11} fill="hsl(var(--muted-foreground))">{Math.round(t)}</text>
          </g>
        ))}
        {shown.map((p, i) => {
          const x = pad.l + i * slot + (slot - barW) / 2;
          let acc = 0;
          const segments = LEVELS.map((l) => ({ l, n: p.by_level?.[l] ?? 0 }));
          const untriaged = p.cases - segments.reduce((a, s) => a + s.n, 0);
          if (untriaged > 0) segments.push({ l: 'SIN' as TriageLevel, n: untriaged });
          return (
            <g key={p.week_start} onMouseEnter={() => setHover(i)} opacity={hover === null || hover === i ? 1 : 0.55}>
              <rect x={pad.l + i * slot} y={pad.t} width={slot} height={plotH} fill="transparent" />
              {segments.map(({ l, n }) => {
                if (!n) return null;
                const top = y(acc + n);
                const h = y(acc) - top;
                acc += n;
                return (
                  <rect
                    key={l}
                    x={x}
                    y={top}
                    width={barW}
                    height={Math.max(0, h - 1)}
                    rx={2}
                    fill={l === ('SIN' as TriageLevel) ? 'hsl(var(--muted-foreground) / 0.35)' : `hsl(var(--${l.toLowerCase()}))`}
                  />
                );
              })}
              {(i % every === 0 || i === shown.length - 1) && (
                <text x={x + barW / 2} y={H - 6} textAnchor="middle" fontSize={11} fill="hsl(var(--muted-foreground))">{fmt(p.week_start)}</text>
              )}
            </g>
          );
        })}
      </svg>
      {hover !== null && (
        <div
          className="absolute top-0 px-3 py-2 bg-popover border border-border rounded-lg shadow-overlay text-sm pointer-events-none whitespace-nowrap"
          style={{ left: `${Math.min(85, Math.max(15, ((pad.l + (hover + 0.5) * slot) / W) * 100))}%`, transform: 'translateX(-50%)' }}
        >
          <p className="font-bold">Semana del {fmt(shown[hover].week_start)}</p>
          <p className="tabular-nums">{shown[hover].cases} casos</p>
          {shown[hover].by_level && (
            <p className="flex gap-3 tabular-nums">
              {LEVELS.map((l) => (
                <span key={l} className="inline-flex items-center gap-1">
                  <LevelBadge level={l} /> {shown[hover].by_level![l] ?? 0}
                </span>
              ))}
            </p>
          )}
        </div>
      )}
      <div className="mt-2 flex flex-wrap gap-x-5 gap-y-1 text-sm text-muted-foreground" aria-hidden>
        {LEVELS.map((l) => (
          <span key={l} className="inline-flex items-center gap-1.5">
            <span className={cn('w-2.5 h-2.5 rounded-sm', LEVEL_FILL[l])} /> {l}
          </span>
        ))}
        {points.length > shown.length && <span>Últimas {shown.length} semanas</span>}
      </div>
    </div>
  );
}

/** Conteos en una fila con reglas finas; cada estado abre la lista de Casos filtrada. */
function StatusRow({ data }: { data: Record<CaseStatus, number> }) {
  const keys = Object.keys(data) as CaseStatus[];
  return (
    <dl className="grid grid-cols-2 sm:grid-cols-4 border-t border-border">
      {keys.map((k) => (
        <Link key={k} to={`/casos?estado=${k}`} className="block pt-3 pb-1 pr-3 rounded-md hover:bg-accent/60 transition-colors">
          <dd className="text-lg font-extrabold tabular-nums">{data[k]}</dd>
          <dt className="text-xs text-muted-foreground">{CASE_STATUS_LABELS[k]}</dt>
        </Link>
      ))}
    </dl>
  );
}

/** Casos ALTA que hoy esperan más que el umbral, del más antiguo al más reciente. */
function AltaWaiting({ items, hours }: { items: QueueItem[]; hours: number }) {
  const late = items
    .filter((q) => q.level === 'ALTA' && q.status !== 'CERRADO' && q.waiting_hours > hours)
    .sort((a, b) => b.waiting_hours - a.waiting_hours);
  return (
    <section className={cn(cardClass, 'overflow-hidden')} aria-labelledby="dash-late">
      <div className="px-6 pt-5 pb-3 flex flex-wrap items-baseline justify-between gap-2">
        <h2 id="dash-late" className={sectionTitle}>ALTA con más de {hours} h de espera</h2>
        <span className="text-sm text-muted-foreground">Ahora, sin importar el período</span>
      </div>
      {late.length === 0 ? (
        <p className="px-6 pb-5 flex items-center gap-2 text-sm">
          <CheckCircle2 aria-hidden className="w-4 h-4 text-baja" /> Ningún caso ALTA espera más de {hours} h.
        </p>
      ) : (
        <div className="relative overflow-x-auto">
          <table className="w-full">
            <caption className="sr-only">Casos ALTA atrasados</caption>
            <thead className="bg-muted/60">
              <tr>
                <th scope="col" className={cn(thClass, 'pl-6')}>Código</th>
                <th scope="col" className={thClass}>Estado</th>
                <th scope="col" className={thClass}>Motivo</th>
                <th scope="col" className={cn(thClass, 'text-right pr-6')}>Espera</th>
              </tr>
            </thead>
            <tbody>
              {late.slice(0, 8).map((q) => (
                <tr key={q.code} className="hover:bg-accent/60">
                  <td className={cn(tdClass, 'pl-6')}>
                    <Link to={`/casos/${q.code}`} className="font-bold tabular-nums hover:text-brand hover:underline">{q.code}</Link>
                  </td>
                  <td className={cn(tdClass, 'text-muted-foreground')}>{CASE_STATUS_LABELS[q.status]}</td>
                  <td className={cn(tdClass, 'text-muted-foreground')}>
                    {q.escalation_rule ? RULE_LABELS[q.escalation_rule] ?? 'Escalamiento' : 'Puntaje'}
                  </td>
                  <td className={cn(tdClass, 'text-right pr-6 font-bold tabular-nums text-alta')}>{hoursText(q.waiting_hours)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {late.length > 8 && (
            <p className="px-6 py-3 text-sm text-muted-foreground">
              Y {late.length - 8} más. <Link to="/cola" className="font-semibold text-foreground hover:text-brand hover:underline">Ver la cola</Link>
            </p>
          )}
        </div>
      )}
    </section>
  );
}

function ModelStatusLine({ status }: { status: InferenceStatus }) {
  const real = status.provider === 'http';
  const online = real && status.reachable === true;
  return (
    <p className="flex flex-wrap items-center gap-2 text-sm">
      <span aria-hidden className={cn('w-2 h-2 rounded-full', online ? 'bg-baja' : real ? 'bg-media' : 'bg-muted-foreground')} />
      {online
        ? `Modelo conectado: ${status.model_version ?? 'sin versión'}${status.clinically_validated ? '' : ', prototipo sin validación clínica'}.`
        : real
          ? 'El modelo no responde: los resultados nuevos usan la IA simulada.'
          : 'Sin modelo conectado: los resultados usan la IA simulada.'}
      {!online && <SimulatedBadge />}
    </p>
  );
}

/** Desempeño del modelo por versión, con la validación del médico como referencia (KPI K5). */
function ModelPerformanceTable({ report, status }: { report: ModelPerformanceReport; status: InferenceStatus | null }) {
  return (
    <section className={cn(cardClass, 'overflow-hidden')}>
      <div className="p-6 pb-4">
        <h2 className={sectionTitle}>Desempeño del modelo por versión</h2>
        <p className="mt-1 text-sm text-muted-foreground max-w-[75ch]">
          Comparado con la validación del médico. Entre paréntesis, intervalo de confianza de 95 %.
        </p>
        {status && <div className="mt-3"><ModelStatusLine status={status} /></div>}
      </div>
      {report.versions.length === 0 ? (
        <p className="px-6 pb-6 text-sm text-muted-foreground">Aún no hay validaciones médicas de resultados de IA.</p>
      ) : (
        <div className="relative overflow-x-auto">
          <table className="w-full">
            <thead className="bg-muted/60">
              <tr>
                <th scope="col" className={thClass}>Versión</th>
                <th scope="col" className={cn(thClass, 'text-right')}>Evaluables</th>
                <th scope="col" className={cn(thClass, 'text-right')}>VP / VN / FP / FN</th>
                <th scope="col" className={cn(thClass, 'text-right')}>Exactitud</th>
                <th scope="col" className={cn(thClass, 'text-right')}>Sensibilidad</th>
                <th scope="col" className={cn(thClass, 'text-right')}>Especificidad</th>
                <th scope="col" className={cn(thClass, 'text-right')}>VPP / VPN</th>
                <th scope="col" className={thClass}>Meta ≥ {(report.k5_target * 100).toFixed(0)} %</th>
              </tr>
            </thead>
            <tbody className="tabular-nums">
              {report.versions.map((v) => (
                <tr key={`${v.model_version}-${v.is_simulated}`}>
                  <td className={tdClass}>
                    <span className="inline-flex items-center gap-2 font-semibold">
                      {v.model_version}
                      {v.is_simulated && <SimulatedBadge />}
                    </span>
                  </td>
                  <td className={cn(tdClass, 'text-right')}>
                    {v.evaluable}
                    {v.not_evaluable > 0 && <span className="text-muted-foreground"> (+{v.not_evaluable} no eval.)</span>}
                  </td>
                  <td className={cn(tdClass, 'text-right')}>
                    {v.true_positives} / {v.true_negatives} / {v.false_positives} / {v.false_negatives}
                  </td>
                  <td className={cn(tdClass, 'text-right')}>{pctCi(v.accuracy, v.accuracy_ci95)}</td>
                  <td className={cn(tdClass, 'text-right')}>{pctCi(v.sensitivity, v.sensitivity_ci95)}</td>
                  <td className={cn(tdClass, 'text-right')}>{pctCi(v.specificity, v.specificity_ci95)}</td>
                  <td className={cn(tdClass, 'text-right')}>{pct(v.ppv)} / {pct(v.npv)}</td>
                  <td className={tdClass}>
                    {v.meets_k5 === null ? (
                      <span className="text-sm text-muted-foreground">{v.is_simulated ? 'No aplica' : 'Muestra insuficiente'}</span>
                    ) : (
                      <Status ok={v.meets_k5} />
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

const CLINICAL_ROLES = ['MEDICO', 'ADMINISTRATIVO'];

export default function Dashboard({ me }: { me: Me }) {
  const [params, setParams] = useSearchParams();
  const rawPeriod = params.get('periodo') as PeriodKey | null;
  const period: PeriodKey = PERIODS.some((p) => p.value === rawPeriod) ? rawPeriod! : 'todo';
  const from = params.get('desde') ?? '';
  const to = params.get('hasta') ?? '';
  const hours = Math.max(1, Number(params.get('alerta')) || 24);
  const [hoursInput, setHoursInput] = useState(String(hours));
  const ranges = useMemo(() => periodRanges(period, from, to), [period, from, to]);
  const [data, setData] = useState<DashboardMetrics | null>(null);
  const [previous, setPrevious] = useState<DashboardMetrics | null>(null);
  const [model, setModel] = useState<ModelPerformanceReport | null>(null);
  const [queue, setQueue] = useState<QueueItem[] | null>(null);
  const [inference, setInference] = useState<InferenceStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showTable, setShowTable] = useState(false);
  const clinical = CLINICAL_ROLES.includes(me.role);

  const setParam = (changes: Record<string, string | null>) => {
    const next = new URLSearchParams(params);
    for (const [k, v] of Object.entries(changes)) {
      if (v) next.set(k, v);
      else next.delete(k);
    }
    setParams(next, { replace: true });
  };

  const load = useCallback(async () => {
    const range = apiRange(ranges.current);
    const [r, m, prev, q, inf] = await Promise.all([
      apiClient.getDashboard({ ...range, alta_pending_hours: hours }),
      apiClient.getModelPerformance(range),
      ranges.previous ? apiClient.getDashboard({ ...apiRange(ranges.previous), alta_pending_hours: hours }) : Promise.resolve(null),
      clinical ? apiClient.getQueue(true) : Promise.resolve(null),
      me.role === 'ADMINISTRATIVO' ? Promise.resolve(null) : apiClient.getInferenceStatus(),
    ]);
    if (r.data) {
      setData(r.data);
      setError(null);
    } else setError(r.error || 'No se pudieron cargar las métricas.');
    setPrevious(prev?.data ?? null);
    // Solo MEDICO y ADMIN ven el desempeño del modelo; para el resto la sección no se muestra
    setModel(m.data ?? null);
    setQueue(q?.data ?? null);
    setInference(inf?.data ?? null);
  }, [ranges, hours, clinical, me.role]);

  useEffect(() => {
    load();
  }, [load]);

  // jsPDF y la tipografía se cargan solo al exportar
  const exportPdf = async () => {
    if (!data) return;
    try {
      const [{ buildManagementReport }, { loadPdfAssets }] = await Promise.all([
        import('../utils/generateManagementReport'),
        import('../utils/pdfTheme'),
      ]);
      const doc = buildManagementReport({
        data,
        previous,
        model,
        inference,
        altaWaiting: queue?.filter((q) => q.level === 'ALTA' && q.status !== 'CERRADO' && q.waiting_hours > hours) ?? null,
        generatedBy: me.full_name,
        assets: await loadPdfAssets(),
      });
      doc.save(`informe-gestion-aurora-care-${new Date().toISOString().slice(0, 10)}.pdf`);
    } catch {
      setError('No se pudo generar el informe PDF. Intente de nuevo.');
    }
  };

  const total = data?.total_cases ?? 0;
  const alta = data?.cases_by_level.ALTA ?? 0;
  const summary = data && [
    {
      label: 'Casos',
      value: total.toLocaleString('es-CL'),
      note: <Delta now={total} before={previous?.total_cases} />,
    },
    {
      label: 'Casos ALTA',
      value: alta.toLocaleString('es-CL'),
      note: <span className="block text-xs text-muted-foreground tabular-nums">{total ? `${dec((alta / total) * 100, 0)} % del total` : '—'}</span>,
    },
    {
      label: 'ALTA: triage a revisión',
      value: hoursText(data.avg_triage_to_review_hours_by_level.ALTA),
      note: <Delta kind="hours" now={data.avg_triage_to_review_hours_by_level.ALTA} before={previous?.avg_triage_to_review_hours_by_level.ALTA} />,
    },
    {
      label: 'Triage aprobado por el médico',
      value: pct(data.triage_agreement_rate),
      note: <Delta kind="rate" now={data.triage_agreement_rate} before={previous?.triage_agreement_rate} />,
    },
  ];

  return (
    <div className={pageClass}>
      <ListHeader
        title="Dashboard"
        actions={
          <button type="button" className={secondaryButton} onClick={exportPdf} disabled={!data}>
            <FileDown aria-hidden className="w-4 h-4" /> Exportar informe PDF
          </button>
        }
      />

      <div className="mt-6 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3">
          <Segmented
            label="Período"
            value={period}
            onChange={(v) => setParam({ periodo: v === 'todo' ? null : v, ...(v === 'rango' ? {} : { desde: null, hasta: null }) })}
            options={PERIODS}
          />
          {period === 'rango' && (
            <span className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
              <label htmlFor="d-from" className="sr-only">Desde</label>
              <input id="d-from" type="date" className={cn(inputClass, 'h-9 w-40')} value={from} max={to || undefined}
                onChange={(e) => setParam({ desde: e.target.value || null })} />
              a
              <label htmlFor="d-to" className="sr-only">Hasta</label>
              <input id="d-to" type="date" className={cn(inputClass, 'h-9 w-40')} value={to} min={from || undefined}
                onChange={(e) => setParam({ hasta: e.target.value || null })} />
            </span>
          )}
        </div>
        <label className="flex items-center gap-2 text-sm text-muted-foreground">
          ALTA atrasado tras
          <input type="number" min={1} className={cn(inputClass, 'h-9 w-20 tabular-nums')} value={hoursInput}
            onChange={(e) => setHoursInput(e.target.value)}
            onBlur={() => setParam({ alerta: Number(hoursInput) > 0 && Number(hoursInput) !== 24 ? String(Math.round(Number(hoursInput))) : null })}
            onKeyDown={(e) => e.key === 'Enter' && (e.target as HTMLInputElement).blur()} />
          h
        </label>
      </div>

      <ErrorMessage className="mt-4">{error}</ErrorMessage>
      {!data || !summary ? (
        <Loading label="Cargando métricas…" />
      ) : (
        <div className="mt-6 space-y-6">
          <dl className={cn(cardClass, 'grid grid-cols-2 lg:grid-cols-4 divide-x divide-border')}>
            {summary.map(({ label, value, note }) => (
              <div key={label} className="px-6 py-4 [&:nth-child(3)]:border-l-0 lg:[&:nth-child(3)]:border-l">
                <dt className="text-sm text-muted-foreground">{label}</dt>
                <dd className="mt-1 text-2xl font-extrabold tabular-nums">{value}</dd>
                <dd>{note}</dd>
              </div>
            ))}
          </dl>

          <div className="grid xl:grid-cols-[minmax(0,7fr)_minmax(0,5fr)] gap-6 items-start">
            <Panel title="Casos creados por semana">
              <WeeklyColumns points={data.cases_per_week} />
            </Panel>
            <Panel title="Nivel vigente y estado">
              <LevelBars data={data.cases_by_level} />
              <div className="mt-4">
                <StatusRow data={data.cases_by_status} />
              </div>
            </Panel>
          </div>

          {queue && <AltaWaiting items={queue} hours={hours} />}

          <section className={cn(cardClass, 'overflow-hidden')}>
            <div className="px-6 pt-5 pb-3">
              <h2 className={sectionTitle}>Indicadores y metas</h2>
            </div>
            <div className="relative overflow-x-auto">
<table className="w-full">
              <caption className="sr-only">Indicadores y metas</caption>
              <thead className="bg-muted/60">
                <tr>
                  <th scope="col" className={thClass}>Indicador</th>
                  <th scope="col" className={cn(thClass, 'text-right')}>Valor</th>
                  <th scope="col" className={thClass}>Meta</th>
                  <th scope="col" className={thClass}>Estado</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th scope="row" className={cn(tdClass, 'text-left font-normal')}>Casos en el período</th>
                  <td className={cn(tdClass, 'text-right text-lg font-extrabold tabular-nums')}>{data.total_cases.toLocaleString('es-CL')}</td>
                  <td className={cn(tdClass, 'text-muted-foreground')}>—</td>
                  <td className={tdClass}><Status ok={null} /></td>
                </tr>
                <tr>
                  <th scope="row" className={cn(tdClass, 'text-left font-normal')}>Creación → triage (promedio)</th>
                  <td className={cn(tdClass, 'text-right text-lg font-extrabold tabular-nums')}>{formatSeconds(data.avg_creation_to_triage_seconds)}</td>
                  <td className={cn(tdClass, 'text-muted-foreground')}>≤ 5 min</td>
                  <td className={tdClass}>
                    <Status ok={data.avg_creation_to_triage_seconds === null ? null : data.avg_creation_to_triage_seconds <= data.kpi_creation_to_triage_target_seconds} />
                  </td>
                </tr>
                <tr>
                  <th scope="row" className={cn(tdClass, 'text-left font-normal')}>Casos ALTA pendientes más de {data.alta_pending_threshold_hours} h</th>
                  <td className={cn(tdClass, 'text-right text-lg font-extrabold tabular-nums', data.alta_pending_over_hours > 0 && 'text-alta')}>
                    {data.alta_pending_over_hours}
                  </td>
                  <td className={cn(tdClass, 'text-muted-foreground')}>0</td>
                  <td className={tdClass}><Status ok={data.alta_pending_over_hours === 0} /></td>
                </tr>
                <tr>
                  <th scope="row" className={cn(tdClass, 'text-left font-normal')}>
                    Tiempo de respuesta de la API, p95 <span className="text-muted-foreground">({data.api_requests} solicitudes)</span>
                  </th>
                  <td className={cn(tdClass, 'text-right text-lg font-extrabold tabular-nums')}>{data.api_p95_ms === null ? '—' : `${data.api_p95_ms.toFixed(0)} ms`}</td>
                  <td className={cn(tdClass, 'text-muted-foreground')}>&lt; 3 s</td>
                  <td className={tdClass}><Status ok={data.api_p95_ms === null ? null : data.api_p95_ms < data.kpi_api_p95_target_ms} /></td>
                </tr>
                <tr>
                  <th scope="row" className={cn(tdClass, 'text-left font-normal')}>
                    Errores del servidor
                  </th>
                  <td className={cn(tdClass, 'text-right text-lg font-extrabold tabular-nums', data.server_errors > 0 && 'text-alta')}>
                    {data.server_errors}
                    {data.server_error_rate !== null && (
                      <span className="ml-1 text-sm font-normal text-muted-foreground">
                        ({(data.server_error_rate * 100).toLocaleString('es-CL', { maximumFractionDigits: 2 })} %)
                      </span>
                    )}
                  </td>
                  <td className={cn(tdClass, 'text-muted-foreground')}>—</td>
                  <td className={tdClass}><Status ok={null} /></td>
                </tr>
              </tbody>
            </table>
</div>
          </section>

          <section className={cn(cardClass, 'overflow-hidden')}>
            <div className="px-6 pt-6 pb-3">
              <h2 className={sectionTitle}>Calidad de las decisiones</h2>
            </div>
            <div className="relative overflow-x-auto">
<table className="w-full">
              <caption className="sr-only">Indicadores de calidad del triage y de la IA</caption>
              <thead className="bg-muted/60">
                <tr>
                  <th scope="col" className={thClass}>Indicador</th>
                  <th scope="col" className={cn(thClass, 'text-right')}>Valor</th>
                  <th scope="col" className={thClass}>Desglose</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th scope="row" className={cn(tdClass, 'text-left font-normal align-top')}>Triage → revisión médica (promedio)</th>
                  <td className={cn(tdClass, 'text-right text-muted-foreground align-top')}>por nivel</td>
                  <td className={cn(tdClass, 'whitespace-normal')}>
                    <span className="flex flex-wrap gap-x-6 gap-y-1">
                      {LEVELS.map((l) => {
                        const h = data.avg_triage_to_review_hours_by_level[l];
                        return (
                          <span key={l} className="inline-flex items-center gap-2">
                            <LevelBadge level={l} />
                            <strong className="tabular-nums">{h === null ? '—' : `${dec(h)} h`}</strong>
                          </span>
                        );
                      })}
                    </span>
                  </td>
                </tr>
                <tr>
                  <th scope="row" className={cn(tdClass, 'text-left font-normal')}>Ajustes médicos del nivel</th>
                  <td className={cn(tdClass, 'text-right text-lg font-extrabold tabular-nums')}>{pct(data.override_ratio)}</td>
                  <td className={cn(tdClass, 'whitespace-normal text-muted-foreground')}>
                    {data.triage_overrides} de {data.triage_total} cálculos ajustados
                  </td>
                </tr>
                <tr>
                  <th scope="row" className={cn(tdClass, 'text-left font-normal align-top')}>
                    Concordancia IA – médico
                    <span className="block text-xs text-muted-foreground">{data.ai_validations_total} validaciones</span>
                  </th>
                  <td className={cn(tdClass, 'text-right text-lg font-extrabold tabular-nums align-top')}>{pct(data.ai_agreement_rate)}</td>
                  <td className={cn(tdClass, 'whitespace-normal')}>
                    <span className="flex flex-wrap gap-x-5 gap-y-1">
                      {(Object.keys(AI_VERDICT_LABELS) as AIVerdict[]).map((v) => (
                        <span key={v}>
                          <strong className="tabular-nums">{data.ai_validations_by_verdict[v] ?? 0}</strong>{' '}
                          <span className="text-muted-foreground">{AI_VERDICT_LABELS[v].toLowerCase()}</span>
                        </span>
                      ))}
                    </span>
                    {data.ai_validations_simulated > 0 && (
                      <span className="mt-2 flex items-center gap-2 text-sm">
                        <SimulatedBadge />
                        {data.ai_validations_simulated} de {data.ai_validations_total} sobre IA simulada
                      </span>
                    )}
                  </td>
                </tr>
                <tr>
                  <th scope="row" className={cn(tdClass, 'text-left font-normal align-top')}>
                    Aprobación del triage
                    <span className="block text-xs text-muted-foreground">{data.triage_assessments_total} evaluaciones</span>
                  </th>
                  <td className={cn(tdClass, 'text-right text-lg font-extrabold tabular-nums align-top')}>{pct(data.triage_agreement_rate)}</td>
                  <td className={cn(tdClass, 'whitespace-normal')}>
                    <span className="flex flex-wrap gap-x-5 gap-y-1">
                      {(Object.keys(TRIAGE_ASSESSMENT_LABELS) as TriageAssessment[]).map((x) => (
                        <span key={x}>
                          <strong className="tabular-nums">{data.triage_assessments_by_value[x] ?? 0}</strong>{' '}
                          <span className="text-muted-foreground">{TRIAGE_ASSESSMENT_LABELS[x].split(' (')[0].toLowerCase()}</span>
                        </span>
                      ))}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
</div>
          </section>

          {model && <ModelPerformanceTable report={model} status={inference} />}

          <div>
            <button className={ghostButton} onClick={() => setShowTable((v) => !v)} aria-expanded={showTable}>
              {showTable ? 'Ocultar' : 'Ver'} los datos de los gráficos en tabla
            </button>
            {showTable && (
              <table className="mt-2 w-full max-w-xl">
                <tbody>
                  {data.cases_per_week.map((p) => (
                    <tr key={p.week_start}>
                      <td className={cn(tdClass, 'text-muted-foreground')}>Semana del {p.week_start}</td>
                      <td className={cn(tdClass, 'text-right tabular-nums')}>{p.cases} casos</td>
                    </tr>
                  ))}
                  {LEVELS.map((l) => (
                    <tr key={l}>
                      <td className={cn(tdClass, 'text-muted-foreground')}>Nivel {l}</td>
                      <td className={cn(tdClass, 'text-right tabular-nums')}>{data.cases_by_level[l]} casos</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
