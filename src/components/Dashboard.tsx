import { useCallback, useEffect, useState } from 'react';
import { AlertTriangle, BarChart3, CheckCircle2, Clock, Gauge, Loader2, Timer } from 'lucide-react';
import { apiClient } from '../services/api';
import type { CaseStatus, DashboardMetrics, TriageLevel } from '../types';
import { CASE_STATUS_LABELS } from '../types';
import { cardClass, errorBox, inputClass, labelClass } from './ui';

const LEVELS: TriageLevel[] = ['ALTA', 'MEDIA', 'BAJA'];
// Los niveles de triage son estados: color reservado + etiqueta de texto siempre visible
const LEVEL_FILL: Record<TriageLevel, string> = { ALTA: '#ef4444', MEDIA: '#f59e0b', BAJA: '#22c55e' };

function formatSeconds(s: number | null): string {
  if (s === null) return '—';
  if (s < 60) return `${s.toFixed(0)} s`;
  if (s < 3600) return `${(s / 60).toFixed(1)} min`;
  return `${(s / 3600).toFixed(1)} h`;
}

function Kpi({
  icon: Icon,
  label,
  value,
  hint,
  ok,
}: {
  icon: typeof Gauge;
  label: string;
  value: string;
  hint?: string;
  ok?: boolean | null;
}) {
  return (
    <div className={`${cardClass} p-3`}>
      <div className="flex items-center justify-between mb-1">
        <Icon className="w-4 h-4 text-primary" />
        {ok !== undefined && ok !== null && (
          <span className={`text-[10px] font-semibold flex items-center gap-1 ${ok ? 'text-green-400' : 'text-orange-400'}`}>
            {ok ? <CheckCircle2 className="w-3 h-3" /> : <AlertTriangle className="w-3 h-3" />}
            {ok ? 'Cumple' : 'Fuera de meta'}
          </span>
        )}
      </div>
      <p className="text-xl font-bold text-foreground">{value}</p>
      <p className="text-[10px] text-muted-foreground">{label}</p>
      {hint && <p className="text-[10px] text-muted-foreground mt-0.5">{hint}</p>}
    </div>
  );
}

function LevelBars({ data }: { data: Record<TriageLevel, number> }) {
  const max = Math.max(1, ...LEVELS.map((l) => data[l]));
  return (
    <div className="space-y-2" role="img" aria-label={LEVELS.map((l) => `${l}: ${data[l]}`).join(', ')}>
      {LEVELS.map((l) => (
        <div key={l} className="flex items-center gap-2 group" title={`${l}: ${data[l]} casos`}>
          <span className="w-12 text-[10px] font-semibold text-muted-foreground">{l}</span>
          <div className="flex-1 h-5 bg-secondary/40 rounded">
            <div
              className="h-5 rounded-r transition-all group-hover:opacity-80"
              style={{ width: `${(data[l] / max) * 100}%`, background: LEVEL_FILL[l], minWidth: data[l] ? 4 : 0 }}
            />
          </div>
          <span className="w-8 text-right text-xs text-foreground">{data[l]}</span>
        </div>
      ))}
    </div>
  );
}

function WeeklyLine({ points }: { points: Array<{ week_start: string; cases: number }> }) {
  const [hover, setHover] = useState<number | null>(null);
  if (points.length === 0) return <p className="text-xs text-muted-foreground">Sin casos en el período.</p>;
  const W = 520;
  const H = 160;
  const pad = { l: 28, r: 12, t: 12, b: 24 };
  const max = Math.max(1, ...points.map((p) => p.cases));
  const x = (i: number) => pad.l + (points.length === 1 ? (W - pad.l - pad.r) / 2 : (i * (W - pad.l - pad.r)) / (points.length - 1));
  const y = (v: number) => pad.t + (H - pad.t - pad.b) * (1 - v / max);
  const path = points.map((p, i) => `${i ? 'L' : 'M'}${x(i)},${y(p.cases)}`).join(' ');
  const ticks = [0, Math.ceil(max / 2), max];
  const fmt = (d: string) => new Date(`${d}T00:00:00`).toLocaleDateString('es-CL', { day: '2-digit', month: 'short' });

  return (
    <div className="relative">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-40" onMouseLeave={() => setHover(null)}>
        {ticks.map((t) => (
          <g key={t}>
            <line x1={pad.l} x2={W - pad.r} y1={y(t)} y2={y(t)} stroke="hsl(var(--border))" strokeWidth={1} />
            <text x={pad.l - 6} y={y(t) + 3} textAnchor="end" fontSize={9} fill="hsl(var(--muted-foreground))">{t}</text>
          </g>
        ))}
        <path d={path} fill="none" stroke="hsl(var(--primary))" strokeWidth={2} strokeLinejoin="round" />
        {points.map((p, i) => (
          <g key={p.week_start}>
            <rect
              x={x(i) - (W / points.length) / 2}
              y={pad.t}
              width={W / points.length}
              height={H - pad.t - pad.b}
              fill="transparent"
              onMouseEnter={() => setHover(i)}
            />
            <circle cx={x(i)} cy={y(p.cases)} r={hover === i ? 5 : 4} fill="hsl(var(--primary))" stroke="hsl(var(--card))" strokeWidth={2} />
            {(i === 0 || i === points.length - 1 || points.length <= 6) && (
              <text x={x(i)} y={H - 6} textAnchor="middle" fontSize={9} fill="hsl(var(--muted-foreground))">{fmt(p.week_start)}</text>
            )}
          </g>
        ))}
        {hover !== null && (
          <line x1={x(hover)} x2={x(hover)} y1={pad.t} y2={H - pad.b} stroke="hsl(var(--muted-foreground))" strokeDasharray="3 3" />
        )}
      </svg>
      {hover !== null && (
        <div
          className="absolute top-0 px-2 py-1 bg-card border border-border rounded text-[10px] text-foreground pointer-events-none"
          style={{ left: `${(x(hover) / W) * 100}%`, transform: 'translateX(-50%)' }}
        >
          Semana del {fmt(points[hover].week_start)}: <strong>{points[hover].cases}</strong> casos
        </div>
      )}
    </div>
  );
}

export default function Dashboard() {
  const [from, setFrom] = useState('');
  const [to, setTo] = useState('');
  const [hours, setHours] = useState(24);
  const [data, setData] = useState<DashboardMetrics | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showTable, setShowTable] = useState(false);

  const load = useCallback(async () => {
    const r = await apiClient.getDashboard({
      from: from ? `${from}T00:00:00` : undefined,
      to: to ? `${to}T23:59:59` : undefined,
      alta_pending_hours: hours,
    });
    if (r.data) {
      setData(r.data);
      setError(null);
    } else setError(r.error || 'Error al cargar métricas');
  }, [from, to, hours]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 space-y-4">
      <div>
        <h2 className="text-lg font-bold text-foreground flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-primary" /> Dashboard
        </h2>
        <p className="mt-0.5 text-xs text-muted-foreground">Métricas agregadas, sin datos identificables de pacientes.</p>
      </div>

      <div className="flex flex-wrap items-end gap-3">
        <div>
          <label className={labelClass} htmlFor="d-from">Desde</label>
          <input id="d-from" type="date" className={inputClass} value={from} onChange={(e) => setFrom(e.target.value)} />
        </div>
        <div>
          <label className={labelClass} htmlFor="d-to">Hasta</label>
          <input id="d-to" type="date" className={inputClass} value={to} onChange={(e) => setTo(e.target.value)} />
        </div>
        <div>
          <label className={labelClass} htmlFor="d-hours">ALTA pendiente más de (h)</label>
          <input id="d-hours" type="number" min={1} className={`${inputClass} w-24`} value={hours}
            onChange={(e) => setHours(Math.max(1, Number(e.target.value) || 1))} />
        </div>
      </div>

      {error && <div className={errorBox}>{error}</div>}
      {!data ? (
        <div className="flex justify-center py-12"><Loader2 className="w-6 h-6 animate-spin text-primary" /></div>
      ) : (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <Kpi icon={BarChart3} label="Casos en el período" value={data.total_cases.toLocaleString('es-CL')} />
            <Kpi
              icon={Timer}
              label="Creación → triage (promedio)"
              value={formatSeconds(data.avg_creation_to_triage_seconds)}
              hint="Meta ≤ 5 min"
              ok={data.avg_creation_to_triage_seconds === null ? null : data.avg_creation_to_triage_seconds <= data.kpi_creation_to_triage_target_seconds}
            />
            <Kpi
              icon={AlertTriangle}
              label={`Casos ALTA pendientes > ${data.alta_pending_threshold_hours} h`}
              value={String(data.alta_pending_over_hours)}
              ok={data.alta_pending_over_hours === 0}
            />
            <Kpi
              icon={Gauge}
              label={`p95 tiempo de respuesta API (${data.api_requests} requests)`}
              value={data.api_p95_ms === null ? '—' : `${data.api_p95_ms.toFixed(0)} ms`}
              hint="Meta < 3 s"
              ok={data.api_p95_ms === null ? null : data.api_p95_ms < data.kpi_api_p95_target_ms}
            />
          </div>

          <div className="grid lg:grid-cols-2 gap-4">
            <div className={`${cardClass} p-4`}>
              <h3 className="text-sm font-semibold text-foreground mb-3">Casos por nivel de triage vigente</h3>
              <LevelBars data={data.cases_by_level} />
              <div className="mt-4 grid grid-cols-4 gap-2 text-center">
                {(Object.keys(data.cases_by_status) as CaseStatus[]).map((s) => (
                  <div key={s} className="p-2 bg-secondary/40 rounded">
                    <p className="text-sm font-bold text-foreground">{data.cases_by_status[s]}</p>
                    <p className="text-[10px] text-muted-foreground">{CASE_STATUS_LABELS[s]}</p>
                  </div>
                ))}
              </div>
            </div>
            <div className={`${cardClass} p-4`}>
              <h3 className="text-sm font-semibold text-foreground mb-3">Casos creados por semana</h3>
              <WeeklyLine points={data.cases_per_week} />
            </div>
          </div>

          <div className="grid lg:grid-cols-2 gap-4">
            <div className={`${cardClass} p-4`}>
              <h3 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-1.5">
                <Clock className="w-4 h-4 text-primary" /> Triage → revisión médica (promedio)
              </h3>
              <div className="grid grid-cols-3 gap-2 text-center">
                {LEVELS.map((l) => (
                  <div key={l} className="p-2 bg-secondary/40 rounded">
                    <p className="text-sm font-bold text-foreground">
                      {data.avg_triage_to_review_hours_by_level[l] === null ? '—' : `${data.avg_triage_to_review_hours_by_level[l]!.toFixed(1)} h`}
                    </p>
                    <p className="text-[10px] text-muted-foreground">{l}</p>
                  </div>
                ))}
              </div>
            </div>
            <div className={`${cardClass} p-4`}>
              <h3 className="text-sm font-semibold text-foreground mb-3">Overrides médicos</h3>
              <p className="text-2xl font-bold text-foreground">
                {data.override_ratio === null ? '—' : `${(data.override_ratio * 100).toFixed(1)}%`}
              </p>
              <p className="text-[10px] text-muted-foreground">
                {data.triage_overrides} de {data.triage_total} cálculos de triage fueron ajustados por un médico.
                Una proporción alta sugiere revisar los parámetros.
              </p>
            </div>
          </div>

          <button className="text-xs text-primary" onClick={() => setShowTable((v) => !v)}>
            {showTable ? 'Ocultar' : 'Ver'} datos en tabla
          </button>
          {showTable && (
            <table className="w-full text-xs">
              <tbody className="divide-y divide-border">
                {data.cases_per_week.map((p) => (
                  <tr key={p.week_start}>
                    <td className="py-1 text-muted-foreground">Semana del {p.week_start}</td>
                    <td className="text-right text-foreground">{p.cases} casos</td>
                  </tr>
                ))}
                {LEVELS.map((l) => (
                  <tr key={l}>
                    <td className="py-1 text-muted-foreground">Nivel {l}</td>
                    <td className="text-right text-foreground">{data.cases_by_level[l]} casos</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      )}
    </div>
  );
}
