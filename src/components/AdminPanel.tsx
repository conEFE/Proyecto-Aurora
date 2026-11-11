import { Fragment, useCallback, useEffect, useState } from 'react';
import { ChevronLeft, ChevronRight, KeyRound, Loader2, ScrollText, ServerCrash, Unlock, UserPlus, Users } from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '../services/api';
import type {
  AdminStats,
  AuditEntry,
  DataRequestSummary,
  ErrorLogEntry,
  ErrorTypeCount,
  Page,
  Role,
  UserAccount,
  UserCreateInput,
} from '../types';
import { ROLE_LABELS } from '../types';
import { isValidRut, normalizeRut } from '../utils/rut';
import { PASSWORD_MIN_LENGTH, passwordHints } from '../utils/password';
import { cn } from '../lib/cn';
import Dialog from './Dialog';
import { ErrorMessage, Loading } from './Feedback';
import {
  cardClass,
  dangerButton,
  formatDateTime,
  ghostButton,
  inputClass,
  labelClass,
  pageClass,
  pageSubtitle,
  pageTitle,
  primaryButton,
  secondaryButton,
  sectionTitle,
  tdClass,
  thClass,
} from './ui';

const ROLES: Role[] = ['MEDICO', 'ADMINISTRATIVO', 'ADMIN'];
const ACTIONS = [
  'LOGIN_OK',
  'LOGIN_FAIL',
  'VIEW',
  'CREATE',
  'UPDATE',
  'DELETE',
  'DOWNLOAD',
  'OVERRIDE',
  'CONFIG_CHANGE',
  'SIGN',
  'SIGN_FAIL',
  'EXPORT',
  'PASSWORD_CHANGE',
  'PASSWORD_CHANGE_FAIL',
  'CONSENT_GRANT',
  'CONSENT_WITHDRAW',
  'BLOCK',
  'UNBLOCK',
];
const isLocked = (u: UserAccount) => !!u.locked_until && new Date(u.locked_until).getTime() > Date.now();

const EMPTY_USER: UserCreateInput = { rut: '', email: '', full_name: '', password: '', role: 'MEDICO' };

function UserForm({ onCreated, onCancel }: { onCreated: () => void; onCancel: () => void }) {
  const [form, setForm] = useState<UserCreateInput>(EMPTY_USER);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const rutError = form.rut && !isValidRut(form.rut) ? 'RUT inválido: revise el dígito verificador.' : null;

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (rutError) return;
    setSaving(true);
    setError(null);
    const r = await apiClient.createUser({ ...form, rut: normalizeRut(form.rut) });
    setSaving(false);
    if (r.data) {
      toast.success(`Usuario ${form.full_name} creado`);
      setForm(EMPTY_USER);
      onCreated();
    } else {
      setError(r.error || 'No se pudo crear el usuario. Revise los datos.');
    }
  };

  return (
    <form onSubmit={submit} className="space-y-4">
      <ErrorMessage>{error}</ErrorMessage>
      <div className="grid sm:grid-cols-2 gap-4">
        <div>
          <label className={labelClass} htmlFor="u-rut">RUT</label>
          <input id="u-rut" className={inputClass} value={form.rut} required
            aria-invalid={rutError ? true : undefined} aria-describedby={rutError ? 'u-rut-error' : undefined}
            onChange={(e) => setForm({ ...form, rut: e.target.value })} placeholder="12345678-5" />
          {rutError && <p id="u-rut-error" className="mt-1 text-sm text-destructive">{rutError}</p>}
        </div>
        <div>
          <label className={labelClass} htmlFor="u-name">Nombre completo</label>
          <input id="u-name" className={inputClass} value={form.full_name} required minLength={3}
            onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
        </div>
        <div>
          <label className={labelClass} htmlFor="u-email">Correo</label>
          <input id="u-email" type="email" className={inputClass} value={form.email} required
            onChange={(e) => setForm({ ...form, email: e.target.value })} />
        </div>
        <div>
          <label className={labelClass} htmlFor="u-role">Rol</label>
          <select id="u-role" className={inputClass} value={form.role}
            onChange={(e) => setForm({ ...form, role: e.target.value as Role })}>
            {ROLES.map((r) => (
              <option key={r} value={r}>{ROLE_LABELS[r]}</option>
            ))}
          </select>
        </div>
        <div className="sm:col-span-2">
          <label className={labelClass} htmlFor="u-pass">Contraseña temporal</label>
          <input id="u-pass" type="password" className={inputClass} value={form.password} required minLength={PASSWORD_MIN_LENGTH}
            aria-describedby="u-pass-hint"
            onChange={(e) => setForm({ ...form, password: e.target.value })} autoComplete="new-password" />
          <p id="u-pass-hint" className="mt-1 text-xs text-muted-foreground">Mínimo {PASSWORD_MIN_LENGTH} caracteres, con letras y números. La persona deberá cambiarla en su primer ingreso; entréguela por un canal seguro.</p>
        </div>
      </div>
      <div className="flex justify-end gap-2">
        <button type="button" className={secondaryButton} onClick={onCancel}>Cancelar</button>
        <button type="submit" disabled={saving || !!rutError} className={primaryButton}>
          {saving && <Loader2 aria-hidden className="w-4 h-4 animate-spin" />}
          Crear usuario
        </button>
      </div>
    </form>
  );
}

function AuditViewer({ users }: { users: UserAccount[] }) {
  const [filters, setFilters] = useState({ action: '', user_id: '', from: '', to: '' });
  const [page, setPage] = useState(1);
  const [data, setData] = useState<Page<AuditEntry> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const size = 25;

  const load = useCallback(async () => {
    const r = await apiClient.listAudit({
      action: filters.action || undefined,
      user_id: filters.user_id ? Number(filters.user_id) : undefined,
      from: filters.from ? `${filters.from}T00:00:00` : undefined,
      to: filters.to ? `${filters.to}T23:59:59` : undefined,
      page,
      size,
    });
    if (r.data) {
      setData(r.data);
      setError(null);
    } else setError(r.error || 'No se pudo cargar la auditoría.');
  }, [filters, page]);

  useEffect(() => {
    load();
  }, [load]);

  const userName = (id: number | null) =>
    id === null ? '— (sin usuario)' : users.find((u) => u.id === id)?.full_name ?? `#${id}`;
  const totalPages = data ? Math.max(1, Math.ceil(data.total / size)) : 1;

  return (
    <section aria-labelledby="audit-title" className={cn(cardClass, 'overflow-hidden')}>
      <div className="p-6 pb-4 space-y-4">
        <div className="flex items-baseline gap-3">
          <h2 id="audit-title" className={sectionTitle}>Bitácora de auditoría</h2>
          {data && <span className="text-sm text-muted-foreground tabular-nums">{data.total} registros</span>}
        </div>
        <div className="grid sm:grid-cols-4 gap-3">
          <div>
            <label htmlFor="a-action" className={labelClass}>Acción</label>
            <select id="a-action" className={inputClass} value={filters.action}
              onChange={(e) => { setPage(1); setFilters({ ...filters, action: e.target.value }); }}>
              <option value="">Todas</option>
              {ACTIONS.map((a) => <option key={a} value={a}>{a}</option>)}
            </select>
          </div>
          <div>
            <label htmlFor="a-user" className={labelClass}>Usuario</label>
            <select id="a-user" className={inputClass} value={filters.user_id}
              onChange={(e) => { setPage(1); setFilters({ ...filters, user_id: e.target.value }); }}>
              <option value="">Todos</option>
              {users.map((u) => <option key={u.id} value={u.id}>{u.full_name}</option>)}
            </select>
          </div>
          <div>
            <label htmlFor="a-from" className={labelClass}>Desde</label>
            <input id="a-from" type="date" className={inputClass} value={filters.from}
              onChange={(e) => { setPage(1); setFilters({ ...filters, from: e.target.value }); }} />
          </div>
          <div>
            <label htmlFor="a-to" className={labelClass}>Hasta</label>
            <input id="a-to" type="date" className={inputClass} value={filters.to}
              onChange={(e) => { setPage(1); setFilters({ ...filters, to: e.target.value }); }} />
          </div>
        </div>
        <ErrorMessage>{error}</ErrorMessage>
      </div>
      {data === null ? (
        <Loading label="Cargando auditoría…" />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <caption className="sr-only">Registros de auditoría</caption>
            <thead className="bg-muted/60">
              <tr>
                <th scope="col" className={thClass}>Fecha</th>
                <th scope="col" className={thClass}>Usuario</th>
                <th scope="col" className={thClass}>Acción</th>
                <th scope="col" className={thClass}>Entidad</th>
                <th scope="col" className={thClass}>IP</th>
                <th scope="col" className={thClass}>Detalle</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((a) => (
                <tr key={a.id}>
                  <td className={cn(tdClass, 'text-muted-foreground tabular-nums')}>{formatDateTime(a.created_at)}</td>
                  <td className={tdClass}>{userName(a.user_id)}</td>
                  <td className={tdClass}>
                    <span className={cn('text-xs font-extrabold tracking-wide', a.action.endsWith('_FAIL') ? 'text-alta' : 'text-brand')}>
                      {a.action}
                    </span>
                  </td>
                  <td className={cn(tdClass, 'text-muted-foreground')}>
                    {a.entity}{a.entity_id !== null ? ` #${a.entity_id}` : ''}
                  </td>
                  <td className={cn(tdClass, 'text-muted-foreground tabular-nums')}>{a.ip_address ?? '—'}</td>
                  <td className={cn(tdClass, 'text-muted-foreground max-w-xs truncate')} title={a.detail ? JSON.stringify(a.detail) : undefined}>
                    {a.detail ? JSON.stringify(a.detail) : ''}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <div className="flex items-center justify-between px-4 py-3 border-t border-border">
        <button className={secondaryButton} disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
          <ChevronLeft aria-hidden className="w-4 h-4" /> Anterior
        </button>
        <span className="text-sm text-muted-foreground tabular-nums">Página {page} de {totalPages}</span>
        <button className={secondaryButton} disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
          Siguiente <ChevronRight aria-hidden className="w-4 h-4" />
        </button>
      </div>
    </section>
  );
}

function ResetPasswordForm({ user, onDone }: { user: UserAccount; onDone: (error?: string) => void }) {
  const [password, setPassword] = useState('');
  const [saving, setSaving] = useState(false);
  const ok = passwordHints(password).every((h) => h.ok);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ok) return;
    setSaving(true);
    const r = await apiClient.updateUser(user.id, { password });
    setSaving(false);
    if (!r.error) toast.success(`Contraseña temporal asignada a ${user.full_name}`);
    onDone(r.error);
  };

  const inputId = `reset-${user.id}`;
  return (
    <form onSubmit={submit} className="flex flex-wrap items-end gap-3">
      <div>
        <label htmlFor={inputId} className={labelClass}>Contraseña temporal para {user.full_name}</label>
        <input
          id={inputId}
          type="password"
          className={cn(inputClass, 'w-72')}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder={`Mínimo ${PASSWORD_MIN_LENGTH}, con letras y números`}
          autoComplete="new-password"
          required
        />
      </div>
      <button type="submit" className={primaryButton} disabled={!ok || saving}>
        {saving && <Loader2 aria-hidden className="w-4 h-4 animate-spin" />}
        Restablecer
      </button>
      <button type="button" className={secondaryButton} onClick={() => onDone()}>Cancelar</button>
      <p className="w-full text-xs text-muted-foreground">Cierra sus sesiones y le exige cambiarla al ingresar.</p>
    </form>
  );
}

function ErrorViewer({ users }: { users: UserAccount[] }) {
  const [filters, setFilters] = useState({ error_type: '', from: '', to: '' });
  const [page, setPage] = useState(1);
  const [data, setData] = useState<Page<ErrorLogEntry> | null>(null);
  const [types, setTypes] = useState<ErrorTypeCount[]>([]);
  const [error, setError] = useState<string | null>(null);
  const size = 25;

  const load = useCallback(async () => {
    const [r, t] = await Promise.all([
      apiClient.listErrors({
        error_type: filters.error_type || undefined,
        from: filters.from ? `${filters.from}T00:00:00` : undefined,
        to: filters.to ? `${filters.to}T23:59:59` : undefined,
        page,
        size,
      }),
      apiClient.listErrorTypes(),
    ]);
    if (t.data) setTypes(t.data);
    if (r.data) {
      setData(r.data);
      setError(null);
    } else setError(r.error || 'No se pudo cargar el registro de errores.');
  }, [filters, page]);

  useEffect(() => {
    load();
  }, [load]);

  const userName = (id: number | null) => (id === null ? '—' : users.find((u) => u.id === id)?.full_name ?? `#${id}`);
  const totalPages = data ? Math.max(1, Math.ceil(data.total / size)) : 1;

  return (
    <section aria-labelledby="errors-title" className={cn(cardClass, 'overflow-hidden')}>
      <div className="p-6 pb-4 space-y-4">
        <div>
          <div className="flex items-baseline gap-3">
            <h2 id="errors-title" className={sectionTitle}>Errores del servidor (5xx)</h2>
            {data && <span className="text-sm text-muted-foreground tabular-nums">{data.total} registros</span>}
          </div>
          <p className="mt-1 text-sm text-muted-foreground">
            Sin datos personales ni clínicos. El código de solicitud es el que ve el usuario en el mensaje de error.
          </p>
        </div>
        <div className="grid sm:grid-cols-3 gap-3">
          <div>
            <label htmlFor="e-type" className={labelClass}>Tipo</label>
            <select id="e-type" className={inputClass} value={filters.error_type}
              onChange={(e) => { setPage(1); setFilters({ ...filters, error_type: e.target.value }); }}>
              <option value="">Todos</option>
              {types.map((t) => (
                <option key={t.error_type} value={t.error_type}>{t.error_type} ({t.count})</option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="e-from" className={labelClass}>Desde</label>
            <input id="e-from" type="date" className={inputClass} value={filters.from}
              onChange={(e) => { setPage(1); setFilters({ ...filters, from: e.target.value }); }} />
          </div>
          <div>
            <label htmlFor="e-to" className={labelClass}>Hasta</label>
            <input id="e-to" type="date" className={inputClass} value={filters.to}
              onChange={(e) => { setPage(1); setFilters({ ...filters, to: e.target.value }); }} />
          </div>
        </div>
        <ErrorMessage>{error}</ErrorMessage>
      </div>
      {data === null ? (
        <Loading label="Cargando errores…" />
      ) : data.items.length === 0 ? (
        <p className="px-6 pb-8 text-sm text-muted-foreground">No hay errores registrados con estos filtros.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <caption className="sr-only">Errores del servidor</caption>
            <thead className="bg-muted/60">
              <tr>
                <th scope="col" className={thClass}>Fecha</th>
                <th scope="col" className={thClass}>Código</th>
                <th scope="col" className={thClass}>Ruta</th>
                <th scope="col" className={thClass}>Tipo</th>
                <th scope="col" className={thClass}>Mensaje</th>
                <th scope="col" className={thClass}>Ubicación</th>
                <th scope="col" className={thClass}>Usuario</th>
                <th scope="col" className={thClass}>Solicitud</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((e) => (
                <tr key={e.id}>
                  <td className={cn(tdClass, 'text-muted-foreground tabular-nums')}>{formatDateTime(e.occurred_at)}</td>
                  <td className={tdClass}><span className="text-xs font-extrabold text-alta">{e.status_code}</span></td>
                  <td className={tdClass}>{e.method} {e.path}</td>
                  <td className={cn(tdClass, 'text-muted-foreground')}>{e.error_type}</td>
                  <td className={cn(tdClass, 'text-muted-foreground max-w-xs truncate')} title={e.message ?? ''}>{e.message ?? '—'}</td>
                  <td className={cn(tdClass, 'text-muted-foreground')}>{e.location ?? '—'}</td>
                  <td className={cn(tdClass, 'text-muted-foreground')}>{userName(e.user_id)}</td>
                  <td className={cn(tdClass, 'text-muted-foreground tabular-nums')}>{e.request_id.slice(0, 8)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <div className="flex items-center justify-between px-4 py-3 border-t border-border">
        <button className={secondaryButton} disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
          <ChevronLeft aria-hidden className="w-4 h-4" /> Anterior
        </button>
        <span className="text-sm text-muted-foreground tabular-nums">Página {page} de {totalPages}</span>
        <button className={secondaryButton} disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
          Siguiente <ChevronRight aria-hidden className="w-4 h-4" />
        </button>
      </div>
    </section>
  );
}

export default function AdminPanel() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [privacy, setPrivacy] = useState<DataRequestSummary | null>(null);
  const [users, setUsers] = useState<UserAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [tab, setTab] = useState<'users' | 'audit' | 'errors'>('users');
  const [resetFor, setResetFor] = useState<number | null>(null);
  const [confirmUser, setConfirmUser] = useState<UserAccount | null>(null);

  const loadData = useCallback(async () => {
    const [s, u, pr] = await Promise.all([apiClient.getAdminStats(), apiClient.listUsers(), apiClient.dataRequestsSummary()]);
    if (s.data) setStats(s.data);
    if (pr.data) setPrivacy(pr.data);
    if (u.data) setUsers(u.data);
    setError(s.error || u.error || null);
    setLoading(false);
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const updateUser = async (user: UserAccount, change: { role?: Role; is_active?: boolean }) => {
    const r = await apiClient.updateUser(user.id, change);
    if (r.error) setError(r.error);
    else if (change.is_active !== undefined) toast.success(`${user.full_name} ${change.is_active ? 'activado' : 'desactivado'}`);
    else if (change.role) toast.success(`Rol de ${user.full_name}: ${ROLE_LABELS[change.role]}`);
    loadData();
  };

  const unlockUser = async (user: UserAccount) => {
    const r = await apiClient.unlockUser(user.id);
    if (r.error) setError(r.error);
    else toast.success(`${user.full_name} desbloqueado`);
    loadData();
  };

  if (loading) return <Loading label="Cargando administración…" className="h-64" />;

  const statItems = [
    { label: 'Usuarios', value: stats?.total_users ?? 0 },
    { label: 'Usuarios activos', value: stats?.active_users ?? 0 },
    { label: 'Casos', value: stats?.total_cases ?? 0 },
    { label: 'Pacientes', value: stats?.total_patients ?? 0 },
  ];

  const tabClass = (active: boolean) =>
    cn(
      'inline-flex items-center gap-2 h-9 px-3 rounded-md text-sm transition-colors',
      active ? 'bg-card text-foreground font-bold ring-1 ring-border' : 'text-muted-foreground hover:text-foreground',
    );

  return (
    <div className={pageClass}>
      <h1 className={pageTitle}>Administración</h1>
      <p className={pageSubtitle}>
        Usuarios, roles, auditoría y errores del servidor. Por mínimo privilegio, el administrador no accede a datos clínicos.
      </p>

      <ErrorMessage className="mt-4">{error}</ErrorMessage>

      <dl className={cn(cardClass, 'mt-6 grid grid-cols-2 lg:grid-cols-4 divide-x divide-border')}>
        {statItems.map(({ label, value }) => (
          <div key={label} className="px-6 py-4">
            <dd className="text-2xl font-extrabold tabular-nums">{value.toLocaleString('es-CL')}</dd>
            <dt className="text-sm text-muted-foreground">{label}</dt>
          </div>
        ))}
      </dl>

      {privacy && (
        <div className={cn(cardClass, 'mt-4 px-6 py-4 flex flex-wrap items-baseline gap-x-6 gap-y-1 text-sm')}>
          <span className="font-bold">Solicitudes de titulares (Ley 21.719)</span>
          <span><strong className="tabular-nums">{privacy.open_total}</strong> <span className="text-muted-foreground">abiertas</span></span>
          <span className={privacy.overdue > 0 ? 'font-bold text-alta' : 'text-muted-foreground'}>
            <span className="tabular-nums">{privacy.overdue}</span> con el plazo de 30 días vencido
          </span>
          <span className="text-muted-foreground">
            <span className="tabular-nums">{privacy.by_status.RESUELTA}</span> resueltas, <span className="tabular-nums">{privacy.by_status.RECHAZADA}</span> rechazadas
          </span>
          <span className="text-xs text-muted-foreground">Las gestionan médicos y administrativos en «Privacidad».</span>
        </div>
      )}

      <div className="mt-6 flex flex-wrap items-center justify-between gap-3">
        <div role="group" aria-label="Sección" className="inline-flex p-1 rounded-lg bg-muted">
          <button className={tabClass(tab === 'users')} aria-pressed={tab === 'users'} onClick={() => setTab('users')}>
            <Users aria-hidden className="w-4 h-4" /> Usuarios
          </button>
          <button className={tabClass(tab === 'audit')} aria-pressed={tab === 'audit'} onClick={() => setTab('audit')}>
            <ScrollText aria-hidden className="w-4 h-4" /> Auditoría
          </button>
          <button className={tabClass(tab === 'errors')} aria-pressed={tab === 'errors'} onClick={() => setTab('errors')}>
            <ServerCrash aria-hidden className="w-4 h-4" /> Errores
          </button>
        </div>
        {tab === 'users' && (
          <button className={primaryButton} onClick={() => setShowForm(true)}>
            <UserPlus aria-hidden className="w-4 h-4" /> Nuevo usuario
          </button>
        )}
      </div>

      <div className="mt-4">
        {tab === 'users' ? (
          <section aria-label="Usuarios y roles" className={cn(cardClass, 'overflow-hidden')}>
            <div className="overflow-x-auto">
              <table className="w-full">
                <caption className="sr-only">Usuarios y roles</caption>
                <thead className="bg-muted/60">
                  <tr>
                    <th scope="col" className={thClass}>Nombre</th>
                    <th scope="col" className={thClass}>RUT</th>
                    <th scope="col" className={thClass}>Correo</th>
                    <th scope="col" className={thClass}>Rol</th>
                    <th scope="col" className={thClass}>Último acceso</th>
                    <th scope="col" className={thClass}>Estado</th>
                    <th scope="col" className={thClass}>Acceso</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <Fragment key={u.id}>
                    <tr>
                      <td className={cn(tdClass, 'font-semibold')}>{u.full_name}</td>
                      <td className={cn(tdClass, 'text-muted-foreground tabular-nums')}>{u.rut}</td>
                      <td className={cn(tdClass, 'text-muted-foreground')}>{u.email}</td>
                      <td className={tdClass}>
                        <select
                          className={cn(inputClass, 'h-9 w-44')}
                          value={u.role}
                          onChange={(e) => updateUser(u, { role: e.target.value as Role })}
                          aria-label={`Rol de ${u.full_name}`}
                        >
                          {ROLES.map((r) => <option key={r} value={r}>{ROLE_LABELS[r]}</option>)}
                        </select>
                      </td>
                      <td className={cn(tdClass, 'text-muted-foreground tabular-nums')}>{formatDateTime(u.last_login_at)}</td>
                      <td className={tdClass}>
                        <span className="inline-flex items-center gap-3">
                          <span className="inline-flex items-center gap-1.5 text-sm">
                            <span aria-hidden className={cn('w-2 h-2 rounded-full', u.is_active ? 'bg-baja' : 'bg-muted-foreground')} />
                            {u.is_active ? 'Activo' : 'Inactivo'}
                          </span>
                          <button
                            className={cn(secondaryButton, 'h-8 px-3 text-xs')}
                            onClick={() => (u.is_active ? setConfirmUser(u) : updateUser(u, { is_active: true }))}
                          >
                            {u.is_active ? 'Desactivar' : 'Activar'}
                          </button>
                        </span>
                      </td>
                      <td className={tdClass}>
                        <span className="flex flex-wrap items-center gap-2">
                          {isLocked(u) && (
                            <button
                              onClick={() => unlockUser(u)}
                              className={cn(secondaryButton, 'h-8 px-3 text-xs text-media border-media/40')}
                              title={`Bloqueado hasta ${formatDateTime(u.locked_until)} por intentos fallidos`}
                            >
                              <Unlock aria-hidden className="w-3.5 h-3.5" /> Bloqueado: desbloquear
                            </button>
                          )}
                          {u.must_change_password && (
                            <span className="text-xs font-semibold text-muted-foreground">Cambio de contraseña pendiente</span>
                          )}
                          <button
                            onClick={() => setResetFor(resetFor === u.id ? null : u.id)}
                            aria-expanded={resetFor === u.id}
                            className={cn(ghostButton, 'h-8 px-2 text-xs')}
                          >
                            <KeyRound aria-hidden className="w-3.5 h-3.5" /> Restablecer
                          </button>
                        </span>
                      </td>
                    </tr>
                    {resetFor === u.id && (
                      <tr>
                        <td colSpan={7} className="px-4 py-4 bg-muted border-b border-border">
                          <ResetPasswordForm
                            user={u}
                            onDone={(err) => {
                              setResetFor(null);
                              if (err) setError(err);
                              loadData();
                            }}
                          />
                        </td>
                      </tr>
                    )}
                    </Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        ) : tab === 'audit' ? (
          <AuditViewer users={users} />
        ) : (
          <ErrorViewer users={users} />
        )}
      </div>

      <Dialog open={showForm} onOpenChange={setShowForm} title="Nuevo usuario" description="La persona podrá ingresar con su RUT y esta contraseña.">
        <UserForm
          onCancel={() => setShowForm(false)}
          onCreated={() => {
            setShowForm(false);
            loadData();
          }}
        />
      </Dialog>

      <Dialog
        open={confirmUser !== null}
        onOpenChange={(open) => !open && setConfirmUser(null)}
        title={`¿Desactivar a ${confirmUser?.full_name ?? ''}?`}
        description="No podrá iniciar sesión hasta que se vuelva a activar. Sus registros se conservan."
        footer={
          <>
            <button className={secondaryButton} onClick={() => setConfirmUser(null)}>Cancelar</button>
            <button
              className={dangerButton}
              onClick={() => {
                if (confirmUser) updateUser(confirmUser, { is_active: false });
                setConfirmUser(null);
              }}
            >
              Desactivar
            </button>
          </>
        }
      >
        <p className="text-sm text-muted-foreground">Esta acción queda registrada en la bitácora de auditoría.</p>
      </Dialog>
    </div>
  );
}
