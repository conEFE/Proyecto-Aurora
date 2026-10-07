import { useCallback, useEffect, useState } from 'react';
import { Gauge, History, Loader2, RefreshCw, ShieldAlert } from 'lucide-react';
import { apiClient } from '../services/api';
import type { TriageBreakdown, TriageLevel, TriageResult } from '../types';
import { LevelBadge, SimulatedBadge } from './Badges';
import { cardClass, errorBox, formatDateTime, inputClass, labelClass, primaryButton, secondaryButton } from './ui';

const FACTOR_LABELS: Record<keyof Omit<TriageBreakdown, 'escalation_rule' | 'ai_is_simulated' | 'images_analyzed'>, string> = {
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
  if (key === 'ai') return `${value.toFixed(1)}%`;
  if (key === 'age') return `${value} años`;
  if (key === 'wait_time') return `${value.toFixed(1)} días`;
  return String(value);
}

interface TriageDetailProps {
  caseId: number;
  closed: boolean;
  onChanged: () => void;
}

export default function TriageDetail({ caseId, closed, onChanged }: TriageDetailProps) {
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
    } else setError(r.error || 'Error al cargar el triage');
  }, [caseId]);

  useEffect(() => {
    load();
  }, [load]);

  const loadHistory = async () => {
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
      onChanged();
    } else setError(r.error || 'No se pudo recalcular');
  };

  const submitOverride = async () => {
    setBusy(true);
    const r = await apiClient.overrideTriage(caseId, level, reason.trim());
    setBusy(false);
    if (r.data) {
      setTriage(r.data);
      setOverrideOpen(false);
      setReason('');
      onChanged();
    } else setError(r.error || 'No se pudo cambiar el nivel');
  };

  if (!triage) {
    return (
      <div className={`${cardClass} p-4 text-xs text-muted-foreground`}>
        {error ? <div className={errorBox}>{error}</div> : 'El caso aún no tiene triage calculado.'}
      </div>
    );
  }

  const b = triage.breakdown;
  const factorKeys = Object.keys(FACTOR_LABELS) as Array<keyof typeof FACTOR_LABELS>;

  return (
    <div className={`${cardClass} p-4 space-y-3`}>
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-semibold text-foreground flex items-center gap-1.5">
          <Gauge className="w-3.5 h-3.5 text-primary" /> Triage
        </h4>
        <div className="flex items-center gap-2">
          {b?.ai_is_simulated && <SimulatedBadge />}
          <LevelBadge level={triage.final_level} />
        </div>
      </div>

      {error && <div className={errorBox}>{error}</div>}

      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="p-2 bg-secondary/40 rounded">
          <p className="text-lg font-bold text-foreground">{triage.score.toFixed(2)}</p>
          <p className="text-[10px] text-muted-foreground">Puntaje (0–100)</p>
        </div>
        <div className="p-2 bg-secondary/40 rounded">
          <p className="text-sm font-bold text-foreground mt-1">{triage.computed_level}</p>
          <p className="text-[10px] text-muted-foreground">Nivel calculado</p>
        </div>
        <div className="p-2 bg-secondary/40 rounded">
          <p className="text-sm font-bold text-foreground mt-1">v{triage.config_version}</p>
          <p className="text-[10px] text-muted-foreground">Configuración</p>
        </div>
      </div>

      {triage.escalation_rule && (
        <div className="p-2 bg-red-500/10 border border-red-500/20 rounded text-[10px] text-red-300 flex items-start gap-1.5">
          <ShieldAlert className="w-3.5 h-3.5 flex-shrink-0" />
          <span>
            Escalamiento directo a ALTA por la regla <strong>{triage.escalation_rule}</strong>:{' '}
            {RULE_LABELS[triage.escalation_rule] ?? ''}. El puntaje se muestra como referencia.
          </span>
        </div>
      )}

      {triage.override_by !== null && (
        <div className="p-2 bg-blue-500/10 border border-blue-500/20 rounded text-[10px] text-blue-200">
          Nivel ajustado por médico de <strong>{triage.computed_level}</strong> a{' '}
          <strong>{triage.final_level}</strong>. Motivo: {triage.override_reason}
        </div>
      )}

      {b && (
        <table className="w-full text-[10px]">
          <thead>
            <tr className="text-muted-foreground">
              <th className="text-left font-semibold py-1">Factor</th>
              <th className="text-right font-semibold">Valor</th>
              <th className="text-right font-semibold">Peso</th>
              <th className="text-right font-semibold">Aporte</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {factorKeys.map((key) => (
              <tr key={key}>
                <td className="py-1 text-foreground">{FACTOR_LABELS[key]}</td>
                <td className="text-right text-muted-foreground">{formatValue(key, b[key].value)}</td>
                <td className="text-right text-muted-foreground">{b[key].weight}</td>
                <td className="text-right font-semibold text-foreground">{b[key].points.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <p className="text-[10px] text-muted-foreground">
        Calculado el {formatDateTime(triage.computed_at)} · Propuesta técnica de priorización, no un criterio clínico
        validado.
      </p>

      {!closed && (
        <div className="flex flex-wrap gap-2">
          <button className={secondaryButton} onClick={recalc} disabled={busy}>
            <RefreshCw className="w-3.5 h-3.5" /> Recalcular
          </button>
          <button className={secondaryButton} onClick={() => setOverrideOpen((v) => !v)} disabled={busy}>
            Cambiar nivel
          </button>
          <button className={secondaryButton} onClick={loadHistory}>
            <History className="w-3.5 h-3.5" /> Historial
          </button>
        </div>
      )}

      {overrideOpen && (
        <div className="p-3 border border-border rounded space-y-2">
          <div>
            <label className={labelClass} htmlFor="ov-level">Nivel final</label>
            <select id="ov-level" className={inputClass} value={level} onChange={(e) => setLevel(e.target.value as TriageLevel)}>
              <option value="ALTA">ALTA</option>
              <option value="MEDIA">MEDIA</option>
              <option value="BAJA">BAJA</option>
            </select>
          </div>
          <div>
            <label className={labelClass} htmlFor="ov-reason">Motivo (obligatorio)</label>
            <textarea id="ov-reason" rows={2} className={inputClass} value={reason} onChange={(e) => setReason(e.target.value)} />
          </div>
          <button className={primaryButton} onClick={submitOverride} disabled={busy || reason.trim().length < 5}>
            {busy ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Confirmar cambio de nivel'}
          </button>
          <p className="text-[10px] text-muted-foreground">El cambio queda registrado en la auditoría.</p>
        </div>
      )}

      {showHistory && (
        <div className="space-y-1">
          <p className="text-[10px] font-semibold text-muted-foreground uppercase">Historial</p>
          {history.map((h) => (
            <div key={h.id} className="flex items-center justify-between text-[10px] text-muted-foreground">
              <span>{formatDateTime(h.computed_at)} · v{h.config_version}</span>
              <span>
                {h.score.toFixed(2)} · <LevelBadge level={h.final_level} />
                {h.is_current && <span className="ml-1 text-primary">vigente</span>}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
