import { useState } from 'react';
import { Loader2, Mail } from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '../services/api';
import type { Me } from '../types';
import { ROLE_LABELS } from '../types';
import { cn } from '../lib/cn';
import ChangePassword from './ChangePassword';
import { ErrorMessage } from './Feedback';
import { DetailHeader } from './PageHeader';
import { cardClass, formatDateTime, inputClass, labelClass, pageClass, primaryButton, sectionTitle } from './ui';

interface ProfileProps {
  me: Me;
  onUpdated: (me: Me) => void;
}

/** Mi perfil: datos de la cuenta, corrección del email propio y cambio de contraseña. */
export default function Profile({ me, onUpdated }: ProfileProps) {
  const [email, setEmail] = useState(me.email);
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const changed = email.trim() !== me.email;
  const canSave = changed && email.includes('@') && password.length > 0 && !saving;

  const saveEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSave) return;
    setSaving(true);
    setError(null);
    const r = await apiClient.changeEmail(email.trim(), password);
    setSaving(false);
    if (r.data) {
      setPassword('');
      onUpdated(r.data);
      toast.success('Email actualizado.');
    } else setError(r.error || 'No se pudo actualizar el email.');
  };

  const rows: [string, string][] = [
    ['Cuenta creada', formatDateTime(me.created_at)],
    ['Último ingreso', formatDateTime(me.last_login_at)],
    ['Contraseña cambiada', formatDateTime(me.password_changed_at)],
  ];

  return (
    <div className={pageClass}>
      <DetailHeader
        title={me.full_name}
        status={<span className="text-sm font-semibold text-brand">{ROLE_LABELS[me.role]}</span>}
        meta={<>RUT {me.rut} · {me.email}</>}
      />

      <div className="mt-6 grid xl:grid-cols-[minmax(0,7fr)_minmax(0,5fr)] gap-6 items-start">
        <div className="space-y-6 min-w-0">
          <section className={cn(cardClass, 'p-6')} aria-labelledby="pf-email">
            <h2 id="pf-email" className={sectionTitle}>Email</h2>
            <form onSubmit={saveEmail} className="mt-4 space-y-4" noValidate>
              <ErrorMessage>{error}</ErrorMessage>
              <div>
                <label className={labelClass} htmlFor="pf-email-input">Email</label>
                <input id="pf-email-input" type="email" className={inputClass} value={email} autoComplete="email"
                  onChange={(e) => setEmail(e.target.value)} />
              </div>
              {changed && (
                <div>
                  <label className={labelClass} htmlFor="pf-email-password">Contraseña actual (para confirmar)</label>
                  <input id="pf-email-password" type="password" className={inputClass} value={password}
                    autoComplete="current-password" onChange={(e) => setPassword(e.target.value)} />
                </div>
              )}
              <button type="submit" disabled={!canSave} className={primaryButton}>
                {saving ? <Loader2 aria-hidden className="w-4 h-4 animate-spin" /> : <Mail aria-hidden className="w-4 h-4" />}
                Guardar email
              </button>
            </form>
          </section>

          <section className={cn(cardClass, 'p-6')} aria-labelledby="pf-password">
            <h2 id="pf-password" className={sectionTitle}>Contraseña</h2>
            <p className="mt-1 mb-4 text-sm text-muted-foreground">Al guardar, se cierran las demás sesiones abiertas.</p>
            <ChangePassword embedded />
          </section>
        </div>

        <section className={cn(cardClass, 'p-6')} aria-labelledby="pf-account">
          <h2 id="pf-account" className={sectionTitle}>Cuenta</h2>
          <dl className="mt-4 divide-y divide-border text-sm">
            {rows.map(([label, value]) => (
              <div key={label} className="flex items-baseline justify-between gap-4 py-2.5 first:pt-0">
                <dt className="text-muted-foreground">{label}</dt>
                <dd className="font-medium tabular-nums text-right">{value}</dd>
              </div>
            ))}
          </dl>
          <p className="mt-4 pt-4 border-t border-border text-sm text-muted-foreground">
            El nombre, el RUT y el rol los cambia un administrador.
          </p>
        </section>
      </div>
    </div>
  );
}
