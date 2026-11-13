import { useCallback, useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { CheckCircle2, ChevronLeft, ChevronRight, LayoutDashboard, Loader2, ScrollText, ServerCrash, Unlock, UserCheck, UserPlus, Users, UserX } from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '../services/api';
import type {
  AdminOverview as Overview,
  AdminStats,
  AuditEntry,
  DataRequestSummary,
  ErrorLogEntry,
  ErrorTypeCount,
  InferenceStatus,
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
import { EmptyState, ErrorMessage, Loading } from './Feedback';
import { DetailHeader, ListHeader, Segmented } from './PageHeader';
import AdminOverview, { type AdminView } from './admin/AdminOverview';
import AuditLog from './admin/AuditLog';
import { describeAudit, relativeTime } from '../utils/audit';
import {
  cardClass,
  dangerButton,
  formatDateTime,
  ghostButton,
  inputClass,
  labelClass,
  pageClass,
  primaryButton,
  secondaryButton,
  sectionTitle,
  tdClass,
  thClass,
} from './ui';

const ROLES: Role[] = ['MEDICO', 'ADMINISTRATIVO', 'ADMIN'];
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
    if (!r.error) {
      toast.success(`Contraseña temporal asignada a ${user.full_name}`);
      setPassword('');
    }
    onDone(r.error);
  };

  const inputId = `reset-${user.id}`;
  return (
    <form onSubmit={submit} className="flex flex-wrap items-end gap-3">
      <div>
        <label htmlFor={inputId} className={labelClass}>Contraseña temporal</label>
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
    <>
      <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
        <label htmlFor="e-type" className="sr-only">Tipo de error</label>
        <select id="e-type" className={cn(inputClass, 'h-9 w-64')} value={filters.error_type}
          onChange={(e) => { setPage(1); setFilters({ ...filters, error_type: e.target.value }); }}>
          <option value="">Todos los tipos</option>
          {types.map((t) => (
            <option key={t.error_type} value={t.error_type}>{t.error_type} ({t.count})</option>
          ))}
        </select>
        <label htmlFor="e-from" className="sr-only">Desde</label>
        <input id="e-from" type="date" className={cn(inputClass, 'h-9 w-40')} value={filters.from}
          onChange={(e) => { setPage(1); setFilters({ ...filters, from: e.target.value }); }} />
        a
        <label htmlFor="e-to" className="sr-only">Hasta</label>
        <input id="e-to" type="date" className={cn(inputClass, 'h-9 w-40')} value={filters.to}
          onChange={(e) => { setPage(1); setFilters({ ...filters, to: e.target.value }); }} />
      </div>
      <ErrorMessage className="mt-4">{error}</ErrorMessage>
      <section aria-label="Errores del servidor" className={cn(cardClass, 'mt-4 overflow-hidden')}>
        {data === null ? (
          <Loading label="Cargando errores…" />
        ) : data.items.length === 0 ? (
          <EmptyState title="Sin errores del servidor" icon={<CheckCircle2 aria-hidden className="w-8 h-8 text-baja" />}>
            {filters.error_type || filters.from || filters.to
              ? 'No hay errores con estos filtros.'
              : 'Aquí aparecen las fallas internas (5xx), sin datos de pacientes, para avisar al equipo técnico.'}
          </EmptyState>
        ) : (
          <div className="relative overflow-x-auto">
            <table className="w-full">
              <caption className="sr-only">Errores del servidor</caption>
              <thead className="bg-muted/60">
                <tr>
                  <th scope="col" className={cn(thClass, 'pl-5')}>Cuándo</th>
                  <th scope="col" className={thClass}>Solicitud</th>
                  <th scope="col" className={thClass}>Tipo</th>
                  <th scope="col" className={thClass}>Mensaje</th>
                  <th scope="col" className={thClass}>Usuario</th>
                  <th scope="col" className={cn(thClass, 'pr-5')}>Referencia</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((e) => (
                  <tr key={e.id} className="align-top">
                    <td className={cn(tdClass, 'pl-5 tabular-nums')}>
                      <span className="block">{relativeTime(e.occurred_at)}</span>
                      <span className="block text-xs text-muted-foreground">{formatDateTime(e.occurred_at)}</span>
                    </td>
                    <td className={tdClass}>
                      <span className="font-bold text-destructive tabular-nums">{e.status_code}</span>{' '}
                      <span className="text-muted-foreground">{e.method} {e.path}</span>
                    </td>
                    <td className={tdClass}>{e.error_type}</td>
                    <td className={cn(tdClass, 'text-muted-foreground max-w-xs whitespace-normal')}>
                      {e.message ?? '—'}
                      {e.location && <span className="block text-xs">{e.location}</span>}
                    </td>
                    <td className={cn(tdClass, 'text-muted-foreground')}>{userName(e.user_id)}</td>
                    <td className={cn(tdClass, 'pr-5 text-muted-foreground tabular-nums')} title={e.request_id}>{e.request_id.slice(0, 8)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {data && data.total > 0 && (
          <div className="px-5 py-3 border-t border-border flex flex-wrap items-center justify-between gap-3">
            <span className="text-sm text-muted-foreground tabular-nums">{data.total} errores</span>
            <div className="flex items-center gap-3">
              <span className="text-sm text-muted-foreground tabular-nums">Página {page} de {totalPages}</span>
              <button className={secondaryButton} disabled={page <= 1} onClick={() => setPage((p) => p - 1)} aria-label="Página anterior">
                <ChevronLeft aria-hidden className="w-4 h-4" />
              </button>
              <button className={secondaryButton} disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)} aria-label="Página siguiente">
                <ChevronRight aria-hidden className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </section>
    </>
  );
}

function UserState({ u }: { u: UserAccount }) {
  if (!u.is_active) return <span className="text-sm font-semibold text-muted-foreground">Inactivo</span>;
  if (isLocked(u)) return <span className="text-sm font-semibold text-media">Bloqueado</span>;
  return <span className="text-sm text-baja">Activo</span>;
}

/** Página propia de un usuario: rol, estado, contraseña temporal y actividad reciente. */
function UserPage({ userId, meId, onBack }: { userId: number; meId: number; onBack: () => void }) {
  const [user, setUser] = useState<UserAccount | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [activity, setActivity] = useState<AuditEntry[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [role, setRole] = useState<Role>('MEDICO');
  const [confirmOff, setConfirmOff] = useState(false);
  const [busy, setBusy] = useState(false);
  const self = userId === meId;

  const load = useCallback(async () => {
    const [u, a] = await Promise.all([apiClient.listUsers(), apiClient.listAudit({ user_id: userId, page: 1, size: 10 })]);
    if (u.data) {
      const found = u.data.find((x) => x.id === userId) ?? null;
      setUser(found);
      setNotFound(!found);
      if (found) setRole(found.role);
    }
    if (a.data) setActivity(a.data.items);
    setError(u.error || a.error || null);
  }, [userId]);

  useEffect(() => {
    load();
  }, [load]);

  const update = async (change: { role?: Role; is_active?: boolean }, ok: string) => {
    setBusy(true);
    const r = await apiClient.updateUser(userId, change);
    setBusy(false);
    if (r.error) setError(r.error);
    else toast.success(ok);
    load();
  };

  const unlock = async () => {
    const r = await apiClient.unlockUser(userId);
    if (r.error) setError(r.error);
    else toast.success('Usuario desbloqueado');
    load();
  };

  if (notFound) {
    return (
      <>
        <button className={cn(ghostButton, '-ml-3 mb-4')} onClick={onBack}>
          <ChevronLeft aria-hidden className="w-4 h-4" /> Administración
        </button>
        <EmptyState title="No existe el usuario" icon={<Users aria-hidden className="w-8 h-8" />}>
          No hay un usuario con ese número.
        </EmptyState>
      </>
    );
  }
  if (!user) return error ? <ErrorMessage>{error}</ErrorMessage> : <Loading label="Cargando usuario…" />;

  const rows: [string, string][] = [
    ['Cuenta creada', formatDateTime(user.created_at)],
    ['Último ingreso', formatDateTime(user.last_login_at)],
    ['Contraseña', user.must_change_password ? 'Cambio pendiente' : 'Definida por la persona'],
  ];
  if (isLocked(user)) rows.push(['Bloqueada hasta', formatDateTime(user.locked_until)]);

  return (
    <div className="space-y-6">
      <DetailHeader
        backLabel="Administración"
        onBack={onBack}
        title={user.full_name}
        status={<UserState u={user} />}
        meta={<>RUT {user.rut} · {ROLE_LABELS[user.role]} · {user.email}</>}
        actions={
          <>
            {isLocked(user) && (
              <button className={secondaryButton} onClick={unlock}>
                <Unlock aria-hidden className="w-4 h-4" /> Desbloquear
              </button>
            )}
            {!self &&
              (user.is_active ? (
                <button className={secondaryButton} disabled={busy} onClick={() => setConfirmOff(true)}>
                  <UserX aria-hidden className="w-4 h-4" /> Desactivar
                </button>
              ) : (
                <button className={primaryButton} disabled={busy}
                  onClick={() => update({ is_active: true }, `${user.full_name} activado`)}>
                  <UserCheck aria-hidden className="w-4 h-4" /> Activar
                </button>
              ))}
          </>
        }
      />

      <ErrorMessage>{error}</ErrorMessage>

      <div className="grid xl:grid-cols-[minmax(0,7fr)_minmax(0,5fr)] gap-6 items-start">
        <div className="space-y-6 min-w-0">
          <section className={cn(cardClass, 'p-6 space-y-4')} aria-labelledby="up-role">
            <h2 id="up-role" className={sectionTitle}>Rol</h2>
            {self ? (
              <p className="text-sm text-muted-foreground">No puede cambiar su propio rol.</p>
            ) : (
              <div className="flex flex-wrap items-end gap-3">
                <div>
                  <label htmlFor="up-role-select" className={labelClass}>Rol en la plataforma</label>
                  <select id="up-role-select" className={cn(inputClass, 'w-56')} value={role}
                    onChange={(e) => setRole(e.target.value as Role)}>
                    {ROLES.map((r) => <option key={r} value={r}>{ROLE_LABELS[r]}</option>)}
                  </select>
                </div>
                <button className={primaryButton} disabled={busy || role === user.role}
                  onClick={() => update({ role }, `Rol de ${user.full_name}: ${ROLE_LABELS[role]}`)}>
                  Guardar rol
                </button>
              </div>
            )}
          </section>

          <section className={cn(cardClass, 'p-6 space-y-4')} aria-labelledby="up-password">
            <h2 id="up-password" className={sectionTitle}>Restablecer contraseña</h2>
            <ResetPasswordForm
              user={user}
              onDone={(err) => {
                if (err) setError(err);
                load();
              }}
            />
          </section>

          <section className={cn(cardClass, 'overflow-hidden')} aria-labelledby="up-activity">
            <h2 id="up-activity" className={cn(sectionTitle, 'px-6 pt-5 pb-3')}>Actividad reciente</h2>
            {activity === null ? (
              <Loading label="Cargando actividad…" />
            ) : activity.length === 0 ? (
              <p className="px-6 pb-5 text-sm text-muted-foreground">Sin registros.</p>
            ) : (
              <ul>
                {activity.map((e) => (
                  <li key={e.id} className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-0.5 px-6 py-2.5 border-t border-border text-sm">
                    <span>
                      {describeAudit(e).title}
                      {describeAudit(e).detail && <span className="text-muted-foreground"> · {describeAudit(e).detail}</span>}
                    </span>
                    <span className="text-muted-foreground tabular-nums">{formatDateTime(e.created_at)}</span>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>

        <section className={cn(cardClass, 'p-6')} aria-labelledby="up-account">
          <h2 id="up-account" className={sectionTitle}>Cuenta</h2>
          <dl className="mt-4 divide-y divide-border text-sm">
            {rows.map(([label, value]) => (
              <div key={label} className="flex items-baseline justify-between gap-4 py-2.5 first:pt-0">
                <dt className="text-muted-foreground">{label}</dt>
                <dd className="font-medium tabular-nums text-right">{value}</dd>
              </div>
            ))}
          </dl>
        </section>
      </div>

      <Dialog
        open={confirmOff}
        onOpenChange={setConfirmOff}
        title={`¿Desactivar a ${user.full_name}?`}
        description="No podrá iniciar sesión hasta que se vuelva a activar. Sus registros se conservan."
        footer={
          <>
            <button className={secondaryButton} onClick={() => setConfirmOff(false)}>Cancelar</button>
            <button
              className={dangerButton}
              onClick={() => {
                setConfirmOff(false);
                update({ is_active: false }, `${user.full_name} desactivado`);
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

type UserFilter = 'activos' | 'inactivos' | 'bloqueados' | 'pendientes' | 'sin-uso';
const USER_FILTERS: Array<{ value: UserFilter | 'todos'; label: string }> = [
  { value: 'todos', label: 'Todos los estados' },
  { value: 'activos', label: 'Activos' },
  { value: 'inactivos', label: 'Desactivados' },
  { value: 'bloqueados', label: 'Bloqueados' },
  { value: 'pendientes', label: 'Contraseña temporal' },
  { value: 'sin-uso', label: 'Sin uso en 30 días' },
];

function matchesFilter(u: UserAccount, f: UserFilter | null): boolean {
  const idle = !u.last_login_at || Date.now() - new Date(u.last_login_at).getTime() > 30 * 86400000;
  switch (f) {
    case 'activos':
      return u.is_active;
    case 'inactivos':
      return !u.is_active;
    case 'bloqueados':
      return u.is_active && isLocked(u);
    case 'pendientes':
      return u.is_active && !!u.must_change_password;
    case 'sin-uso':
      return u.is_active && idle;
    default:
      return true;
  }
}

/** Lista de usuarios con filtros por rol, estado y búsqueda (en la dirección). */
function UsersView({ users, onOpenUser }: { users: UserAccount[] | null; onOpenUser: (id: number) => void }) {
  const [params, setParams] = useSearchParams();
  const role = (ROLES as string[]).includes(params.get('rol') ?? '') ? (params.get('rol') as Role) : null;
  const filter = USER_FILTERS.some((f) => f.value === params.get('estado')) ? (params.get('estado') as UserFilter) : null;
  const query = params.get('q') ?? '';
  const setParam = (k: string, v: string | null) => {
    const next = new URLSearchParams(params);
    if (v) next.set(k, v);
    else next.delete(k);
    setParams(next, { replace: true });
  };
  const term = query.trim().toLowerCase().replace(/\./g, '');
  const shown = (users ?? []).filter(
    (u) =>
      (!role || u.role === role) &&
      matchesFilter(u, filter) &&
      (!term || `${u.full_name} ${u.rut} ${u.email}`.toLowerCase().replace(/\./g, '').includes(term)),
  );
  const count = (r: Role | null) => (users ?? []).filter((u) => !r || u.role === r).length;

  return (
    <>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Segmented
          label="Filtrar por rol"
          value={role ?? 'todos'}
          onChange={(v) => setParam('rol', v === 'todos' ? null : v)}
          options={[
            { value: 'todos', label: 'Todos', count: users ? count(null) : null },
            ...ROLES.map((r) => ({ value: r, label: ROLE_LABELS[r], count: users ? count(r) : null })),
          ]}
        />
        <div className="flex flex-wrap items-center gap-2">
          <label htmlFor="u-filter" className="sr-only">Estado</label>
          <select id="u-filter" className={cn(inputClass, 'h-9 w-52')} value={filter ?? 'todos'}
            onChange={(e) => setParam('estado', e.target.value === 'todos' ? null : e.target.value)}>
            {USER_FILTERS.map((f) => <option key={f.value} value={f.value}>{f.label}</option>)}
          </select>
          <label htmlFor="u-search" className="sr-only">Buscar por nombre, RUT o email</label>
          <input id="u-search" type="search" className={cn(inputClass, 'h-9 w-60')} placeholder="Buscar nombre, RUT o email"
            value={query} onChange={(e) => setParam('q', e.target.value || null)} />
        </div>
      </div>

      <section aria-label="Usuarios" className={cn(cardClass, 'mt-4 overflow-hidden')}>
        {users === null ? (
          <Loading label="Cargando usuarios…" />
        ) : shown.length === 0 ? (
          <EmptyState title="Sin usuarios" icon={<Users aria-hidden className="w-8 h-8" />}>
            No hay usuarios con estos filtros.
          </EmptyState>
        ) : (
          <div className="relative overflow-x-auto">
            <table className="w-full">
              <caption className="sr-only">Usuarios</caption>
              <thead className="bg-muted/60">
                <tr>
                  <th scope="col" className={cn(thClass, 'pl-5')}>Usuario</th>
                  <th scope="col" className={thClass}>RUT</th>
                  <th scope="col" className={thClass}>Rol</th>
                  <th scope="col" className={thClass}>Estado</th>
                  <th scope="col" className={cn(thClass, 'pr-5')}>Último ingreso</th>
                </tr>
              </thead>
              <tbody>
                {shown.map((u) => (
                  <tr key={u.id} onClick={() => onOpenUser(u.id)} className="cursor-pointer hover:bg-accent/60 transition-colors">
                    <td className={cn(tdClass, 'pl-5')}>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onOpenUser(u.id);
                        }}
                        className="font-semibold hover:text-brand hover:underline text-left"
                      >
                        {u.full_name}
                      </button>
                      <span className="block text-xs text-muted-foreground">{u.email}</span>
                    </td>
                    <td className={cn(tdClass, 'text-muted-foreground tabular-nums')}>{u.rut}</td>
                    <td className={tdClass}>{ROLE_LABELS[u.role]}</td>
                    <td className={tdClass}>
                      <UserState u={u} />
                      {u.must_change_password && u.is_active && (
                        <span className="block text-xs text-muted-foreground">Contraseña temporal sin cambiar</span>
                      )}
                    </td>
                    <td className={cn(tdClass, 'pr-5 tabular-nums')}>
                      {u.last_login_at ? (
                        <>
                          <span className="block">{relativeTime(u.last_login_at)}</span>
                          {Date.now() - new Date(u.last_login_at).getTime() < 30 * 86400000 && (
                            <span className="block text-xs text-muted-foreground">{formatDateTime(u.last_login_at)}</span>
                          )}
                        </>
                      ) : (
                        <span className="text-muted-foreground">Nunca</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {users && users.length > 0 && (
          <p className="px-5 py-3 border-t border-border text-sm text-muted-foreground tabular-nums">
            {shown.length === users.length ? `${users.length} usuarios` : `${shown.length} de ${users.length} usuarios`}
          </p>
        )}
      </section>
    </>
  );
}

const VIEWS: AdminView[] = ['resumen', 'usuarios', 'auditoria', 'errores'];

interface AdminPanelProps {
  meId: number;
  /** Usuario abierto, tomado de la dirección /administracion/usuarios/:id */
  userId?: number | null;
  onOpenUser: (userId: number) => void;
  onBack: () => void;
}

export default function AdminPanel({ meId, userId = null, onOpenUser, onBack }: AdminPanelProps) {
  const [params, setParams] = useSearchParams();
  const raw = params.get('vista') as AdminView | null;
  const view: AdminView = raw && VIEWS.includes(raw) ? raw : 'resumen';
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [overview, setOverview] = useState<Overview | null>(null);
  const [privacy, setPrivacy] = useState<DataRequestSummary | null>(null);
  const [inference, setInference] = useState<InferenceStatus | null>(null);
  const [recent, setRecent] = useState<AuditEntry[] | null>(null);
  const [users, setUsers] = useState<UserAccount[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  const loadData = useCallback(async () => {
    const [s, u, pr, ov, inf, rc] = await Promise.all([
      apiClient.getAdminStats(),
      apiClient.listUsers(),
      apiClient.dataRequestsSummary(),
      apiClient.getAdminOverview(),
      apiClient.getInferenceStatus(),
      apiClient.listAudit({ page: 1, size: 8 }),
    ]);
    if (s.data) setStats(s.data);
    if (pr.data) setPrivacy(pr.data);
    if (u.data) setUsers(u.data);
    if (ov.data) setOverview(ov.data);
    setInference(inf.data ?? null);
    setRecent(rc.data?.items ?? []);
    setError(u.error || ov.error || null);
  }, []);

  useEffect(() => {
    if (userId === null) loadData();
  }, [loadData, userId]);

  if (userId !== null) {
    return (
      <div className={pageClass}>
        <UserPage key={userId} userId={userId} meId={meId} onBack={onBack} />
      </div>
    );
  }

  /** Cambia de vista; los filtros de la vista anterior no se arrastran. */
  const go = (v: AdminView, extra: Record<string, string> = {}) =>
    setParams(v === 'resumen' ? {} : { vista: v, ...extra }, { replace: false });

  return (
    <div className={pageClass}>
      <ListHeader
        title="Administración"
        actions={
          <button className={primaryButton} onClick={() => setShowForm(true)}>
            <UserPlus aria-hidden className="w-4 h-4" /> Nuevo usuario
          </button>
        }
      />

      <ErrorMessage className="mt-4">{error}</ErrorMessage>

      <Segmented
        className="mt-6"
        label="Sección"
        value={view}
        onChange={(v) => go(v)}
        options={[
          { value: 'resumen', label: <><LayoutDashboard aria-hidden className="w-4 h-4" /> Resumen</> },
          { value: 'usuarios', label: <><Users aria-hidden className="w-4 h-4" /> Usuarios</>, count: users ? users.length : null },
          { value: 'auditoria', label: <><ScrollText aria-hidden className="w-4 h-4" /> Bitácora</> },
          {
            value: 'errores',
            label: <><ServerCrash aria-hidden className="w-4 h-4" /> Errores</>,
            count: overview ? overview.server_errors_7d || undefined : undefined,
          },
        ]}
      />

      <div className="mt-4">
        {view === 'resumen' ? (
          overview ? (
            <AdminOverview
              overview={overview}
              stats={stats}
              privacy={privacy}
              inference={inference}
              recent={recent}
              users={users ?? []}
              go={go}
              onOpenUser={onOpenUser}
              onNewUser={() => setShowForm(true)}
            />
          ) : (
            <Loading label="Cargando resumen…" />
          )
        ) : view === 'usuarios' ? (
          <UsersView users={users} onOpenUser={onOpenUser} />
        ) : view === 'auditoria' ? (
          <AuditLog users={users ?? []} onOpenUser={onOpenUser} />
        ) : (
          <ErrorViewer users={users ?? []} />
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
    </div>
  );
}
