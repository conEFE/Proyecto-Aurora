import { useCallback, useEffect, useState } from 'react';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '../services/api';
import type { Me, TriageConfig, TriageParams } from '../types';
import { cn } from '../lib/cn';
import { ErrorMessage, Loading } from './Feedback';
import { DetailHeader } from './PageHeader';
import { cardClass, formatDateTime, inputClass, labelClass, pageClass, primaryButton, sectionTitle, textareaClass } from './ui';

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
  className,
}: {
  id: string;
  value: number;
  onChange: (v: number) => void;
  disabled: boolean;
  step?: number;
  className?: string;
}) {
  return (
    <input
      id={id}
      type="number"
      step={step}
      className={cn(inputClass, 'tabular-nums', className)}
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
    return <div className={pageClass}>{error ? <ErrorMessage>{error}</ErrorMessage> : <Loading label="Cargando parámetros…" />}</div>;
  }

  const weightKeys = Object.keys(WEIGHT_LABELS) as Array<keyof TriageParams['weights']>;
  const weightSum = Object.values(draft.weights).reduce((a, b) => a + (Number.isFinite(b) ? b : 0), 0);
  const sumOk = Math.abs(weightSum - 100) < 1e-6;
  const problems: string[] = [];
  if (!sumOk) problems.push(`Los pesos deben sumar 100 (hoy suman ${weightSum}).`);
  if (!(draft.thresholds.alta > draft.thresholds.media)) problems.push('El umbral ALTA debe ser mayor que el de MEDIA.');
  if (!(draft.max_wait_days > 0)) problems.push('Los días máximos de espera deben ser mayores que 0.');
  if (reason.trim().length < 5) problems.push('Indique el motivo del cambio (mínimo 5 caracteres).');
  const dirty = JSON.stringify(draft) !== JSON.stringify(active.params);

  const set = (fn: (d: TriageParams) => void) => {
    const next = structuredClone(draft);
    fn(next);
    setDraft(next);
  };

  const save = async () => {
    setSaving(true);
    const r = await apiClient.createTriageConfig(draft, reason.trim());
    setSaving(false);
    if (r.data) {
      toast.success(`Versión ${r.data.config.version} activada. Se recalcularon ${r.data.recalculated_cases} casos abiertos.`);
      setReason('');
      load();
    } else setError(r.error || 'No se pudo guardar la configuración.');
  };

  const activeSince = history.find((c) => c.is_active)?.created_at ?? active.created_at;

  return (
    <div className={pageClass}>
      <DetailHeader
        title="Parámetros de triage"
        status={<span className="text-sm font-semibold text-brand tabular-nums">Versión {active.version} activa</span>}
        meta={<>Desde el {formatDateTime(activeSince)}{canEdit ? ' · cada cambio crea una versión nueva' : ' · solo lectura'}</>}
      />

      <ErrorMessage className="mt-4">{error}</ErrorMessage>

      <div className="mt-6 grid xl:grid-cols-[minmax(0,7fr)_minmax(0,5fr)] gap-6 items-start">
      <div className="space-y-6 min-w-0">
        <section aria-labelledby="weights-title" className={cn(cardClass, 'p-6 space-y-5')}>
          <div>
            <h2 id="weights-title" className={sectionTitle}>Pesos del puntaje</h2>
            <div aria-hidden className="mt-3 h-2.5 rounded-full overflow-hidden bg-muted">
              <span className={cn('block h-full rounded-full', sumOk ? 'bg-baja' : 'bg-destructive')} style={{ width: `${Math.min(100, Math.max(0, weightSum))}%` }} />
            </div>
            <p role="status" className={cn('mt-2 text-sm font-semibold tabular-nums', sumOk ? 'text-baja' : 'text-destructive')}>
              Suma: {weightSum} de 100
            </p>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 items-end">
            {weightKeys.map((k) => (
              <div key={k}>
                <label className={labelClass} htmlFor={`w-${k}`}>
                  {WEIGHT_LABELS[k]}
                </label>
                <NumberInput id={`w-${k}`} value={draft.weights[k]} disabled={!canEdit}
                  onChange={(v) => set((d) => { d.weights[k] = v; })} />
                <span aria-hidden className="mt-2 block h-1.5 rounded-full bg-muted overflow-hidden">
                  <span className="block h-full rounded-full bg-brand" style={{ width: `${Math.min(100, Math.max(0, Number.isFinite(draft.weights[k]) ? draft.weights[k] : 0))}%` }} />
                </span>
              </div>
            ))}
          </div>

          <div className="pt-5 border-t border-border">
            <h3 className="text-sm font-bold mb-3">Umbrales</h3>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className={labelClass} htmlFor="t-alta">ALTA desde</label>
                <NumberInput id="t-alta" value={draft.thresholds.alta} disabled={!canEdit} step={0.5}
                  onChange={(v) => set((d) => { d.thresholds.alta = v; })} />
              </div>
              <div>
                <label className={labelClass} htmlFor="t-media">MEDIA desde</label>
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
        </section>

        <section aria-labelledby="rules-title" className={cn(cardClass, 'p-6 space-y-5')}>
          <h2 id="rules-title" className={sectionTitle}>Escalamiento directo a ALTA</h2>
          <fieldset>
            <legend className={labelClass}>BI-RADS informado que escala</legend>
            <div className="flex flex-wrap gap-2">
              {[0, 1, 2, 3, 4, 5, 6].map((b) => {
                const on = draft.escalation.birads_alta.includes(b);
                return (
                  <label
                    key={b}
                    className={cn(
                      'inline-flex items-center justify-center w-11 h-10 rounded-lg border text-sm font-bold cursor-pointer transition-colors has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-ring',
                      on ? 'border-alta bg-alta/10 text-alta' : 'border-input text-muted-foreground hover:bg-accent',
                      !canEdit && 'cursor-not-allowed opacity-70',
                    )}
                  >
                    <input
                      type="checkbox"
                      className="sr-only"
                      disabled={!canEdit}
                      checked={on}
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
                );
              })}
            </div>
          </fieldset>
          <label className="flex items-start gap-2 text-sm">
            <input type="checkbox" className="mt-0.5" disabled={!canEdit} checked={draft.escalation.symptoms_alta}
              onChange={(e) => set((d) => { d.escalation.symptoms_alta = e.target.checked; })} />
            Escalar si hay masa palpable, secreción o cambios en piel o pezón
          </label>

          <div className="pt-5 border-t border-border">
            <h3 className="text-sm font-bold mb-3">Bandas de edad</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={labelClass} htmlFor="age-hi-lo">Banda alta desde (años)</label>
                <NumberInput id="age-hi-lo" value={draft.age_bands.high[0]} disabled={!canEdit}
                  onChange={(v) => set((d) => { d.age_bands.high[0] = v; })} />
              </div>
              <div>
                <label className={labelClass} htmlFor="age-hi-hi">hasta (años)</label>
                <NumberInput id="age-hi-hi" value={draft.age_bands.high[1]} disabled={!canEdit}
                  onChange={(v) => set((d) => { d.age_bands.high[1] = v; })} />
              </div>
            </div>
            <p className="mt-2 text-sm text-muted-foreground">
              Medio factor: {draft.age_bands.medium.map(([a, b]) => `${a}–${b}`).join(', ')} años.
            </p>
          </div>
        </section>

      {canEdit && (
        <section aria-labelledby="save-title" className={cn(cardClass, 'p-6 space-y-3')}>
          <h2 id="save-title" className="sr-only">Guardar cambios</h2>
          <label className={labelClass} htmlFor="cfg-reason">Motivo del cambio</label>
          <textarea id="cfg-reason" rows={2} className={textareaClass} value={reason} onChange={(e) => setReason(e.target.value)} />
          {dirty && problems.length > 0 && (
            <ul className="text-sm text-destructive list-disc pl-5 space-y-0.5">
              {problems.map((p) => <li key={p}>{p}</li>)}
            </ul>
          )}
          <button className={primaryButton} disabled={!dirty || problems.length > 0 || saving} onClick={save}>
            {saving && <Loader2 aria-hidden className="w-4 h-4 animate-spin" />}
            Guardar como nueva versión
          </button>
        </section>
      )}

      </div>

      <section aria-labelledby="hist-title" className={cn(cardClass, 'p-6')}>
        <h2 id="hist-title" className={sectionTitle}>Versiones</h2>
        <ol className="mt-4 relative border-l border-border ml-3">
          {history.map((c) => (
            <li key={c.id} className="relative pl-6 pb-5 last:pb-0">
              <span
                aria-hidden
                className={cn(
                  'absolute -left-[5px] top-2 w-2.5 h-2.5 rounded-full ring-2 ring-card',
                  c.is_active ? 'bg-brand' : 'bg-border',
                )}
              />
              <p className="text-sm font-bold leading-6 tabular-nums">
                Versión {c.version}
                {c.is_active && <span className="ml-2 text-xs font-bold text-brand">activa</span>}
              </p>
              <p className="text-sm text-foreground/90">{c.change_reason}</p>
              <p className="text-xs text-muted-foreground tabular-nums">{formatDateTime(c.created_at)}</p>
            </li>
          ))}
        </ol>
      </section>
      </div>
    </div>
  );
}
