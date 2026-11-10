import { useState } from 'react';
import { KeyRound, Loader2, X } from 'lucide-react';
import { apiClient } from '../services/api';
import { passwordHints } from '../utils/password';
import { cardClass, errorBox, inputClass, labelClass, primaryButton, secondaryButton } from './ui';

interface ChangePasswordProps {
  /** Cambio obligatorio (primer ingreso o contraseña restablecida): no se puede cerrar. */
  forced?: boolean;
  onDone?: () => void;
  onCancel?: () => void;
}

export default function ChangePassword({ forced = false, onDone = () => {}, onCancel }: ChangePasswordProps) {
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
      setError(r.error || 'No se pudo cambiar la contraseña');
    }
  };

  return (
    <div className={`${cardClass} p-5 w-full max-w-md`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <KeyRound className="w-4 h-4 text-primary" />
          <h2 className="text-sm font-semibold text-foreground">Cambiar contraseña</h2>
        </div>
        {!forced && onCancel && (
          <button type="button" onClick={onCancel} aria-label="Cerrar" className="text-muted-foreground">
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
      {forced && (
        <p className="mb-3 text-xs text-muted-foreground">
          Su contraseña fue asignada por el administrador. Por seguridad, debe definir una nueva antes de
          continuar.
        </p>
      )}
      <form onSubmit={submit} className="space-y-3">
        {error && <div className={errorBox}>{error}</div>}
        {done && !forced && (
          <div className="p-2 bg-green-500/10 border border-green-500/20 text-green-400 rounded text-xs">
            Contraseña actualizada. Las demás sesiones abiertas se cerraron.
          </div>
        )}
        <div>
          <label className={labelClass} htmlFor="cp-current">Contraseña actual</label>
          <input id="cp-current" type="password" className={inputClass} value={current} required
            autoComplete="current-password" onChange={(e) => setCurrent(e.target.value)} />
        </div>
        <div>
          <label className={labelClass} htmlFor="cp-new">Nueva contraseña</label>
          <input id="cp-new" type="password" className={inputClass} value={next} required
            autoComplete="new-password" onChange={(e) => setNext(e.target.value)} />
          <ul className="mt-1 space-y-0.5">
            {hints.map((h) => (
              <li key={h.label} className={`text-[10px] ${h.ok ? 'text-green-400' : 'text-muted-foreground'}`}>
                {h.ok ? '✓' : '•'} {h.label}
              </li>
            ))}
            <li className="text-[10px] text-muted-foreground">• Distinta de la actual y sin su RUT</li>
          </ul>
        </div>
        <div>
          <label className={labelClass} htmlFor="cp-confirm">Repita la nueva contraseña</label>
          <input id="cp-confirm" type="password" className={inputClass} value={confirm} required
            autoComplete="new-password" onChange={(e) => setConfirm(e.target.value)} />
          {mismatch && <p className="mt-1 text-[10px] text-red-400">Las contraseñas no coinciden</p>}
        </div>
        <div className="flex gap-2">
          <button type="submit" disabled={!canSubmit} className={primaryButton}>
            {saving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Guardar contraseña'}
          </button>
          {forced ? (
            <button
              type="button"
              className={secondaryButton}
              onClick={() => {
                apiClient.setToken(null);
                window.location.reload();
              }}
            >
              Salir
            </button>
          ) : (
            onCancel && (
              <button type="button" className={secondaryButton} onClick={onCancel}>
                Cancelar
              </button>
            )
          )}
        </div>
      </form>
    </div>
  );
}
