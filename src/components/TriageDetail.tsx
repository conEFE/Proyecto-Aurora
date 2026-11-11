import { useCallback, useEffect, useState } from 'react';
import { History, Loader2, PenLine, RefreshCw, ShieldAlert } from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '../services/api';
import type { TriageBreakdown, TriageLevel, TriageResult } from '../types';
import { cn } from '../lib/cn';
import { LevelBadge, PrototypeBadge, ScoreBar, SimulatedBadge } from './Badges';
import { ErrorMessage } from './Feedback';
import { cardClass, formatDateTime, ghostButton, inputClass, labelClass, primaryButton, secondaryButton, sectionTitle, textareaClass } from './ui';

const FACTOR_LABELS: Record<keyof Omit<TriageBreakdown, 'escalation_rule' | 'ai_is_simulated' | 'ai_is_prototype' | 'images_analyzed'>, string> = {
  ai: 'IA (máx. confianza con hallazgo)',
  age: 'Edad',
  family_history: 'Antecedente familiar 1er grado',
  previous_cancer: 'Cáncer de mama previo',
  wait_time: 'Tiempo de espera',
};

const RULE_LABELS: Record<string, string> = {
  R_BIRADS: 'BI-RADS informado en la lista de escalamiento',
  R_SINTOMA: 'Síntoma de alarma registrado',
};

function formatValue(key: string, value: number | boolean): string {
  if (typeof value === 'boolean') return value ? 'Sí' : 'No';
  if (key === 'ai') return `${value.toFixed(1).replace('.', ',')} %`;
  if (key === 'age') return `${value} años`;
  if (key === 'wait_time') return `${value.toFixed(1).replace('.', ',')} días`;
  return String(value);
}

const num = (n: number) => n.toFixed(1).replace('.', ',');

interface TriageDetailProps {
  caseId: number;
  closed: boolean;
  onChanged: () => void;
  embedded?: boolean;
}

export default function TriageDetail({ caseId, closed, onChanged, embedded = false }: TriageDetailProps) {
  const [triage, setTriage] = useState<TriageResult | null>(null);
  const [history, setHistory] = useState<TriageResult[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [overrideOpen, setOverrideOpen] = useState(false);
  const [level, setLevel] = useState<TriageLevel>('ALTA');
  const [reason, setReason] = useState('');
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    const r = await apiClient.getTriage(caseId);
    if (r.data) {
      setTriage(r.data);
      setError(null);
    } else if (r.status === 404) {
      setTriage(null);
    } else setError(r.error || 'No se pudo cargar el triage.');
  }, [caseId]);

  useEffect(() => {
    load();
  }, [load]);

  const loadHistory = async () => {
    if (showHistory) {
      setShowHistory(false);
      return;
    }
    const r = await apiClient.getTriageHistory(caseId);
    if (r.data) setHistory(r.data);
    setShowHistory(true);
  };

  const recalc = async () => {
    setBusy(true);
    const r = await apiClient.recalculateTriage(caseId);
    setBusy(false);
    if (r.data) {
      setTriage(r.data);
      toast.success('Triage recalculado');
      onChanged();
    } else setError(r.error || 'No se pudo recalcular el triage.');
  };

  const submitOverride = async () => {
    setBusy(true);
    const r = await apiClient.overrideTriage(caseId, level, reason.trim());
    setBusy(false);
    if (r.data) {
      setTriage(r.data);
      setOverrideOpen(false);
      setReason('');
      toast.success(`Nivel cambiado a ${r.data.final_level}`);
      onChanged();
    } else setError(r.error || 'No se pudo cambiar el nivel.');
  };

  if (!triage) {
    return (
      <section className={embedded ? '' : cn(cardClass, 'p-6')}>
        <h3 className={sectionTitle}>Triage</h3>
        {error ? <ErrorMessage className="mt-3">{error}</ErrorMessage> : <p className="mt-2 text-sm text-muted-foreground">El caso aún no tiene triage calculado.</p>}
      </section>
    );
  }

  const b = triage.breakdown;
  const factorKeys = Object.keys(FACTOR_LABELS) as Array<keyof typeof FACTOR_LABELS>;

  return (
    <section aria-labelledby={`triage-${caseId}`} className={cn(embedded ? '' : cn(cardClass, 'p-6'), 'space-y-5')}>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 id={`triage-${caseId}`} className={sectionTitle}>Por qué tiene este nivel</h3>
        <span className="flex flex-wrap gap-2">
          {b?.ai_is_simulated && <SimulatedBadge />}
          {b?.ai_is_prototype && <PrototypeBadge />}
        </span>
      </div>

      <dl className="grid grid-cols-3 divide-x divide-border border-y border-border">
        <div className="py-3 pr-4">
          <dt className="text-xs text-muted-foreground">Nivel final</dt>
          <dd className="mt-1"><LevelBadge level={triage.final_level} size="lg" /></dd>
        </div>
        <div className="py-3 px-4">
          <dt className="text-xs text-muted-foreground">Puntaje (0–100)</dt>
          <dd className="mt-1.5"><ScoreBar score={triage.score} level={triage.final_level} /></dd>
        </div>
        <div className="py-3 pl-4">
          <dt className="text-xs text-muted-foreground">Calculado · configuración</dt>
          <dd className="mt-1 text-sm font-semibold">
            {triage.computed_level} · v{triage.config_version}
          </dd>
        </div>
      </dl>

      {triage.escalation_rule && (
        <div className="flex items-start gap-2 px-4 py-3 rounded-lg bg-alta/10 border border-alta/30 text-sm">
          <ShieldAlert aria-hidden className="w-4 h-4 mt-0.5 shrink-0 text-alta" />
          <p>
            Escalado directo a ALTA por la regla <strong>{triage.escalation_rule}</strong>
            {RULE_LABELS[triage.escalation_rule] ? `: ${RULE_LABELS[triage.escalation_rule].toLowerCase()}` : ''}. El
            puntaje queda como referencia.
          </p>
        </div>
      )}

      {triage.override_by !== null && (
        <div className="flex items-start gap-2 px-4 py-3 rounded-lg bg-info/10 border border-info/30 text-sm">
          <PenLine aria-hidden className="w-4 h-4 mt-0.5 shrink-0 text-info" />
          <p>
            Un médico ajustó el nivel de <strong>{triage.computed_level}</strong> a <strong>{triage.final_level}</strong>.
            Motivo: {triage.override_reason}
          </p>
        </div>
      )}

      {b && (
        <table className="w-full text-sm">
          <caption className="sr-only">Aporte de cada factor al puntaje</caption>
          <thead>
            <tr className="text-xs text-muted-foreground">
              <th scope="col" className="text-left font-semibold pb-2">Factor</th>
              <th scope="col" className="text-right font-semibold pb-2">Valor</th>
              <th scope="col" className="text-left font-semibold pb-2 pl-6">Aporte / peso</th>
            </tr>
          </thead>
          <tbody>
            {factorKeys.map((key) => {
              const f = b[key];
              const pct = f.weight > 0 ? Math.min(100, (f.points / f.weight) * 100) : 0;
              return (
                <tr key={key} className="border-t border-border">
                  <th scope="row" className="py-2.5 text-left font-normal">{FACTOR_LABELS[key]}</th>
                  <td className="py-2.5 text-right text-muted-foreground tabular-nums">{formatValue(key, f.value)}</td>
                  <td className="py-2.5 pl-6">
                    <span className="inline-flex items-center gap-2.5">
                      <span aria-hidden className="relative w-28 h-1.5 rounded-full bg-muted overflow-hidden">
                        <span className="absolute inset-y-0 left-0 rounded-full bg-brand" style={{ width: `${pct}%` }} />
                      </span>
                      <span className="tabular-nums">
                        <strong>{num(f.points)}</strong>
                        <span className="text-muted-foreground"> / {f.weight}</span>
                      </span>
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}

      <p className="text-xs text-muted-foreground">
        Calculado el {formatDateTime(triage.computed_at)}. Es una propuesta técnica de priorización, no un criterio
        clínico validado.
      </p>

      <ErrorMessage>{error}</ErrorMessage>

      {!closed && (
        <div className="flex flex-wrap gap-2">
          <button className={secondaryButton} onClick={() => setOverrideOpen((v) => !v)} disabled={busy} aria-expanded={overrideOpen}>
            <PenLine aria-hidden className="w-4 h-4" /> Cambiar nivel
          </button>
          <button className={secondaryButton} onClick={recalc} disabled={busy}>
            <RefreshCw aria-hidden className="w-4 h-4" /> Recalcular
          </button>
          <button className={ghostButton} onClick={loadHistory} aria-expanded={showHistory}>
            <History aria-hidden className="w-4 h-4" /> Historial
          </button>
        </div>
      )}

      {overrideOpen && (
        <div className="p-4 rounded-lg bg-muted border border-border space-y-4">
          <div>
            <label className={labelClass} htmlFor={`ov-level-${caseId}`}>Nivel final</label>
            <select id={`ov-level-${caseId}`} className={cn(inputClass, 'w-48')} value={level} onChange={(e) => setLevel(e.target.value as TriageLevel)}>
              <option value="ALTA">ALTA</option>
              <option value="MEDIA">MEDIA</option>
              <option value="BAJA">BAJA</option>
            </select>
          </div>
          <div>
            <label className={labelClass} htmlFor={`ov-reason-${caseId}`}>Motivo del cambio</label>
            <textarea
              id={`ov-reason-${caseId}`}
              rows={2}
              className={textareaClass}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              aria-describedby={`ov-hint-${caseId}`}
            />
            <p id={`ov-hint-${caseId}`} className="mt-1 text-xs text-muted-foreground">
              Obligatorio (mínimo 5 caracteres). Queda registrado en la auditoría.
            </p>
          </div>
          <button className={primaryButton} onClick={submitOverride} disabled={busy || reason.trim().length < 5}>
            {busy && <Loader2 aria-hidden className="w-4 h-4 animate-spin" />}
            Confirmar cambio de nivel
          </button>
        </div>
      )}

      {showHistory && (
        <div>
          <h4 className="text-sm font-semibold text-muted-foreground mb-1">Historial de cálculos</h4>
          <ul>
            {history.map((h) => (
              <li key={h.id} className="flex items-center justify-between gap-4 py-2 border-b border-border last:border-0 text-sm">
                <span className="text-muted-foreground tabular-nums">
                  {formatDateTime(h.computed_at)} · v{h.config_version}
                </span>
                <span className="inline-flex items-center gap-3">
                  <span className="tabular-nums">{num(h.score)}</span>
                  <LevelBadge level={h.final_level} />
                  {h.is_current && <span className="text-xs font-bold text-brand">vigente</span>}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
