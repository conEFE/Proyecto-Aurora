import { useState } from 'react';
import { Loader2, Mail } from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '../services/api';
import type { Me, Role } from '../types';
import { ROLE_LABELS } from '../types';
import { cn } from '../lib/cn';
import ChangePassword from './ChangePassword';
import { ErrorMessage } from './Feedback';
import {
  cardClass,
  formatDateTime,
  hintClass,
  inputClass,
  labelClass,
  pageClass,
  pageSubtitle,
  pageTitle,
  primaryButton,
  sectionTitle,
} from './ui';

// Resumen de la matriz de permisos, en lenguaje de usuario
const ROLE_PERMISSIONS: Record<Role, string[]> = {
  MEDICO: [
    'Registrar pacientes, crear casos y cargar imágenes',
    'Ver imágenes, resultados de IA y el detalle del triage',
    'Ajustar la prioridad (override) con motivo',
    'Registrar la revisión médica, cerrar casos y firmar reportes',
    'Editar los parámetros del triage',
  ],
  ADMINISTRATIVO: [
    'Registrar y editar pacientes con su consentimiento',
    'Crear casos y cargar imágenes',
    'Ver la cola de triage (código, nivel y estado)',
    'Gestionar consentimiento, bloqueo y solicitudes de datos',
  ],
  ADMIN: [
    'Crear, editar y desactivar usuarios',
    'Revisar la bitácora de auditoría y los errores',
    'Ver los parámetros del triage y el dashboard agregado',
    'No accede a datos de pacientes',
  ],
};

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
    ['Nombre', me.full_name],
    ['RUT', me.rut],
    ['Rol', ROLE_LABELS[me.role]],
    ['Email', me.email],
    ['Cuenta creada', formatDateTime(me.created_at)],
    ['Último inicio de sesión', formatDateTime(me.last_login_at)],
    ['Último cambio de contraseña', formatDateTime(me.password_changed_at)],
  ];

  return (
    <div className={pageClass}>
      <h1 className={pageTitle}>Mi perfil</h1>
      <p className={pageSubtitle}>Sus datos de acceso a Aurora Care. El nombre, el RUT y el rol los cambia un administrador.</p>

      <div className="mt-6 grid xl:grid-cols-2 gap-6 items-start">
        <div className="space-y-6">
          <section className={cn(cardClass, 'p-6')} aria-labelledby="pf-account">
            <h2 id="pf-account" className={sectionTitle}>Cuenta</h2>
            <dl className="mt-4 grid sm:grid-cols-[minmax(0,14rem)_minmax(0,1fr)] gap-x-4 gap-y-2 text-sm">
              {rows.map(([label, value]) => (
                <div key={label} className="contents">
                  <dt className="text-muted-foreground">{label}</dt>
                  <dd className="font-medium tabular-nums break-words">{value}</dd>
                </div>
              ))}
            </dl>
          </section>

          <section className={cn(cardClass, 'p-6')} aria-labelledby="pf-role">
            <h2 id="pf-role" className={sectionTitle}>Qué puede hacer como {ROLE_LABELS[me.role].toLowerCase()}</h2>
            <ul className="mt-3 space-y-1.5 text-sm list-disc pl-5 marker:text-brand">
              {ROLE_PERMISSIONS[me.role].map((p) => (
                <li key={p}>{p}</li>
              ))}
            </ul>
          </section>
        </div>

        <div className="space-y-6">
          <section className={cn(cardClass, 'p-6')} aria-labelledby="pf-email">
            <h2 id="pf-email" className={sectionTitle}>Email</h2>
            <form onSubmit={saveEmail} className="mt-4 space-y-4" noValidate>
              <ErrorMessage>{error}</ErrorMessage>
              <div>
                <label className={labelClass} htmlFor="pf-email-input">Email</label>
                <input id="pf-email-input" type="email" className={inputClass} value={email} autoComplete="email"
                  onChange={(e) => setEmail(e.target.value)} />
                <p className={hintClass}>Se usa para identificarle en la plataforma. No se publica.</p>
              </div>
              {changed && (
                <div>
                  <label className={labelClass} htmlFor="pf-email-password">Contraseña actual (para confirmar)</label>
                  <input id="pf-email-password" type="password" className={inputClass} value={password}
                    autoComplete="current-password" onChange={(e) => setPassword(e.target.value)} />
                </div>
              )}
              <div className="flex justify-end">
                <button type="submit" disabled={!canSave} className={primaryButton}>
                  {saving ? <Loader2 aria-hidden className="w-4 h-4 animate-spin" /> : <Mail aria-hidden className="w-4 h-4" />}
                  Guardar email
                </button>
              </div>
            </form>
          </section>

          <section className={cn(cardClass, 'p-6')} aria-labelledby="pf-password">
            <h2 id="pf-password" className={sectionTitle}>Contraseña</h2>
            <p className="mt-1 mb-4 text-sm text-muted-foreground">Al guardar, se cierran las demás sesiones abiertas.</p>
            <ChangePassword embedded />
          </section>
        </div>
      </div>
    </div>
  );
}
