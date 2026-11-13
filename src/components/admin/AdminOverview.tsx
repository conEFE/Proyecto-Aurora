import { useState, type ReactNode } from 'react';
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Clock,
  FileWarning,
  KeyRound,
  Lock,
  ServerCrash,
  ShieldAlert,
  UserX,
} from 'lucide-react';
import type { AdminOverview as Overview, AdminStats, AuditEntry, DataRequestSummary, InferenceStatus, Role, UserAccount } from '../../types';
import { ROLE_LABELS } from '../../types';
import { cn } from '../../lib/cn';
import { AUDIT_GROUPS, SECURITY_ACTIONS, actorFallback, describeAudit, relativeTime, type AuditGroup } from '../../utils/audit';
import { SimulatedBadge } from '../Badges';
import { cardClass, ghostButton, sectionTitle } from '../ui';

export type AdminView = 'resumen' | 'usuarios' | 'auditoria' | 'errores';
type Go = (view: AdminView, params?: Record<string, string>) => void;

const ROLES: Role[] = ['MEDICO', 'ADMINISTRATIVO', 'ADMIN'];
const isoDay = (d: Date) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;

function Section({ title, aside, children, className }: { title: string; aside?: ReactNode; children: ReactNode; className?: string }) {
  return (
    <section className={cn(cardClass, 'p-6', className)} aria-label={title}>
      <div className="mb-4 flex flex-wrap items-baseline justify-between gap-2">
        <h2 className={sectionTitle}>{title}</h2>
        {aside}
      </div>
      {children}
    </section>
  );
}

/** Ingresos correctos y fallidos por día: barras pareadas, los fallidos en el color de alerta. */
function LoginChart({ days }: { days: Overview['logins_per_day'] }) {
  const [hover, setHover] = useState<number | null>(null);
  const W = 640;
  const H = 170;
  const pad = { l: 26, r: 6, t: 10, b: 22 };
  const max = Math.max(1, ...days.map((d) => Math.max(d.ok, d.failed)));
  const top = max <= 4 ? max : Math.ceil(max / 4) * 4;
  const plotW = W - pad.l - pad.r;
  const plotH = H - pad.t - pad.b;
  const slot = plotW / days.length;
  const bw = Math.min(12, slot * 0.32);
  const y = (v: number) => pad.t + plotH * (1 - v / top);
  const fmt = (d: string) => new Date(`${d}T12:00:00`).toLocaleDateString('es-CL', { day: '2-digit', month: 'short' });
  const total = days.reduce((a, d) => a + d.ok, 0);
  const failed = days.reduce((a, d) => a + d.failed, 0);

  return (
    <div className="relative">
      <p className="mb-2 text-sm text-muted-foreground tabular-nums">
        <strong className="text-foreground">{total.toLocaleString('es-CL')}</strong> ingresos ·{' '}
        <strong className={failed ? 'text-destructive' : 'text-foreground'}>{failed.toLocaleString('es-CL')}</strong> fallidos
      </p>
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="w-full h-44"
        role="img"
        aria-label={`Ingresos por día: ${days.map((d) => `${fmt(d.day)}, ${d.ok} correctos y ${d.failed} fallidos`).join('; ')}`}
        onMouseLeave={() => setHover(null)}
      >
        {[0, top / 2, top].map((t) => (
          <g key={t}>
            <line x1={pad.l} x2={W - pad.r} y1={y(t)} y2={y(t)} stroke="hsl(var(--border))" />
            <text x={pad.l - 6} y={y(t) + 4} textAnchor="end" fontSize={11} fill="hsl(var(--muted-foreground))">{Math.round(t)}</text>
          </g>
        ))}
        {days.map((d, i) => {
          const cx = pad.l + i * slot + slot / 2;
          return (
            <g key={d.day} onMouseEnter={() => setHover(i)} opacity={hover === null || hover === i ? 1 : 0.5}>
              <rect x={pad.l + i * slot} y={pad.t} width={slot} height={plotH} fill="transparent" />
              {d.ok > 0 && <rect x={cx - bw - 1} y={y(d.ok)} width={bw} height={y(0) - y(d.ok)} rx={2} fill="hsl(var(--brand))" />}
              {d.failed > 0 && <rect x={cx + 1} y={y(d.failed)} width={bw} height={y(0) - y(d.failed)} rx={2} fill="hsl(var(--destructive))" />}
              {(i % 2 === days.length % 2 || i === days.length - 1) && (
                <text x={cx} y={H - 5} textAnchor="middle" fontSize={11} fill="hsl(var(--muted-foreground))">
                  {i === days.length - 1 ? 'hoy' : fmt(d.day)}
                </text>
              )}
            </g>
          );
        })}
      </svg>
      {hover !== null && (
        <div
          className="absolute top-6 px-3 py-2 bg-popover border border-border rounded-lg shadow-overlay text-sm pointer-events-none whitespace-nowrap"
          style={{ left: `${Math.min(85, Math.max(15, ((pad.l + (hover + 0.5) * slot) / W) * 100))}%`, transform: 'translateX(-50%)' }}
        >
          <p className="font-bold">{fmt(days[hover].day)}</p>
          <p className="tabular-nums">{days[hover].ok} ingresos · {days[hover].failed} fallidos</p>
        </div>
      )}
      <div aria-hidden className="mt-1 flex gap-5 text-sm text-muted-foreground">
        <span className="inline-flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-sm bg-brand" /> Correctos</span>
        <span className="inline-flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-sm bg-destructive" /> Fallidos</span>
      </div>
    </div>
  );
}

interface Attention {
  icon: typeof Lock;
  tone: 'alert' | 'warn' | 'info';
  text: string;
  hint: string;
  action?: { label: string; onClick: () => void };
}

function attentionItems(o: Overview, privacy: DataRequestSummary | null, go: Go, onNewUser: () => void): Attention[] {
  const items: Attention[] = [];
  const plural = (n: number, one: string, many: string) => `${n} ${n === 1 ? one : many}`;
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  if (o.users_locked > 0)
    items.push({
      icon: Lock,
      tone: 'alert',
      text: plural(o.users_locked, 'cuenta bloqueada', 'cuentas bloqueadas'),
      hint: 'Por intentos fallidos. Confirme con la persona antes de desbloquear.',
      action: { label: 'Ver', onClick: () => go('usuarios', { estado: 'bloqueados' }) },
    });
  if (o.security_events_24h > 0)
    items.push({
      icon: ShieldAlert,
      tone: 'alert',
      text: plural(o.security_events_24h, 'alerta de seguridad', 'alertas de seguridad') + ' en 24 h',
      hint: 'Ingresos, cambios de contraseña o firmas que fallaron.',
      action: { label: 'Revisar', onClick: () => go('auditoria', { grupo: 'seguridad', desde: isoDay(yesterday) }) },
    });
  if (o.server_errors_7d > 0)
    items.push({
      icon: ServerCrash,
      tone: 'warn',
      text: plural(o.server_errors_7d, 'error del servidor', 'errores del servidor') + ' en 7 días',
      hint: o.last_server_error_at ? `El último, ${relativeTime(o.last_server_error_at)}.` : '',
      action: { label: 'Ver', onClick: () => go('errores') },
    });
  if (privacy && privacy.overdue > 0)
    items.push({
      icon: FileWarning,
      tone: 'warn',
      text: plural(privacy.overdue, 'solicitud de titular vencida', 'solicitudes de titulares vencidas'),
      hint: 'Superan los 30 días. Las responde el equipo clínico en Privacidad.',
    });
  if (o.users_pending_password > 0)
    items.push({
      icon: KeyRound,
      tone: 'info',
      text: plural(o.users_pending_password, 'persona no ha', 'personas no han') + ' cambiado su contraseña temporal',
      hint: 'Aún no ingresan por primera vez.',
      action: { label: 'Ver', onClick: () => go('usuarios', { estado: 'pendientes' }) },
    });
  if (o.users_idle_30d > 0)
    items.push({
      icon: UserX,
      tone: 'info',
      text: plural(o.users_idle_30d, 'cuenta activa sin uso', 'cuentas activas sin uso') + ' en 30 días',
      hint: 'Si la persona ya no trabaja en el centro, desactívela.',
      action: { label: 'Ver', onClick: () => go('usuarios', { estado: 'sin-uso' }) },
    });
  if (o.admins_active < 2)
    items.push({
      icon: AlertTriangle,
      tone: 'info',
      text: 'Hay un solo administrador activo',
      hint: 'Si pierde el acceso, nadie podrá gestionar las cuentas. Conviene un segundo administrador.',
      action: { label: 'Crear', onClick: onNewUser },
    });
  return items;
}

const TONE: Record<Attention['tone'], string> = {
  alert: 'text-destructive',
  warn: 'text-media',
  info: 'text-info',
};

interface AdminOverviewProps {
  overview: Overview;
  stats: AdminStats | null;
  privacy: DataRequestSummary | null;
  inference: InferenceStatus | null;
  recent: AuditEntry[] | null;
  users: UserAccount[];
  go: Go;
  onOpenUser: (id: number) => void;
  onNewUser: () => void;
}

/** Portada del administrador: estado del sistema, lo que requiere atención, ingresos, actividad y equipo. */
export default function AdminOverview({ overview: o, stats, privacy, inference, recent, users, go, onOpenUser, onNewUser }: AdminOverviewProps) {
  const attention = attentionItems(o, privacy, go, onNewUser);
  const modelOnline = inference?.provider === 'http' && inference.reachable === true;
  const userName = (id: number | null) => (id === null ? null : users.find((u) => u.id === id)?.full_name ?? `Usuario n.º ${id}`);
  const groupCount = (g: AuditGroup) =>
    [...new Set(AUDIT_GROUPS[g].actions as readonly string[])].reduce((a, k) => a + (o.actions_7d[k] ?? 0), 0);

  const status: Array<{ label: string; value: ReactNode; note: ReactNode; onClick?: () => void }> = [
    {
      label: 'Versión instalada',
      value: o.version === 'local' ? 'Local' : o.version.replace(/^sha-/, '').slice(0, 12),
      note: o.version === 'local' ? 'Entorno de desarrollo' : o.version.startsWith('sha-') ? 'Compilación del código' : 'Versión publicada',
    },
    {
      label: 'Modelo de IA',
      value: inference ? (modelOnline ? 'Conectado' : inference.provider === 'http' ? 'Sin conexión' : 'Simulado') : '—',
      note: inference ? (
        modelOnline ? (
          `${inference.model_version ?? ''}${inference.clinically_validated ? '' : ' · prototipo'}`
        ) : (
          <span className="inline-flex items-center gap-1.5">Respaldo <SimulatedBadge /></span>
        )
      ) : (
        'Sin información'
      ),
    },
    {
      label: 'Errores del servidor',
      value: o.server_errors_7d.toLocaleString('es-CL'),
      note: o.last_server_error_at ? `7 días · último ${relativeTime(o.last_server_error_at)}` : '7 días · ninguno',
      onClick: () => go('errores'),
    },
    {
      label: 'Datos',
      value: stats ? `${stats.total_patients.toLocaleString('es-CL')} / ${stats.total_cases.toLocaleString('es-CL')}` : '—',
      note: 'pacientes / casos',
    },
  ];

  return (
    <div className="space-y-6">
      <dl className={cn(cardClass, 'grid grid-cols-2 lg:grid-cols-4 divide-x divide-border')}>
        {status.map(({ label, value, note, onClick }) => {
          const body = (
            <>
              <dt className="text-sm text-muted-foreground">{label}</dt>
              <dd className="mt-1 text-xl font-extrabold tabular-nums truncate">{value}</dd>
              <dd className="text-xs text-muted-foreground">{note}</dd>
            </>
          );
          return onClick ? (
            <button key={label} onClick={onClick} className="flex flex-col items-start justify-start px-6 py-4 text-left hover:bg-accent/60 transition-colors [&:nth-child(3)]:border-l-0 lg:[&:nth-child(3)]:border-l">
              {body}
            </button>
          ) : (
            <div key={label} className="px-6 py-4 min-w-0 [&:nth-child(3)]:border-l-0 lg:[&:nth-child(3)]:border-l">{body}</div>
          );
        })}
      </dl>

      <div className="grid xl:grid-cols-[minmax(0,7fr)_minmax(0,5fr)] gap-6 items-start">
        <div className="space-y-6 min-w-0">
          <Section title="Ingresos de los últimos 14 días">
            <LoginChart days={o.logins_per_day} />
          </Section>
          <section className={cn(cardClass, 'overflow-hidden')} aria-labelledby="ov-recent">
            <div className="px-6 pt-5 pb-3 flex flex-wrap items-baseline justify-between gap-2">
              <h2 id="ov-recent" className={sectionTitle}>Actividad reciente</h2>
              <button className={cn(ghostButton, 'h-8 px-2 -mr-2')} onClick={() => go('auditoria')}>
                Ver la bitácora <ArrowRight aria-hidden className="w-4 h-4" />
              </button>
            </div>
            {recent === null ? (
              <p className="px-6 pb-5 text-sm text-muted-foreground">Cargando…</p>
            ) : recent.length === 0 ? (
              <p className="px-6 pb-5 text-sm text-muted-foreground">Sin registros.</p>
            ) : (
              <ol>
                {recent.map((e) => {
                  const t = describeAudit(e);
                  const alert = SECURITY_ACTIONS.has(e.action);
                  const name = userName(e.user_id);
                  return (
                    <li key={e.id} className="grid grid-cols-[5.5rem_minmax(0,1fr)] gap-3 px-6 py-2.5 border-t border-border text-sm">
                      <time dateTime={e.created_at} className="text-muted-foreground tabular-nums" title={new Date(e.created_at).toLocaleString('es-CL')}>
                        {relativeTime(e.created_at)}
                      </time>
                      <p className="min-w-0">
                        <span className={cn(alert && 'font-semibold text-destructive')}>{t.title}</span>
                        {t.detail && <span className="text-muted-foreground"> · {t.detail}</span>}
                        <span className="block text-xs text-muted-foreground">
                          {name && e.user_id !== null ? (
                            <button className="hover:text-brand hover:underline" onClick={() => onOpenUser(e.user_id!)}>{name}</button>
                          ) : (
                            actorFallback(e)
                          )}
                        </span>
                      </p>
                    </li>
                  );
                })}
              </ol>
            )}
          </section>
        </div>
        {/* En pantallas chicas, lo que requiere atención va primero */}
        <div className="space-y-6 order-first xl:order-none">
          <Section title="Requiere atención">
            {attention.length === 0 ? (
              <p className="flex items-center gap-2 text-sm">
                <CheckCircle2 aria-hidden className="w-5 h-5 text-baja" /> Todo en orden: no hay cuentas ni alertas pendientes.
              </p>
            ) : (
              <ul className="-my-2 divide-y divide-border">
                {attention.map((a) => (
                  <li key={a.text} className="flex items-start gap-3 py-3">
                    <a.icon aria-hidden className={cn('w-5 h-5 mt-0.5 shrink-0', TONE[a.tone])} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-bold">{a.text}</p>
                      {a.hint && <p className="text-sm text-muted-foreground">{a.hint}</p>}
                    </div>
                    {a.action && (
                      <button className={cn(ghostButton, 'h-8 px-2 -mr-2 text-foreground')} onClick={a.action.onClick}>
                        {a.action.label} <ArrowRight aria-hidden className="w-4 h-4" />
                      </button>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </Section>
          <Section title="Equipo" aside={<span className="text-sm text-muted-foreground tabular-nums">{o.users_active} activos de {o.users_total}</span>}>
            <ul className="-my-1">
              {ROLES.map((r) => (
                <li key={r}>
                  <button
                    className="w-full flex items-center justify-between gap-3 rounded-lg px-2 py-2 -mx-2 hover:bg-accent/60 transition-colors"
                    onClick={() => go('usuarios', { rol: r })}
                  >
                    <span className="text-sm">{ROLE_LABELS[r]}</span>
                    <span className="font-bold tabular-nums">{o.users_by_role[r] ?? 0}</span>
                  </button>
                </li>
              ))}
            </ul>
            {o.users_total > o.users_active && (
              <button className="mt-2 text-sm text-muted-foreground hover:text-foreground hover:underline" onClick={() => go('usuarios', { estado: 'inactivos' })}>
                {o.users_total - o.users_active} {o.users_total - o.users_active === 1 ? 'desactivado' : 'desactivados'}
              </button>
            )}
          </Section>

          <Section title="Uso en 7 días" aside={<Clock aria-hidden className="w-4 h-4 text-muted-foreground" />}>
            <dl className="-my-1 divide-y divide-border">
              {(['ingresos', 'cambios', 'consultas'] as AuditGroup[]).map((g) => (
                <div key={g} className="flex items-center justify-between gap-3 py-2">
                  <dt className="text-sm">
                    <button className="hover:text-brand hover:underline" onClick={() => go('auditoria', { grupo: g })}>{AUDIT_GROUPS[g].label}</button>
                  </dt>
                  <dd className="font-bold tabular-nums">{groupCount(g).toLocaleString('es-CL')}</dd>
                </div>
              ))}
            </dl>
          </Section>
        </div>
      </div>
    </div>
  );
}
