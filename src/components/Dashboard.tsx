import { useCallback, useEffect, useState, type ReactNode } from 'react';
import { AlertTriangle, CheckCircle2, FileDown, Minus } from 'lucide-react';
import { apiClient } from '../services/api';
import type {
  AIVerdict,
  CaseStatus,
  DashboardMetrics,
  Me,
  ModelPerformanceReport,
  TriageAssessment,
  TriageLevel,
} from '../types';
import { AI_VERDICT_LABELS, CASE_STATUS_LABELS, TRIAGE_ASSESSMENT_LABELS } from '../types';
import { LEVEL_FILL, LEVEL_RING, LEVEL_TEXT } from '../constants';
import { cn } from '../lib/cn';
import { SimulatedBadge } from './Badges';
import { ErrorMessage, Loading } from './Feedback';
import { cardClass, ghostButton, secondaryButton, inputClass, labelClass, pageClass, pageTitle, sectionTitle, tdClass, thClass } from './ui';

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

function Panel({ title, children, className }: { title: string; children: ReactNode; className?: string }) {
  return (
    <section className={cn(cardClass, 'p-6', className)}>
      <h2 className={cn(sectionTitle, 'mb-4')}>{title}</h2>
      {children}
    </section>
  );
}

function LevelBars({ data }: { data: Record<TriageLevel, number> }) {
  const max = Math.max(1, ...LEVELS.map((l) => data[l]));
  return (
    <ul className="space-y-3">
      {LEVELS.map((l) => (
        <li key={l} className="grid grid-cols-[5rem_1fr_3rem] items-center gap-3">
          <span className={cn('inline-flex items-center gap-1.5 text-xs font-extrabold', LEVEL_TEXT[l])}>
            <span aria-hidden className={cn('w-3 h-3 rounded-full border-current', LEVEL_RING[l])} />
            {l}
          </span>
          <span aria-hidden className="h-3 rounded-full bg-muted overflow-hidden">
            <span
              className={cn('block h-full rounded-full', LEVEL_FILL[l])}
              style={{ width: `${(data[l] / max) * 100}%`, minWidth: data[l] ? 6 : 0 }}
            />
          </span>
          <span className="text-right font-bold tabular-nums">{data[l]}</span>
        </li>
      ))}
    </ul>
  );
}

function WeeklyLine({ points }: { points: Array<{ week_start: string; cases: number }> }) {
  const [hover, setHover] = useState<number | null>(null);
  if (points.length === 0) return <p className="text-sm text-muted-foreground">Sin casos en el período.</p>;
  const W = 560;
  const H = 180;
  const pad = { l: 32, r: 12, t: 14, b: 26 };
  const max = Math.max(1, ...points.map((p) => p.cases));
  const x = (i: number) => pad.l + (points.length === 1 ? (W - pad.l - pad.r) / 2 : (i * (W - pad.l - pad.r)) / (points.length - 1));
  const y = (v: number) => pad.t + (H - pad.t - pad.b) * (1 - v / max);
  const path = points.map((p, i) => `${i ? 'L' : 'M'}${x(i)},${y(p.cases)}`).join(' ');
  const area = `${path} L${x(points.length - 1)},${H - pad.b} L${x(0)},${H - pad.b} Z`;
  const ticks = [0, Math.ceil(max / 2), max];
  const fmt = (d: string) => new Date(`${d}T00:00:00`).toLocaleDateString('es-CL', { day: '2-digit', month: 'short' });

  return (
    <div className="relative">
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="w-full h-44"
        role="img"
        aria-label={`Casos creados por semana: ${points.map((p) => `semana del ${fmt(p.week_start)}, ${p.cases}`).join('; ')}`}
        onMouseLeave={() => setHover(null)}
      >
        {ticks.map((t) => (
          <g key={t}>
            <line x1={pad.l} x2={W - pad.r} y1={y(t)} y2={y(t)} stroke="hsl(var(--border))" strokeWidth={1} />
            <text x={pad.l - 8} y={y(t) + 4} textAnchor="end" fontSize={11} fill="hsl(var(--muted-foreground))">{t}</text>
          </g>
        ))}
        <path d={area} fill="hsl(var(--brand) / 0.08)" />
        <path d={path} fill="none" stroke="hsl(var(--brand))" strokeWidth={2.25} strokeLinejoin="round" strokeLinecap="round" />
        {points.map((p, i) => (
          <g key={p.week_start}>
            <rect
              x={x(i) - W / points.length / 2}
              y={pad.t}
              width={W / points.length}
              height={H - pad.t - pad.b}
              fill="transparent"
              onMouseEnter={() => setHover(i)}
            />
            <circle cx={x(i)} cy={y(p.cases)} r={hover === i ? 5 : 3.5} fill="hsl(var(--brand))" stroke="hsl(var(--card))" strokeWidth={2} />
            {(i === 0 || i === points.length - 1 || points.length <= 6) && (
              <text x={x(i)} y={H - 6} textAnchor={points.length > 1 && i === 0 ? "start" : points.length > 1 && i === points.length - 1 ? "end" : "middle"} fontSize={11} fill="hsl(var(--muted-foreground))">{fmt(p.week_start)}</text>
            )}
          </g>
        ))}
        {hover !== null && (
          <line x1={x(hover)} x2={x(hover)} y1={pad.t} y2={H - pad.b} stroke="hsl(var(--muted-foreground))" strokeDasharray="3 3" />
        )}
      </svg>
      {hover !== null && (
        <div
          className="absolute top-0 px-2.5 py-1.5 bg-popover border border-border rounded-lg shadow-overlay text-sm pointer-events-none whitespace-nowrap"
          style={{ left: `${(x(hover) / W) * 100}%`, transform: 'translateX(-50%)' }}
        >
          Semana del {fmt(points[hover].week_start)}: <strong className="tabular-nums">{points[hover].cases}</strong> casos
        </div>
      )}
    </div>
  );
}

/** Conteos en una fila con reglas finas, sin tarjetas. */
function CountRow({ items }: { items: Array<{ label: string; value: ReactNode }> }) {
  return (
    <dl className="grid divide-x divide-border border-t border-border" style={{ gridTemplateColumns: `repeat(${items.length}, minmax(0, 1fr))` }}>
      {items.map((it) => (
        <div key={it.label} className="pt-3 px-3 first:pl-0">
          <dd className="text-lg font-extrabold tabular-nums">{it.value}</dd>
          <dt className="text-xs text-muted-foreground">{it.label}</dt>
        </div>
      ))}
    </dl>
  );
}

/** Desempeño del modelo por versión, con la validación del médico como referencia (KPI K5). */
function ModelPerformanceTable({ report }: { report: ModelPerformanceReport }) {
  return (
    <section className={cn(cardClass, 'overflow-hidden')}>
      <div className="p-6 pb-4">
        <h2 className={sectionTitle}>Desempeño del modelo por versión</h2>
        <p className="mt-1 text-sm text-muted-foreground max-w-[75ch]">
          Comparado con la validación del médico. Entre paréntesis, intervalo de confianza de 95 %.
        </p>
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

export default function Dashboard({ me }: { me: Me }) {
  const [from, setFrom] = useState('');
  const [to, setTo] = useState('');
  const [hours, setHours] = useState(24);
  const [data, setData] = useState<DashboardMetrics | null>(null);
  const [model, setModel] = useState<ModelPerformanceReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showTable, setShowTable] = useState(false);

  const load = useCallback(async () => {
    const range = { from: from ? `${from}T00:00:00` : undefined, to: to ? `${to}T23:59:59` : undefined };
    const [r, m] = await Promise.all([
      apiClient.getDashboard({ ...range, alta_pending_hours: hours }),
      apiClient.getModelPerformance(range),
    ]);
    if (r.data) {
      setData(r.data);
      setError(null);
    } else setError(r.error || 'No se pudieron cargar las métricas.');
    // Solo MEDICO y ADMIN ven el desempeño del modelo; para el resto la sección no se muestra
    setModel(m.data ?? null);
  }, [from, to, hours]);

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
      const doc = buildManagementReport({ data, model, generatedBy: me.full_name, assets: await loadPdfAssets() });
      doc.save(`informe-gestion-aurora-care-${new Date().toISOString().slice(0, 10)}.pdf`);
    } catch {
      setError('No se pudo generar el informe PDF. Intente de nuevo.');
    }
  };

  return (
    <div className={pageClass}>
      <div className="flex flex-wrap items-end justify-between gap-6">
        <div>
          <h1 className={pageTitle}>Dashboard</h1>
        </div>
        <div className="flex flex-wrap items-end gap-3">
          <div>
            <label className={labelClass} htmlFor="d-from">Desde</label>
            <input id="d-from" type="date" className={cn(inputClass, 'w-44')} value={from} onChange={(e) => setFrom(e.target.value)} />
          </div>
          <div>
            <label className={labelClass} htmlFor="d-to">Hasta</label>
            <input id="d-to" type="date" className={cn(inputClass, 'w-44')} value={to} onChange={(e) => setTo(e.target.value)} />
          </div>
          <div>
            <label className={labelClass} htmlFor="d-hours">Alerta ALTA tras (h)</label>
            <input id="d-hours" type="number" min={1} className={cn(inputClass, 'w-28')} value={hours}
              onChange={(e) => setHours(Math.max(1, Number(e.target.value) || 1))} />
          </div>
          <button type="button" className={secondaryButton} onClick={exportPdf} disabled={!data}>
            <FileDown className="w-4 h-4" /> Exportar informe PDF
          </button>
        </div>
      </div>

      <ErrorMessage className="mt-4">{error}</ErrorMessage>
      {!data ? (
        <Loading label="Cargando métricas…" />
      ) : (
        <div className="mt-6 space-y-6">
          <section className={cn(cardClass, 'overflow-hidden')}>
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
          </section>

          <div className="grid xl:grid-cols-2 gap-6">
            <Panel title="Casos por nivel de triage vigente">
              <LevelBars data={data.cases_by_level} />
              <div className="mt-5">
                <CountRow
                  items={(Object.keys(data.cases_by_status) as CaseStatus[]).map((s) => ({
                    label: CASE_STATUS_LABELS[s],
                    value: data.cases_by_status[s],
                  }))}
                />
              </div>
            </Panel>
            <Panel title="Casos creados por semana">
              <WeeklyLine points={data.cases_per_week} />
            </Panel>
          </div>

          <section className={cn(cardClass, 'overflow-hidden')}>
            <div className="px-6 pt-6 pb-3">
              <h2 className={sectionTitle}>Calidad de las decisiones</h2>
            </div>
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
                            <span className={cn('inline-flex items-center gap-1.5 text-xs font-extrabold', LEVEL_TEXT[l])}>
                              <span aria-hidden className={cn('w-3 h-3 rounded-full border-current', LEVEL_RING[l])} />
                              {l}
                            </span>
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
          </section>

          {model && <ModelPerformanceTable report={model} />}

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
