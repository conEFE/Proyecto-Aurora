import { useEffect, useState } from 'react';
import { Check, Loader2 } from 'lucide-react';
import { apiClient } from '../services/api';
import { passwordHints } from '../utils/password';
import { cn } from '../lib/cn';
import PasswordInput from './PasswordInput';
import BrandMark from './BrandMark';
import { ErrorMessage, Loading } from './Feedback';
import { cardClass, labelClass, primaryButton, secondaryButton } from './ui';

interface ActivateAccountProps {
  token: string;
  /** Cuenta activada: el token de sesión ya quedó guardado. */
  onActivated: () => void;
  onGoToLogin: () => void;
}

/** Página del link de activación del email: confirma el email y define la contraseña. */
export default function ActivateAccount({ token, onActivated, onGoToLogin }: ActivateAccountProps) {
  const [info, setInfo] = useState<{ first_name: string; email: string } | null>(null);
  const [linkError, setLinkError] = useState<string | null>(null);
  const [next, setNext] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!token) {
      setLinkError('El link no tiene el código de activación. Ábralo de nuevo desde el email.');
      return;
    }
    apiClient.getActivation(token).then((r) => {
      if (r.data) setInfo(r.data);
      else setLinkError(r.error || 'El link de activación no es válido.');
    });
  }, [token]);

  const hints = passwordHints(next);
  const mismatch = confirm.length > 0 && next !== confirm;
  const canSubmit = hints.every((h) => h.ok) && next === confirm && !saving;

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;
    setSaving(true);
    setError(null);
    const r = await apiClient.activateAccount(token, next);
    setSaving(false);
    if (r.data) onActivated();
    else setError(r.error || 'No se pudo activar la cuenta.');
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4 py-10">
      <section aria-labelledby="act-title" className={cn(cardClass, 'p-8 w-full max-w-md')}>
        <BrandMark />
        <h1 id="act-title" className="mt-4 text-2xl font-extrabold">Active su cuenta</h1>
        {linkError ? (
          <>
            <ErrorMessage className="mt-4">{linkError}</ErrorMessage>
            <button type="button" className={cn(secondaryButton, 'mt-6')} onClick={onGoToLogin}>
              Ir a ingresar
            </button>
          </>
        ) : !info ? (
          <Loading className="mt-6" label="Validando el link…" />
        ) : (
          <>
            <p className="mt-2 mb-6 text-sm text-muted-foreground">
              Hola {info.first_name}. Su email <strong className="text-foreground">{info.email}</strong> quedará
              confirmado al definir su contraseña. Después ingresará con su RUT y esta contraseña.
            </p>
            <form onSubmit={submit} className="space-y-4" noValidate>
              <ErrorMessage>{error}</ErrorMessage>
              <div>
                <label className={labelClass} htmlFor="act-new">Contraseña</label>
                <PasswordInput id="act-new" value={next} required autoComplete="new-password"
                  aria-describedby="act-rules" onChange={(e) => setNext(e.target.value)} />
                <ul id="act-rules" className="mt-2 space-y-1">
                  {hints.map((h) => (
                    <li key={h.label} className={cn('flex items-center gap-2 text-sm', h.ok ? 'text-baja' : 'text-muted-foreground')}>
                      <Check aria-hidden className={cn('w-4 h-4', h.ok ? 'opacity-100' : 'opacity-30')} />
                      {h.label}
                      <span className="sr-only">{h.ok ? '(cumple)' : '(pendiente)'}</span>
                    </li>
                  ))}
                  <li className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Check aria-hidden className="w-4 h-4 opacity-30" /> Sin su RUT
                  </li>
                </ul>
              </div>
              <div>
                <label className={labelClass} htmlFor="act-confirm">Repita la contraseña</label>
                <PasswordInput id="act-confirm" value={confirm} required autoComplete="new-password"
                  aria-invalid={mismatch || undefined} aria-describedby={mismatch ? 'act-mismatch' : undefined}
                  onChange={(e) => setConfirm(e.target.value)} />
                {mismatch && <p id="act-mismatch" className="mt-1 text-sm text-destructive">Las contraseñas no coinciden.</p>}
              </div>
              <div className="flex justify-end pt-1">
                <button type="submit" disabled={!canSubmit} className={primaryButton}>
                  {saving && <Loader2 aria-hidden className="w-4 h-4 animate-spin" />}
                  Activar cuenta
                </button>
              </div>
            </form>
          </>
        )}
      </section>
    </div>
  );
}
