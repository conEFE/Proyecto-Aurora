import { useState } from 'react';
import { Check, Loader2 } from 'lucide-react';
import { apiClient } from '../services/api';
import { passwordHints } from '../utils/password';
import { cn } from '../lib/cn';
import BrandMark from './BrandMark';
import { ErrorMessage, SuccessMessage } from './Feedback';
import { cardClass, inputClass, labelClass, primaryButton, secondaryButton } from './ui';

interface ChangePasswordProps {
  /** Cambio obligatorio (primer ingreso o contraseña restablecida): no se puede cerrar. */
  forced?: boolean;
  /** Dentro de un diálogo: sin tarjeta ni título propios. */
  embedded?: boolean;
  onDone?: () => void;
  onCancel?: () => void;
}

export default function ChangePassword({ forced = false, embedded = false, onDone = () => {}, onCancel }: ChangePasswordProps) {
  const [current, setCurrent] = useState('');
  const [next, setNext] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [done, setDone] = useState(false);

  const hints = passwordHints(next);
  const mismatch = confirm.length > 0 && next !== confirm;
  const canSubmit = current.length > 0 && hints.every((h) => h.ok) && next === confirm && !saving;

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;
    setSaving(true);
    setError(null);
    const r = await apiClient.changePassword(current, next);
    setSaving(false);
    if (r.data) {
      setDone(true);
      setCurrent('');
      setNext('');
      setConfirm('');
      // En el cambio obligatorio se continúa de inmediato; en el voluntario se muestra la confirmación
      if (forced) onDone();
    } else {
      setError(r.error || 'No se pudo cambiar la contraseña. Revise la contraseña actual.');
    }
  };

  const form = (
    <form onSubmit={submit} className="space-y-4" noValidate>
      <ErrorMessage>{error}</ErrorMessage>
      {done && !forced && <SuccessMessage>Contraseña actualizada. Las demás sesiones abiertas se cerraron.</SuccessMessage>}
      <div>
        <label className={labelClass} htmlFor="cp-current">Contraseña actual</label>
        <input id="cp-current" type="password" className={inputClass} value={current} required
          autoComplete="current-password" onChange={(e) => setCurrent(e.target.value)} />
      </div>
      <div>
        <label className={labelClass} htmlFor="cp-new">Nueva contraseña</label>
        <input id="cp-new" type="password" className={inputClass} value={next} required
          autoComplete="new-password" aria-describedby="cp-rules" onChange={(e) => setNext(e.target.value)} />
        <ul id="cp-rules" className="mt-2 space-y-1">
          {hints.map((h) => (
            <li key={h.label} className={cn('flex items-center gap-2 text-sm', h.ok ? 'text-baja' : 'text-muted-foreground')}>
              <Check aria-hidden className={cn('w-4 h-4', h.ok ? 'opacity-100' : 'opacity-30')} />
              {h.label}
              <span className="sr-only">{h.ok ? '(cumple)' : '(pendiente)'}</span>
            </li>
          ))}
          <li className="flex items-center gap-2 text-sm text-muted-foreground">
            <Check aria-hidden className="w-4 h-4 opacity-30" /> Distinta de la actual y sin su RUT
          </li>
        </ul>
      </div>
      <div>
        <label className={labelClass} htmlFor="cp-confirm">Repita la nueva contraseña</label>
        <input id="cp-confirm" type="password" className={inputClass} value={confirm} required
          autoComplete="new-password" aria-invalid={mismatch || undefined}
          aria-describedby={mismatch ? 'cp-mismatch' : undefined}
          onChange={(e) => setConfirm(e.target.value)} />
        {mismatch && <p id="cp-mismatch" className="mt-1 text-sm text-destructive">Las contraseñas no coinciden.</p>}
      </div>
      <div className="flex flex-wrap justify-end gap-2 pt-1">
        {forced ? (
          <button
            type="button"
            className={secondaryButton}
            onClick={() => {
              apiClient.setToken(null);
              window.location.assign('/');
            }}
          >
            Salir
          </button>
        ) : (
          onCancel && (
            <button type="button" className={secondaryButton} onClick={onCancel}>
              {done ? 'Cerrar' : 'Cancelar'}
            </button>
          )
        )}
        <button type="submit" disabled={!canSubmit} className={primaryButton}>
          {saving && <Loader2 aria-hidden className="w-4 h-4 animate-spin" />}
          Guardar contraseña
        </button>
      </div>
    </form>
  );

  if (embedded) return form;

  return (
    <section aria-labelledby="cp-title" className={cn(cardClass, 'p-8 w-full max-w-md')}>
      <BrandMark />
      <h1 id="cp-title" className="mt-4 text-2xl font-extrabold">Cambie su contraseña</h1>
      {forced && (
        <p className="mt-2 mb-6 text-sm text-muted-foreground">
          Su contraseña fue asignada por el administrador. Por seguridad, defina una nueva antes de continuar.
        </p>
      )}
      {form}
    </section>
  );
}
