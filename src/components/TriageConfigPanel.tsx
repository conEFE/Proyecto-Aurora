import { useCallback, useEffect, useState } from 'react';
import { Loader2, SlidersHorizontal } from 'lucide-react';
import { apiClient } from '../services/api';
import type { Me, TriageConfig, TriageParams } from '../types';
import { cardClass, errorBox, formatDateTime, inputClass, labelClass, primaryButton } from './ui';

const WEIGHT_LABELS: Record<keyof TriageParams['weights'], string> = {
  ai: 'IA',
  age: 'Edad',
  family_history: 'Antecedente familiar',
  previous_cancer: 'Cáncer previo',
  wait_time: 'Tiempo de espera',
};

function NumberInput({
  id,
  value,
  onChange,
  disabled,
  step = 1,
}: {
  id: string;
  value: number;
  onChange: (v: number) => void;
  disabled: boolean;
  step?: number;
}) {
  return (
    <input
      id={id}
      type="number"
      step={step}
      className={inputClass}
      value={Number.isFinite(value) ? value : ''}
      disabled={disabled}
      onChange={(e) => onChange(e.target.value === '' ? NaN : Number(e.target.value))}
    />
  );
}

export default function TriageConfigPanel({ me }: { me: Me }) {
  const canEdit = me.role === 'MEDICO';
  const [active, setActive] = useState<TriageConfig | null>(null);
  const [history, setHistory] = useState<TriageConfig[]>([]);
  const [draft, setDraft] = useState<TriageParams | null>(null);
  const [reason, setReason] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    const [a, h] = await Promise.all([apiClient.getTriageConfig(), apiClient.getTriageConfigHistory()]);
    if (a.data) {
      setActive(a.data);
      setDraft(structuredClone(a.data.params));
    }
    if (h.data) setHistory(h.data);
    setError(a.error || h.error || null);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  if (!draft || !active) {
    return (
      <div className="flex items-center justify-center h-64">
        {error ? <div className={errorBox}>{error}</div> : <Loader2 className="w-6 h-6 animate-spin text-primary" />}
      </div>
    );
  }

  const weightSum = Object.values(draft.weights).reduce((a, b) => a + (Number.isFinite(b) ? b : 0), 0);
  const problems: string[] = [];
  if (Math.abs(weightSum - 100) > 1e-6) problems.push(`Los pesos deben sumar 100 (suman ${weightSum})`);
  if (!(draft.thresholds.alta > draft.thresholds.media)) problems.push('El umbral ALTA debe ser mayor que MEDIA');
  if (!(draft.max_wait_days > 0)) problems.push('Los días máximos de espera deben ser mayores que 0');
  if (reason.trim().length < 5) problems.push('Indique el motivo del cambio (mín. 5 caracteres)');
  const dirty = JSON.stringify(draft) !== JSON.stringify(active.params);

  const set = (fn: (d: TriageParams) => void) => {
    const next = structuredClone(draft);
    fn(next);
    setDraft(next);
  };

  const save = async () => {
    setSaving(true);
    setInfo(null);
    const r = await apiClient.createTriageConfig(draft, reason.trim());
    setSaving(false);
    if (r.data) {
      setInfo(`Versión ${r.data.config.version} activada. Se recalcularon ${r.data.recalculated_cases} casos abiertos.`);
      setReason('');
      load();
    } else setError(r.error || 'No se pudo guardar la configuración');
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 space-y-4">
      <div>
        <h2 className="text-lg font-bold text-foreground flex items-center gap-2">
          <SlidersHorizontal className="w-5 h-5 text-primary" /> Parámetros de triage
        </h2>
        <p className="mt-0.5 text-xs text-muted-foreground">
          Versión activa v{active.version}. Los valores iniciales son una propuesta técnica que el equipo médico debe
          revisar. {canEdit ? 'Cada cambio crea una versión nueva y queda auditado.' : 'Solo lectura para el rol Administrador.'}
        </p>
      </div>

      {error && <div className={errorBox}>{error}</div>}
      {info && <div className="p-2 bg-green-500/10 border border-green-500/20 text-green-300 rounded text-xs">{info}</div>}

      <div className="grid lg:grid-cols-2 gap-4">
        <div className={`${cardClass} p-4 space-y-3`}>
          <h3 className="text-sm font-semibold text-foreground">Pesos del puntaje</h3>
          <div className="grid grid-cols-2 gap-3">
            {(Object.keys(WEIGHT_LABELS) as Array<keyof TriageParams['weights']>).map((k) => (
              <div key={k}>
                <label className={labelClass} htmlFor={`w-${k}`}>{WEIGHT_LABELS[k]}</label>
                <NumberInput id={`w-${k}`} value={draft.weights[k]} disabled={!canEdit}
                  onChange={(v) => set((d) => { d.weights[k] = v; })} />
              </div>
            ))}
          </div>
          <p className={`text-xs font-semibold ${Math.abs(weightSum - 100) < 1e-6 ? 'text-green-400' : 'text-red-400'}`}>
            Suma: {weightSum} / 100
          </p>

          <h3 className="text-sm font-semibold text-foreground pt-2">Umbrales</h3>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className={labelClass} htmlFor="t-alta">ALTA si puntaje ≥</label>
              <NumberInput id="t-alta" value={draft.thresholds.alta} disabled={!canEdit} step={0.5}
                onChange={(v) => set((d) => { d.thresholds.alta = v; })} />
            </div>
            <div>
              <label className={labelClass} htmlFor="t-media">MEDIA si puntaje ≥</label>
              <NumberInput id="t-media" value={draft.thresholds.media} disabled={!canEdit} step={0.5}
                onChange={(v) => set((d) => { d.thresholds.media = v; })} />
            </div>
            <div>
              <label className={labelClass} htmlFor="t-wait">Días máx. de espera</label>
              <NumberInput id="t-wait" value={draft.max_wait_days} disabled={!canEdit}
                onChange={(v) => set((d) => { d.max_wait_days = v; })} />
            </div>
          </div>
        </div>

        <div className={`${cardClass} p-4 space-y-3`}>
          <h3 className="text-sm font-semibold text-foreground">Reglas de escalamiento directo a ALTA</h3>
          <div>
            <p className={labelClass}>BI-RADS informado que escala</p>
            <div className="flex flex-wrap gap-2">
              {[0, 1, 2, 3, 4, 5, 6].map((b) => (
                <label key={b} className="flex items-center gap-1 text-xs text-foreground">
                  <input
                    type="checkbox"
                    disabled={!canEdit}
                    checked={draft.escalation.birads_alta.includes(b)}
                    onChange={(e) =>
                      set((d) => {
                        d.escalation.birads_alta = e.target.checked
                          ? [...d.escalation.birads_alta, b].sort()
                          : d.escalation.birads_alta.filter((x) => x !== b);
                      })
                    }
                  />
                  {b}
                </label>
              ))}
            </div>
          </div>
          <label className="flex items-center gap-2 text-xs text-foreground">
            <input type="checkbox" disabled={!canEdit} checked={draft.escalation.symptoms_alta}
              onChange={(e) => set((d) => { d.escalation.symptoms_alta = e.target.checked; })} />
            Escalar si hay masa palpable, secreción o cambios en piel/pezón
          </label>

          <h3 className="text-sm font-semibold text-foreground pt-2">Bandas de edad</h3>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className={labelClass} htmlFor="age-hi-lo">Banda alta (factor 1): desde</label>
              <NumberInput id="age-hi-lo" value={draft.age_bands.high[0]} disabled={!canEdit}
                onChange={(v) => set((d) => { d.age_bands.high[0] = v; })} />
            </div>
            <div>
              <label className={labelClass} htmlFor="age-hi-hi">hasta</label>
              <NumberInput id="age-hi-hi" value={draft.age_bands.high[1]} disabled={!canEdit}
                onChange={(v) => set((d) => { d.age_bands.high[1] = v; })} />
            </div>
          </div>
          <p className="text-[10px] text-muted-foreground">
            Bandas medias (factor 0,5): {draft.age_bands.medium.map(([a, b]) => `${a}–${b}`).join(', ')} años.
          </p>
        </div>
      </div>

      {canEdit && (
        <div className={`${cardClass} p-4 space-y-2`}>
          <label className={labelClass} htmlFor="cfg-reason">Motivo del cambio</label>
          <textarea id="cfg-reason" rows={2} className={inputClass} value={reason} onChange={(e) => setReason(e.target.value)} />
          {dirty && problems.length > 0 && (
            <ul className="text-[10px] text-red-400 list-disc pl-4">
              {problems.map((p) => <li key={p}>{p}</li>)}
            </ul>
          )}
          <button className={primaryButton} disabled={!dirty || problems.length > 0 || saving} onClick={save}>
            {saving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Guardar como nueva versión'}
          </button>
        </div>
      )}

      <div className={`${cardClass} p-4`}>
        <h3 className="text-sm font-semibold text-foreground mb-2">Historial de versiones</h3>
        <div className="space-y-1">
          {history.map((c) => (
            <div key={c.id} className="flex items-start justify-between text-[10px] border-b border-border py-1">
              <span className="text-foreground font-semibold">
                v{c.version} {c.is_active && <span className="text-primary">(activa)</span>}
              </span>
              <span className="text-muted-foreground flex-1 mx-3">{c.change_reason}</span>
              <span className="text-muted-foreground">{formatDateTime(c.created_at)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
