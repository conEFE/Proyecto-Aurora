import { useCallback, useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { AlertTriangle, ChevronLeft, ChevronRight, Download, ScrollText } from 'lucide-react';
import { apiClient } from '../../services/api';
import type { AuditEntry, Page, UserAccount } from '../../types';
import { cn } from '../../lib/cn';
import { AUDIT_GROUPS, SECURITY_ACTIONS, actorFallback, describeAudit, relativeTime, type AuditGroup } from '../../utils/audit';
import { EmptyState, ErrorMessage, Loading } from '../Feedback';
import { Segmented } from '../PageHeader';
import { cardClass, formatDateTime, inputClass, secondaryButton, tdClass, thClass } from '../ui';

const SIZE = 25;
const GROUP_KEYS = Object.keys(AUDIT_GROUPS) as AuditGroup[];

function csvCell(v: string): string {
  return /[",\n;]/.test(v) ? `"${v.replace(/"/g, '""')}"` : v;
}

interface AuditLogProps {
  users: UserAccount[];
  onOpenUser: (id: number) => void;
}

/** Bitácora de auditoría legible, con filtros en la dirección y descarga en CSV. */
export default function AuditLog({ users, onOpenUser }: AuditLogProps) {
  const [params, setParams] = useSearchParams();
  const rawGroup = params.get('grupo');
  const group = (GROUP_KEYS as string[]).includes(rawGroup ?? '') ? (rawGroup as AuditGroup) : null;
  const userId = params.get('usuario') ?? '';
  const from = params.get('desde') ?? '';
  const to = params.get('hasta') ?? '';
  const page = Math.max(1, Number(params.get('pagina')) || 1);
  const [data, setData] = useState<Page<AuditEntry> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);

  const setParam = (changes: Record<string, string | null>, resetPage = true) => {
    const next = new URLSearchParams(params);
    for (const [k, v] of Object.entries(changes)) {
      if (v) next.set(k, v);
      else next.delete(k);
    }
    if (resetPage) next.delete('pagina');
    setParams(next, { replace: true });
  };

  const filters = useCallback(
    () => ({
      action: group ? AUDIT_GROUPS[group].actions.join(',') : undefined,
      user_id: userId ? Number(userId) : undefined,
      from: from ? `${from}T00:00:00` : undefined,
      to: to ? `${to}T23:59:59` : undefined,
    }),
    [group, userId, from, to],
  );

  useEffect(() => {
    let active = true;
    setData(null);
    apiClient.listAudit({ ...filters(), page, size: SIZE }).then((r) => {
      if (!active) return;
      if (r.data) {
        setData(r.data);
        setError(null);
      } else setError(r.error || 'No se pudo cargar la bitácora.');
    });
    return () => {
      active = false;
    };
  }, [filters, page]);

  const userName = (id: number | null) => (id === null ? null : users.find((u) => u.id === id)?.full_name ?? `Usuario n.º ${id}`);
  const totalPages = data ? Math.max(1, Math.ceil(data.total / SIZE)) : 1;

  // Descarga lo filtrado (hasta 2.000 registros) con el texto legible y el código de cada acción
  const exportCsv = async () => {
    setExporting(true);
    const rows: AuditEntry[] = [];
    for (let p = 1; p <= 10; p++) {
      const r = await apiClient.listAudit({ ...filters(), page: p, size: 200 });
      if (!r.data) {
        setError(r.error || 'No se pudo descargar la bitácora.');
        setExporting(false);
        return;
      }
      rows.push(...r.data.items);
      if (rows.length >= r.data.total) break;
    }
    const header = ['Fecha', 'Usuario', 'Acción', 'Detalle', 'Código', 'Entidad', 'Id', 'IP'];
    const lines = rows.map((e) => {
      const t = describeAudit(e);
      return [
        new Date(e.created_at).toLocaleString('es-CL'),
        userName(e.user_id) ?? actorFallback(e),
        t.title,
        t.detail ?? '',
        e.action,
        e.entity,
        e.entity_id === null ? '' : String(e.entity_id),
        e.ip_address ?? '',
      ]
        .map(csvCell)
        .join(';');
    });
    const blob = new Blob(['﻿' + [header.join(';'), ...lines].join('\n')], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bitacora-aurora-care-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    setExporting(false);
  };

  return (
    <>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Segmented
          label="Tipo de registro"
          value={group ?? 'todo'}
          onChange={(v) => setParam({ grupo: v === 'todo' ? null : v })}
          options={[{ value: 'todo', label: 'Todo' }, ...GROUP_KEYS.map((g) => ({ value: g, label: AUDIT_GROUPS[g].label }))]}
        />
        <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
          <label htmlFor="a-user" className="sr-only">Usuario</label>
          <select id="a-user" className={cn(inputClass, 'h-9 w-48')} value={userId} onChange={(e) => setParam({ usuario: e.target.value || null })}>
            <option value="">Todos los usuarios</option>
            {users.map((u) => <option key={u.id} value={u.id}>{u.full_name}</option>)}
          </select>
          <label htmlFor="a-from" className="sr-only">Desde</label>
          <input id="a-from" type="date" className={cn(inputClass, 'h-9 w-40')} value={from} max={to || undefined}
            onChange={(e) => setParam({ desde: e.target.value || null })} />
          a
          <label htmlFor="a-to" className="sr-only">Hasta</label>
          <input id="a-to" type="date" className={cn(inputClass, 'h-9 w-40')} value={to} min={from || undefined}
            onChange={(e) => setParam({ hasta: e.target.value || null })} />
        </div>
      </div>

      <ErrorMessage className="mt-4">{error}</ErrorMessage>

      <section aria-label="Bitácora de auditoría" className={cn(cardClass, 'mt-4 overflow-hidden')}>
        {data === null ? (
          <Loading label="Cargando bitácora…" />
        ) : data.items.length === 0 ? (
          <EmptyState title="Sin registros" icon={<ScrollText aria-hidden className="w-8 h-8" />}>
            No hay registros con estos filtros.
          </EmptyState>
        ) : (
          <div className="relative overflow-x-auto">
            <table className="w-full">
              <caption className="sr-only">Registros de auditoría, del más reciente al más antiguo</caption>
              <thead className="bg-muted/60">
                <tr>
                  <th scope="col" className={cn(thClass, 'pl-5')}>Cuándo</th>
                  <th scope="col" className={thClass}>Usuario</th>
                  <th scope="col" className={thClass}>Acción</th>
                  <th scope="col" className={thClass}>Detalle</th>
                  <th scope="col" className={cn(thClass, 'pr-5')}>IP</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((e) => {
                  const t = describeAudit(e);
                  const alert = SECURITY_ACTIONS.has(e.action);
                  const name = userName(e.user_id);
                  return (
                    <tr key={e.id} className={cn(alert && 'bg-destructive/5')}>
                      <td className={cn(tdClass, 'pl-5')}>
                        <time dateTime={e.created_at} title={formatDateTime(e.created_at)} className="block tabular-nums">
                          {relativeTime(e.created_at)}
                        </time>
                        <span className="block text-xs text-muted-foreground tabular-nums">{formatDateTime(e.created_at)}</span>
                      </td>
                      <td className={tdClass}>
                        {name && e.user_id !== null ? (
                          <button className="font-semibold hover:text-brand hover:underline text-left" onClick={() => onOpenUser(e.user_id!)}>
                            {name}
                          </button>
                        ) : (
                          <span className="text-muted-foreground">{actorFallback(e)}</span>
                        )}
                      </td>
                      <td className={cn(tdClass, alert && 'font-semibold text-destructive')}>
                        <span className="inline-flex items-center gap-1.5">
                          {alert && <AlertTriangle aria-hidden className="w-4 h-4" />}
                          {t.title}
                        </span>
                      </td>
                      <td className={cn(tdClass, 'text-muted-foreground whitespace-normal min-w-[12rem]')}>{t.detail || '—'}</td>
                      <td className={cn(tdClass, 'pr-5 text-muted-foreground tabular-nums')}>{e.ip_address ?? '—'}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
        <div className="px-5 py-3 border-t border-border flex flex-wrap items-center justify-between gap-3">
          <span className="flex items-center gap-3 text-sm text-muted-foreground tabular-nums">
            {data ? `${data.total.toLocaleString('es-CL')} registros` : ''}
            <button className={cn(secondaryButton, 'h-8 px-3')} onClick={exportCsv} disabled={exporting || !data?.total}>
              <Download aria-hidden className="w-4 h-4" /> {exporting ? 'Preparando…' : 'Descargar CSV'}
            </button>
          </span>
          <div className="flex items-center gap-3">
            <span className="text-sm text-muted-foreground tabular-nums">Página {page} de {totalPages}</span>
            <button className={secondaryButton} disabled={page <= 1} aria-label="Página anterior"
              onClick={() => setParam({ pagina: page - 1 > 1 ? String(page - 1) : null }, false)}>
              <ChevronLeft aria-hidden className="w-4 h-4" />
            </button>
            <button className={secondaryButton} disabled={page >= totalPages} aria-label="Página siguiente"
              onClick={() => setParam({ pagina: String(page + 1) }, false)}>
              <ChevronRight aria-hidden className="w-4 h-4" />
            </button>
          </div>
        </div>
      </section>
    </>
  );
}
