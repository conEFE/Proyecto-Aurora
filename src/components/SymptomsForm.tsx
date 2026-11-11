import type { CaseSymptoms } from '../types';
import { BIRADS_LABELS } from '../constants';
import { cn } from '../lib/cn';
import { inputClass, labelClass } from './ui';

interface SymptomsFormProps {
  value: CaseSymptoms;
  onChange: (value: CaseSymptoms) => void;
  disabled?: boolean;
}

const SYMPTOMS: Array<{ key: keyof Omit<CaseSymptoms, 'birads_reported'>; label: string }> = [
  { key: 'palpable_mass', label: 'Masa palpable' },
  { key: 'nipple_discharge', label: 'Secreción por el pezón' },
  { key: 'skin_or_nipple_changes', label: 'Cambios en piel o pezón' },
];

export default function SymptomsForm({ value, onChange, disabled }: SymptomsFormProps) {
  return (
    <div className="grid sm:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] gap-5">
      <fieldset disabled={disabled}>
        <legend className={labelClass}>Síntomas</legend>
        <div className="space-y-2">
          {SYMPTOMS.map(({ key, label }) => (
            <label key={key} className={cn('flex items-center gap-2.5 text-sm', disabled && 'text-muted-foreground')}>
              <input
                type="checkbox"
                checked={value[key]}
                onChange={(e) => onChange({ ...value, [key]: e.target.checked })}
              />
              {label}
            </label>
          ))}
        </div>
      </fieldset>
      <div>
        <label className={labelClass} htmlFor="birads">BI-RADS informado</label>
        <select
          id="birads"
          className={inputClass}
          disabled={disabled}
          value={value.birads_reported ?? ''}
          onChange={(e) =>
            onChange({ ...value, birads_reported: e.target.value === '' ? null : Number(e.target.value) })
          }
        >
          <option value="">Sin informe</option>
          {Object.entries(BIRADS_LABELS).map(([k, label]) => (
            <option key={k} value={k}>{label}</option>
          ))}
        </select>
      </div>
    </div>
  );
}
