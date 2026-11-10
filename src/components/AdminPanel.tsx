import { Fragment, useCallback, useEffect, useState } from 'react';
import { Users, UserPlus, Activity, Loader2, Shield, ScrollText, X, ServerCrash, KeyRound, Unlock } from 'lucide-react';
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
import {
  cardClass,
  errorBox,
  formatDateTime,
  inputClass,
  labelClass,
  primaryButton,
  secondaryButton,
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
  const rutError = form.rut && !isValidRut(form.rut) ? 'RUT inválido' : null;

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (rutError) return;
    setSaving(true);
    setError(null);
    const r = await apiClient.createUser({ ...form, rut: normalizeRut(form.rut) });
    setSaving(false);
    if (r.data) {
      setForm(EMPTY_USER);
      onCreated();
    } else {
      setError(r.error || 'No se pudo crear el usuario');
    }
  };

  return (
    <form onSubmit={submit} className="p-3 border border-border rounded space-y-3 mb-3">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-semibold text-foreground">Nuevo usuario</h4>
        <button type="button" onClick={onCancel} aria-label="Cerrar" className="text-muted-foreground">
          <X className="w-4 h-4" />
        </button>
      </div>
      {error && <div className={errorBox}>{error}</div>}
      <div className="grid sm:grid-cols-2 gap-3">
        <div>
          <label className={labelClass} htmlFor="u-rut">RUT</label>
          <input id="u-rut" className={inputClass} value={form.rut} required
            onChange={(e) => setForm({ ...form, rut: e.target.value })} placeholder="12345678-5" />
          {rutError && <p className="mt-1 text-[10px] text-red-400">{rutError}</p>}
        </div>
        <div>
          <label className={labelClass} htmlFor="u-name">Nombre completo</label>
          <input id="u-name" className={inputClass} value={form.full_name} required minLength={3}
            onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
        </div>
        <div>
          <label className={labelClass} htmlFor="u-email">Email</label>
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
          <label className={labelClass} htmlFor="u-pass">
            Contraseña temporal (mín. {PASSWORD_MIN_LENGTH} caracteres, con letras y números)
          </label>
          <input id="u-pass" type="password" className={inputClass} value={form.password} required
            minLength={PASSWORD_MIN_LENGTH}
            onChange={(e) => setForm({ ...form, password: e.target.value })} autoComplete="new-password" />
          <p className="mt-1 text-[10px] text-muted-foreground">
            El usuario deberá cambiarla en su primer inicio de sesión.
          </p>
        </div>
      </div>
      <button type="submit" disabled={saving || !!rutError} className={primaryButton}>
        {saving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Crear usuario'}
      </button>
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
    } else setError(r.error || 'Error al cargar la auditoría');
  }, [filters, page]);

  useEffect(() => {
    load();
  }, [load]);

  const userName = (id: number | null) =>
    id === null ? '— (sin usuario)' : users.find((u) => u.id === id)?.full_name ?? `#${id}`;
  const totalPages = data ? Math.max(1, Math.ceil(data.total / size)) : 1;

  return (
    <div className={`${cardClass} p-4`}>
      <div className="flex items-center gap-2 mb-3">
        <ScrollText className="w-4 h-4 text-primary" />
        <h3 className="text-sm font-semibold text-foreground">Bitácora de auditoría</h3>
        {data && <span className="text-[10px] text-muted-foreground">{data.total} registros</span>}
      </div>
      <div className="grid sm:grid-cols-4 gap-2 mb-3">
        <select className={inputClass} value={filters.action}
          onChange={(e) => { setPage(1); setFilters({ ...filters, action: e.target.value }); }}>
          <option value="">Todas las acciones</option>
          {ACTIONS.map((a) => <option key={a} value={a}>{a}</option>)}
        </select>
        <select className={inputClass} value={filters.user_id}
          onChange={(e) => { setPage(1); setFilters({ ...filters, user_id: e.target.value }); }}>
          <option value="">Todos los usuarios</option>
          {users.map((u) => <option key={u.id} value={u.id}>{u.full_name}</option>)}
        </select>
        <input type="date" className={inputClass} value={filters.from} aria-label="Desde"
          onChange={(e) => { setPage(1); setFilters({ ...filters, from: e.target.value }); }} />
        <input type="date" className={inputClass} value={filters.to} aria-label="Hasta"
          onChange={(e) => { setPage(1); setFilters({ ...filters, to: e.target.value }); }} />
      </div>
      {error && <div className={errorBox}>{error}</div>}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-secondary/50 border-b border-border">
            <tr>
              <th className={thClass}>Fecha</th>
              <th className={thClass}>Usuario</th>
              <th className={thClass}>Acción</th>
              <th className={thClass}>Entidad</th>
              <th className={thClass}>IP</th>
              <th className={thClass}>Detalle</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {data?.items.map((a) => (
              <tr key={a.id}>
                <td className={`${tdClass} text-muted-foreground`}>{formatDateTime(a.created_at)}</td>
                <td className={`${tdClass} text-foreground`}>{userName(a.user_id)}</td>
                <td className={tdClass}>
                  <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                    a.action.endsWith('_FAIL') ? 'bg-red-500/10 text-red-400' : 'bg-primary/10 text-primary'
                  }`}>{a.action}</span>
                </td>
                <td className={`${tdClass} text-muted-foreground`}>
                  {a.entity}{a.entity_id !== null ? ` #${a.entity_id}` : ''}
                </td>
                <td className={`${tdClass} text-muted-foreground`}>{a.ip_address ?? '—'}</td>
                <td className={`${tdClass} text-muted-foreground max-w-xs truncate`}>
                  {a.detail ? JSON.stringify(a.detail) : ''}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex items-center justify-between pt-2">
        <button className={secondaryButton} disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>Anterior</button>
        <span className="text-xs text-muted-foreground">Página {page} de {totalPages}</span>
        <button className={secondaryButton} disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>Siguiente</button>
      </div>
    </div>
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
    onDone(r.error);
  };

  return (
    <form onSubmit={submit} className="flex flex-wrap items-center gap-2">
      <input
        type="password"
        className={`${inputClass} py-1 w-48`}
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder={`Temporal (mín. ${PASSWORD_MIN_LENGTH}, letras y números)`}
        aria-label={`Contraseña temporal para ${user.full_name}`}
        autoComplete="new-password"
        required
      />
      <button type="submit" className={primaryButton} disabled={!ok || saving}>
        {saving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Restablecer'}
      </button>
      <button type="button" className={secondaryButton} onClick={() => onDone()}>
        Cancelar
      </button>
      <span className="text-[10px] text-muted-foreground">
        Cierra sus sesiones y le exige cambiarla al ingresar.
      </span>
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
    } else setError(r.error || 'Error al cargar el registro de errores');
  }, [filters, page]);

  useEffect(() => {
    load();
  }, [load]);

  const userName = (id: number | null) =>
    id === null ? '—' : users.find((u) => u.id === id)?.full_name ?? `#${id}`;
  const totalPages = data ? Math.max(1, Math.ceil(data.total / size)) : 1;

  return (
    <div className={`${cardClass} p-4`}>
      <div className="flex items-center gap-2 mb-1">
        <ServerCrash className="w-4 h-4 text-primary" />
        <h3 className="text-sm font-semibold text-foreground">Errores del servidor (5xx)</h3>
        {data && <span className="text-[10px] text-muted-foreground">{data.total} registros</span>}
      </div>
      <p className="mb-3 text-[10px] text-muted-foreground">
        Sin datos personales ni clínicos. El código de solicitud es el que ve el usuario en el mensaje de error.
      </p>
      <div className="grid sm:grid-cols-3 gap-2 mb-3">
        <select className={inputClass} value={filters.error_type} aria-label="Tipo de error"
          onChange={(e) => { setPage(1); setFilters({ ...filters, error_type: e.target.value }); }}>
          <option value="">Todos los tipos</option>
          {types.map((t) => (
            <option key={t.error_type} value={t.error_type}>{t.error_type} ({t.count})</option>
          ))}
        </select>
        <input type="date" className={inputClass} value={filters.from} aria-label="Desde"
          onChange={(e) => { setPage(1); setFilters({ ...filters, from: e.target.value }); }} />
        <input type="date" className={inputClass} value={filters.to} aria-label="Hasta"
          onChange={(e) => { setPage(1); setFilters({ ...filters, to: e.target.value }); }} />
      </div>
      {error && <div className={errorBox}>{error}</div>}
      {data && data.items.length === 0 ? (
        <p className="py-6 text-center text-xs text-muted-foreground">No hay errores registrados con estos filtros.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-secondary/50 border-b border-border">
              <tr>
                <th className={thClass}>Fecha</th>
                <th className={thClass}>Código</th>
                <th className={thClass}>Ruta</th>
                <th className={thClass}>Tipo</th>
                <th className={thClass}>Mensaje</th>
                <th className={thClass}>Ubicación</th>
                <th className={thClass}>Usuario</th>
                <th className={thClass}>Solicitud</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {data?.items.map((e) => (
                <tr key={e.id}>
                  <td className={`${tdClass} text-muted-foreground`}>{formatDateTime(e.occurred_at)}</td>
                  <td className={tdClass}>
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-red-500/10 text-red-400">
                      {e.status_code}
                    </span>
                  </td>
                  <td className={`${tdClass} text-foreground font-mono`}>{e.method} {e.path}</td>
                  <td className={`${tdClass} text-muted-foreground font-mono`}>{e.error_type}</td>
                  <td className={`${tdClass} text-muted-foreground max-w-xs truncate`} title={e.message ?? ''}>
                    {e.message ?? '—'}
                  </td>
                  <td className={`${tdClass} text-muted-foreground font-mono`}>{e.location ?? '—'}</td>
                  <td className={`${tdClass} text-muted-foreground`}>{userName(e.user_id)}</td>
                  <td className={`${tdClass} text-muted-foreground font-mono`}>{e.request_id.slice(0, 8)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <div className="flex items-center justify-between pt-2">
        <button className={secondaryButton} disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>Anterior</button>
        <span className="text-xs text-muted-foreground">Página {page} de {totalPages}</span>
        <button className={secondaryButton} disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>Siguiente</button>
      </div>
    </div>
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

  const loadData = useCallback(async () => {
    const [s, u, pr] = await Promise.all([
      apiClient.getAdminStats(),
      apiClient.listUsers(),
      apiClient.dataRequestsSummary(),
    ]);
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
    loadData();
  };

  const unlockUser = async (user: UserAccount) => {
    const r = await apiClient.unlockUser(user.id);
    if (r.error) setError(r.error);
    loadData();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  const statCards = [
    { label: 'Usuarios', value: stats?.total_users ?? 0, icon: Users },
    { label: 'Usuarios activos', value: stats?.active_users ?? 0, icon: Shield },
    { label: 'Casos', value: stats?.total_cases ?? 0, icon: Activity },
    { label: 'Pacientes', value: stats?.total_patients ?? 0, icon: UserPlus },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 space-y-4">
      <div>
        <h2 className="text-lg font-bold text-foreground">Administración</h2>
        <p className="mt-0.5 text-xs text-muted-foreground">
          Usuarios, roles, auditoría y errores del servidor. Por mínimo privilegio, el administrador no accede a datos clínicos.
        </p>
      </div>

      {error && <div className={errorBox}>{error}</div>}

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {statCards.map(({ label, value, icon: Icon }) => (
          <div key={label} className={`${cardClass} p-3`}>
            <Icon className="w-4 h-4 text-primary mb-2" />
            <p className="text-xl font-bold text-foreground">{value.toLocaleString('es-CL')}</p>
            <p className="text-[10px] text-muted-foreground">{label}</p>
          </div>
        ))}
      </div>

      {privacy && (
        <div className={`${cardClass} p-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs`}>
          <span className="font-semibold text-foreground">Solicitudes de titulares (Ley 21.719)</span>
          <span className="text-muted-foreground">{privacy.open_total} abiertas</span>
          <span className={privacy.overdue > 0 ? 'text-red-400 font-semibold' : 'text-muted-foreground'}>
            {privacy.overdue} con el plazo de 30 días vencido
          </span>
          <span className="text-muted-foreground">
            {privacy.by_status.RESUELTA} resueltas · {privacy.by_status.RECHAZADA} rechazadas
          </span>
          <span className="text-[10px] text-muted-foreground">
            Las gestionan médicos y administrativos en «Privacidad».
          </span>
        </div>
      )}

      <div className="flex gap-2">
        <button className={tab === 'users' ? primaryButton : secondaryButton} onClick={() => setTab('users')}>
          <Users className="w-3.5 h-3.5" /> Usuarios
        </button>
        <button className={tab === 'audit' ? primaryButton : secondaryButton} onClick={() => setTab('audit')}>
          <ScrollText className="w-3.5 h-3.5" /> Auditoría
        </button>
        <button className={tab === 'errors' ? primaryButton : secondaryButton} onClick={() => setTab('errors')}>
          <ServerCrash className="w-3.5 h-3.5" /> Errores
        </button>
      </div>

      {tab === 'users' ? (
        <div className={`${cardClass} p-4`}>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-foreground">Usuarios y roles</h3>
            {!showForm && (
              <button className={primaryButton} onClick={() => setShowForm(true)}>
                <UserPlus className="w-3.5 h-3.5" /> Nuevo usuario
              </button>
            )}
          </div>
          {showForm && (
            <UserForm
              onCancel={() => setShowForm(false)}
              onCreated={() => {
                setShowForm(false);
                loadData();
              }}
            />
          )}
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-secondary/50 border-b border-border">
                <tr>
                  <th className={thClass}>Nombre</th>
                  <th className={thClass}>RUT</th>
                  <th className={thClass}>Email</th>
                  <th className={thClass}>Rol</th>
                  <th className={thClass}>Último acceso</th>
                  <th className={thClass}>Estado</th>
                  <th className={thClass}>Acceso</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {users.map((u) => (
                  <Fragment key={u.id}>
                  <tr>
                    <td className={`${tdClass} text-foreground font-medium`}>{u.full_name}</td>
                    <td className={`${tdClass} text-muted-foreground`}>{u.rut}</td>
                    <td className={`${tdClass} text-muted-foreground`}>{u.email}</td>
                    <td className={tdClass}>
                      <select
                        className={`${inputClass} py-1`}
                        value={u.role}
                        onChange={(e) => updateUser(u, { role: e.target.value as Role })}
                        aria-label={`Rol de ${u.full_name}`}
                      >
                        {ROLES.map((r) => <option key={r} value={r}>{ROLE_LABELS[r]}</option>)}
                      </select>
                    </td>
                    <td className={`${tdClass} text-muted-foreground`}>{formatDateTime(u.last_login_at)}</td>
                    <td className={tdClass}>
                      <button
                        onClick={() => updateUser(u, { is_active: !u.is_active })}
                        className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${
                          u.is_active
                            ? 'bg-green-500/10 text-green-400 border-green-500/20'
                            : 'bg-red-500/10 text-red-400 border-red-500/20'
                        }`}
                        title={u.is_active ? 'Clic para desactivar' : 'Clic para activar'}
                      >
                        {u.is_active ? 'Activo' : 'Inactivo'}
                      </button>
                    </td>
                    <td className={tdClass}>
                      <div className="flex flex-wrap items-center gap-1.5">
                        {isLocked(u) && (
                          <button
                            onClick={() => unlockUser(u)}
                            className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold border bg-orange-500/10 text-orange-400 border-orange-500/20"
                            title={`Bloqueado hasta ${formatDateTime(u.locked_until)} por intentos fallidos. Clic para desbloquear`}
                          >
                            <Unlock className="w-3 h-3" /> Bloqueado · desbloquear
                          </button>
                        )}
                        {u.must_change_password && (
                          <span className="px-2 py-0.5 rounded text-[10px] font-semibold border bg-secondary text-muted-foreground border-border">
                            Cambio de contraseña pendiente
                          </span>
                        )}
                        <button
                          onClick={() => setResetFor(resetFor === u.id ? null : u.id)}
                          className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] text-muted-foreground hover:text-foreground hover:bg-accent"
                          title="Asignar una contraseña temporal"
                        >
                          <KeyRound className="w-3 h-3" /> Restablecer
                        </button>
                      </div>
                    </td>
                  </tr>
                  {resetFor === u.id && (
                    <tr>
                      <td colSpan={7} className="px-3 py-2 bg-secondary/30">
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
        </div>
      ) : tab === 'audit' ? (
        <AuditViewer users={users} />
      ) : (
        <ErrorViewer users={users} />
      )}
    </div>
  );
}
