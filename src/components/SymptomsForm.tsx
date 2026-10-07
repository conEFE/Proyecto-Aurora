import type { CaseSymptoms } from '../types';
import { BIRADS_LABELS } from '../constants';
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
    <div className="space-y-2">
      <fieldset className="space-y-1.5" disabled={disabled}>
        <legend className={labelClass}>Síntomas</legend>
        {SYMPTOMS.map(({ key, label }) => (
          <label key={key} className="flex items-center gap-2 text-xs text-foreground">
            <input
              type="checkbox"
              checked={value[key]}
              onChange={(e) => onChange({ ...value, [key]: e.target.checked })}
            />
            {label}
          </label>
        ))}
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
