import { useCallback, useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  AlertTriangle,
  ChevronLeft,
  Download,
  FileText,
  Lock,
  Search,
  ShieldCheck,
  Trash2,
  Unlock,
  Users,
  UserX,
} from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '../services/api';
import { cn } from '../lib/cn';
import type {
  ConsentEvent,
  ConsentText,
  DataRequestStatus,
  DataRequestType,
  DataSubjectRequest,
  Me,
  Patient,
} from '../types';
import { DATA_REQUEST_STATUS_LABELS, DATA_REQUEST_TYPE_LABELS } from '../types';
import { EmptyState, ErrorMessage, Loading, SuccessMessage } from './Feedback';
import { DetailHeader, ListHeader, Segmented } from './PageHeader';
import {
  cardClass,
  dangerButton,
  formatDate,
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

const REQUEST_TYPES = Object.keys(DATA_REQUEST_TYPE_LABELS) as DataRequestType[];
const REQUEST_STATUSES = Object.keys(DATA_REQUEST_STATUS_LABELS) as DataRequestStatus[];

const STATUS_STYLE: Record<DataRequestStatus, string> = {
  RECIBIDA: 'bg-info/10 text-info',
  EN_PROCESO: 'bg-media/10 text-media',
  RESUELTA: 'bg-baja/10 text-baja',
  RECHAZADA: 'bg-secondary text-muted-foreground',
};

function StatusBadge({ status }: { status: DataRequestStatus }) {
  return (
    <span className={`px-1.5 py-0.5 rounded text-xs font-semibold ${STATUS_STYLE[status]}`}>
      {DATA_REQUEST_STATUS_LABELS[status]}
    </span>
  );
}

/** Avanza el estado de una solicitud; resolver o rechazar exige una respuesta. */
function RequestActions({ req, onChanged }: { req: DataSubjectRequest; onChanged: (error?: string) => void }) {
  const [closing, setClosing] = useState<'RESUELTA' | 'RECHAZADA' | null>(null);
  const [resolution, setResolution] = useState('');
  const [saving, setSaving] = useState(false);
  const open = req.status === 'RECIBIDA' || req.status === 'EN_PROCESO';

  const update = async (status: DataRequestStatus, text?: string) => {
    setSaving(true);
    const r = await apiClient.updateDataRequest(req.id, { status, resolution: text });
    setSaving(false);
    setClosing(null);
    setResolution('');
    onChanged(r.error);
  };

  if (!open) {
    return <span className="text-xs text-muted-foreground whitespace-normal">{req.resolution}</span>;
  }
  if (closing) {
    return (
      <div className="flex flex-col gap-1 min-w-[220px]">
        <textarea
          className={inputClass}
          rows={2}
          value={resolution}
          onChange={(e) => setResolution(e.target.value)}
          placeholder={closing === 'RESUELTA' ? 'Cómo se resolvió' : 'Motivo del rechazo'}
          aria-label="Respuesta a la solicitud"
        />
        <div className="flex gap-1">
          <button
            className={primaryButton}
            disabled={saving || resolution.trim().length < 5}
            onClick={() => update(closing, resolution.trim())}
          >
            Guardar
          </button>
          <button className={secondaryButton} onClick={() => setClosing(null)}>
            Cancelar
          </button>
        </div>
      </div>
    );
  }
  return (
    <div className="flex flex-wrap gap-1">
      {req.status === 'RECIBIDA' && (
        <button className={secondaryButton} disabled={saving} onClick={() => update('EN_PROCESO')}>
          En proceso
        </button>
      )}
      <button className={secondaryButton} onClick={() => setClosing('RESUELTA')}>
        Resolver
      </button>
      <button className={secondaryButton} onClick={() => setClosing('RECHAZADA')}>
        Rechazar
      </button>
    </div>
  );
}

function RequestsTable({
  requests,
  showPatient,
  onOpenPatient,
  onChanged,
}: {
  requests: DataSubjectRequest[];
  showPatient: boolean;
  onOpenPatient?: (patientId: number) => void;
  onChanged: (error?: string) => void;
}) {
  if (requests.length === 0) {
    return (
      <EmptyState title="Sin solicitudes" icon={<FileText aria-hidden className="w-8 h-8" />}>
        {showPatient ? 'No hay solicitudes con estos filtros.' : 'Este paciente no tiene solicitudes.'}
      </EmptyState>
    );
  }
  return (
    <div className="relative overflow-x-auto">
      <table className="w-full">
        <caption className="sr-only">Solicitudes de los titulares</caption>
        <thead className="bg-muted/60">
          <tr>
            {showPatient && <th scope="col" className={cn(thClass, 'pl-5')}>Paciente</th>}
            <th scope="col" className={cn(thClass, !showPatient && 'pl-5')}>Tipo</th>
            <th scope="col" className={thClass}>Estado</th>
            <th scope="col" className={thClass}>Recibida</th>
            <th scope="col" className={thClass}>Vence</th>
            <th scope="col" className={thClass}>Detalle</th>
            <th scope="col" className={cn(thClass, 'pr-5')}>Respuesta</th>
          </tr>
        </thead>
        <tbody>
          {requests.map((r) => (
            <tr key={r.id} className="align-top">
              {showPatient && (
                <td className={cn(tdClass, 'pl-5')}>
                  <button
                    className="font-semibold hover:text-brand hover:underline text-left"
                    onClick={() => onOpenPatient?.(r.patient_id)}
                  >
                    {r.patient_name}
                  </button>
                  <span className="block text-xs text-muted-foreground tabular-nums">{r.patient_rut}</span>
                </td>
              )}
              <td className={cn(tdClass, !showPatient && 'pl-5')}>{DATA_REQUEST_TYPE_LABELS[r.request_type]}</td>
              <td className={tdClass}><StatusBadge status={r.status} /></td>
              <td className={cn(tdClass, 'text-muted-foreground tabular-nums')}>{formatDate(r.received_at)}</td>
              <td className={cn(tdClass, 'tabular-nums')}>
                <span className={r.overdue ? 'text-alta font-semibold' : 'text-muted-foreground'}>
                  {formatDate(r.due_at)}
                  {r.overdue && ' · vencida'}
                </span>
              </td>
              <td className={cn(tdClass, 'text-muted-foreground max-w-xs whitespace-normal')}>{r.detail ?? '—'}</td>
              <td className={cn(tdClass, 'pr-5')}><RequestActions req={r} onChanged={onChanged} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

type View = 'solicitudes' | 'pacientes';

function RequestsView({ onOpenPatient }: { onOpenPatient: (id: number) => void }) {
  const [params, setParams] = useSearchParams();
  const status = (params.get('estado') ?? '') as DataRequestStatus | '';
  const overdue = params.get('vencidas') === '1';
  const [requests, setRequests] = useState<DataSubjectRequest[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const setFilter = (key: string, value: string | null) => {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    setParams(next, { replace: true });
  };

  const load = useCallback(async () => {
    const r = await apiClient.listDataRequests({ status: status || undefined, overdue });
    if (r.data) {
      setRequests(r.data);
      setError(null);
    } else setError(r.error || 'No se pudieron cargar las solicitudes');
  }, [status, overdue]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <>
      <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
        <Segmented
          label="Filtrar por estado"
          value={status || 'TODAS'}
          onChange={(v) => setFilter('estado', v === 'TODAS' ? null : v)}
          options={[
            { value: 'TODAS', label: 'Todas' },
            ...REQUEST_STATUSES.map((st) => ({ value: st, label: DATA_REQUEST_STATUS_LABELS[st] })),
          ]}
        />
        <label className="flex items-center gap-2 text-sm text-muted-foreground">
          <input type="checkbox" checked={overdue} onChange={(e) => setFilter('vencidas', e.target.checked ? '1' : null)} />
          Solo vencidas (más de 30 días)
        </label>
      </div>
      <ErrorMessage className="mt-4">{error}</ErrorMessage>
      <div className={cn(cardClass, 'mt-4 overflow-hidden')}>
        {requests === null ? (
          <Loading label="Cargando solicitudes…" />
        ) : (
          <RequestsTable
            requests={requests}
            showPatient
            onOpenPatient={onOpenPatient}
            onChanged={(err) => { if (err) setError(err); load(); }}
          />
        )}
      </div>
    </>
  );
}

function ConsentState({ p }: { p: Patient }) {
  if (p.blocked_at) return <span className="text-sm font-semibold text-alta">Datos bloqueados</span>;
  if (!p.consent_given) return <span className="text-sm font-semibold text-media">Sin consentimiento</span>;
  return <span className="text-sm text-baja">Consentimiento vigente</span>;
}

function PatientsView({ onOpenPatient }: { onOpenPatient: (id: number) => void }) {
  const [params, setParams] = useSearchParams();
  const query = params.get('q') ?? '';
  const [term, setTerm] = useState(query);
  const [results, setResults] = useState<Patient[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setResults(null);
    apiClient.searchPatients(query.trim() || undefined, true).then((r) => {
      if (!active) return;
      if (r.data) {
        setResults(r.data);
        setError(null);
      } else setError(r.error || 'Error al buscar');
    });
    return () => {
      active = false;
    };
  }, [query]);

  return (
    <>
      <form
        className="mt-4 flex gap-2 max-w-xl"
        onSubmit={(e) => {
          e.preventDefault();
          const next = new URLSearchParams(params);
          if (term.trim()) next.set('q', term.trim());
          else next.delete('q');
          setParams(next, { replace: true });
        }}
      >
        <label htmlFor="pv-search" className="sr-only">Buscar por RUT o nombre</label>
        <input id="pv-search" type="search" className={inputClass} value={term} onChange={(e) => setTerm(e.target.value)}
          placeholder="Buscar por RUT o nombre (incluye datos bloqueados)" />
        <button type="submit" className={secondaryButton}><Search aria-hidden className="w-4 h-4" /> Buscar</button>
      </form>
      <ErrorMessage className="mt-4">{error}</ErrorMessage>
      <div className={cn(cardClass, 'mt-4 overflow-hidden')}>
        {results === null ? (
          <Loading label="Buscando…" />
        ) : results.length === 0 ? (
          <EmptyState title="Sin resultados" icon={<Users aria-hidden className="w-8 h-8" />}>
            No hay pacientes que coincidan.
          </EmptyState>
        ) : (
          <div className="relative overflow-x-auto">
            <table className="w-full">
              <caption className="sr-only">Pacientes</caption>
              <thead className="bg-muted/60">
                <tr>
                  <th scope="col" className={cn(thClass, 'pl-5')}>Paciente</th>
                  <th scope="col" className={thClass}>RUT</th>
                  <th scope="col" className={thClass}>Estado</th>
                  <th scope="col" className={cn(thClass, 'pr-5')}>Texto aceptado</th>
                </tr>
              </thead>
              <tbody>
                {results.map((p) => (
                  <tr key={p.id} onClick={() => onOpenPatient(p.id)} className="cursor-pointer hover:bg-accent/60 transition-colors">
                    <td className={cn(tdClass, 'pl-5')}>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onOpenPatient(p.id);
                        }}
                        className="font-semibold hover:text-brand hover:underline text-left"
                      >
                        {p.first_name} {p.last_name}
                      </button>
                    </td>
                    <td className={cn(tdClass, 'text-muted-foreground tabular-nums')}>{p.rut}</td>
                    <td className={tdClass}><ConsentState p={p} /></td>
                    <td className={cn(tdClass, 'pr-5 text-muted-foreground tabular-nums')}>
                      {p.consent_given ? p.consent_text_version ?? 'Sin versión' : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
}

function downloadJson(data: unknown, filename: string) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function PatientPrivacy({
  patient,
  me,
  onBack,
  onChanged,
  onDeleted,
}: {
  patient: Patient;
  me: Me;
  onBack: () => void;
  onChanged: (p: Patient) => void;
  onDeleted: (id: number) => void;
}) {
  const [events, setEvents] = useState<ConsentEvent[]>([]);
  const [requests, setRequests] = useState<DataSubjectRequest[]>([]);
  const [activeText, setActiveText] = useState<ConsentText | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [action, setAction] = useState<'withdraw' | 'grant' | 'block' | 'request' | 'delete' | null>(null);
  const [reason, setReason] = useState('');
  const [confirmed, setConfirmed] = useState(false);
  const [reqType, setReqType] = useState<DataRequestType>('ACCESO');
  const [reqDate, setReqDate] = useState('');
  const [busy, setBusy] = useState(false);
  const blocked = !!patient.blocked_at;
  const outdatedConsent =
    patient.consent_given && activeText !== null && patient.consent_text_version !== activeText.version;

  const load = useCallback(async () => {
    const [e, r, t] = await Promise.all([
      apiClient.consentEvents(patient.id),
      apiClient.listDataRequests({ patient_id: patient.id }),
      apiClient.getConsentText(),
    ]);
    if (e.data) setEvents(e.data);
    if (r.data) setRequests(r.data);
    if (t.data) setActiveText(t.data);
    setError(e.error || r.error || t.error || null);
  }, [patient.id]);

  useEffect(() => {
    load();
  }, [load]);

  const reset = () => {
    setAction(null);
    setReason('');
    setConfirmed(false);
    setReqDate('');
  };

  const run = async (fn: () => Promise<{ data?: Patient; error?: string }>, ok: string) => {
    setBusy(true);
    setError(null);
    const r = await fn();
    setBusy(false);
    if (r.data) {
      onChanged(r.data);
      setNotice(ok);
      reset();
      load();
    } else setError(r.error || 'No se pudo completar la acción');
  };

  const remove = async () => {
    setBusy(true);
    setError(null);
    const r = await apiClient.deletePatient(patient.id);
    setBusy(false);
    if (r.error) setError(r.error);
    else onDeleted(patient.id);
  };

  const submitRequest = async () => {
    setBusy(true);
    const r = await apiClient.createDataRequest(patient.id, {
      request_type: reqType,
      detail: reason.trim() || undefined,
      received_at: reqDate ? `${reqDate}T12:00:00` : undefined,
    });
    setBusy(false);
    if (r.data) {
      setNotice('Solicitud registrada. Vence el ' + formatDate(r.data.due_at) + '.');
      reset();
      load();
    } else setError(r.error || 'No se pudo registrar la solicitud');
  };

  const exportData = async () => {
    setBusy(true);
    const r = await apiClient.exportPatient(patient.id);
    setBusy(false);
    if (r.data) {
      downloadJson(r.data, `aurora-paciente-${patient.id}-${new Date().toISOString().slice(0, 10)}.json`);
      setNotice('Copia de los datos descargada (queda registrada en la auditoría).');
    } else setError(r.error || 'No se pudo exportar');
  };

  return (
    <div className="space-y-6">
      <DetailHeader
        backLabel="Privacidad"
        onBack={onBack}
        title={<>{patient.first_name} {patient.last_name}</>}
        status={<ConsentState p={patient} />}
        meta={
          <>
            RUT {patient.rut}
            {patient.consent_given && ` · texto ${patient.consent_text_version ?? 'sin versión'}`}
            {blocked && ` · bloqueado desde el ${formatDate(patient.blocked_at)}`}
          </>
        }
        actions={
          <>
            {(!patient.consent_given || outdatedConsent) && !blocked && (
              <button className={primaryButton} onClick={() => { reset(); setAction('grant'); }}>
                <ShieldCheck aria-hidden className="w-4 h-4" /> Registrar consentimiento
              </button>
            )}
            <button className={secondaryButton} onClick={() => { reset(); setAction('request'); }}>
              <FileText aria-hidden className="w-4 h-4" /> Registrar solicitud
            </button>
          </>
        }
      />

      <ErrorMessage>{error}</ErrorMessage>
      <SuccessMessage>{notice}</SuccessMessage>
      {outdatedConsent && (
        <div className="flex items-start gap-2 px-3 py-2.5 bg-media/10 border border-media/30 rounded-lg text-sm">
          <AlertTriangle aria-hidden className="w-4 h-4 mt-0.5 shrink-0 text-media" />
          El consentimiento se registró con otra versión del texto. Conviene mostrarle el texto vigente.
        </div>
      )}

      <div className="grid xl:grid-cols-[minmax(0,7fr)_minmax(0,5fr)] gap-6 items-start">
        <div className="space-y-6 min-w-0">
        {action === 'delete' && (
          <div className={cn(cardClass, 'p-6 space-y-3 border-alta/40')}>
            <p className="text-sm text-foreground">
              Solo se elimina un paciente <strong>sin casos</strong> (por ejemplo, registrado por error). Si ya tiene
              casos, su ficha clínica se conserva por la Ley 20.584 y corresponde «Bloquear datos». La eliminación queda
              en la auditoría y no se puede deshacer.
            </p>
            <div className="flex flex-wrap gap-2">
              <button className={dangerButton} disabled={busy} onClick={remove}>
                Eliminar definitivamente
              </button>
              <button className={secondaryButton} onClick={reset}>Cancelar</button>
            </div>
          </div>
        )}

        {action === 'withdraw' && (
          <div className={cn(cardClass, 'p-6 space-y-3')}>
            <p className="text-sm text-foreground">
              El retiro impide registrar casos e imágenes nuevos. Los casos abiertos pueden terminar su revisión y la
              ficha clínica se conserva (Ley 20.584).
            </p>
            <input className={inputClass} value={reason} onChange={(e) => setReason(e.target.value)}
              placeholder="Motivo o canal (opcional)" aria-label="Motivo del retiro" maxLength={500} />
            <div className="flex flex-wrap gap-2">
              <button className={primaryButton} disabled={busy}
                onClick={() => run(() => apiClient.withdrawConsent(patient.id, reason.trim()), 'Consentimiento retirado.')}>
                Confirmar retiro
              </button>
              <button className={secondaryButton} onClick={reset}>Cancelar</button>
            </div>
          </div>
        )}

        {action === 'grant' && activeText && (
          <div className={cn(cardClass, 'p-6 space-y-3')}>
            <p className="text-sm font-bold text-foreground">Texto vigente · versión {activeText.version}</p>
            <div className="max-h-64 overflow-y-auto whitespace-pre-line rounded-lg border border-border bg-background p-3 text-sm leading-relaxed text-muted-foreground" tabIndex={0}>
              {activeText.body}
            </div>
            <label className="flex items-start gap-2 text-sm text-foreground">
              <input type="checkbox" className="mt-0.5" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)} />
              Declaro que mostré o leí este texto al paciente y que autorizó el tratamiento de sus datos.
            </label>
            <div className="flex flex-wrap gap-2">
              <button className={primaryButton} disabled={busy || !confirmed}
                onClick={() => run(() => apiClient.grantConsent(patient.id, activeText.version), 'Consentimiento registrado.')}>
                Registrar
              </button>
              <button className={secondaryButton} onClick={reset}>Cancelar</button>
            </div>
          </div>
        )}

        {action === 'block' && (
          <div className={cn(cardClass, 'p-6 space-y-3')}>
            <p className="text-sm text-foreground">
              El bloqueo reemplaza a la supresión mientras la ley obligue a conservar la ficha: los datos se guardan, pero
              no se pueden editar, no aparecen en las búsquedas y no se crean casos nuevos. Exige que sus casos estén
              cerrados.
            </p>
            <input className={inputClass} value={reason} onChange={(e) => setReason(e.target.value)}
              placeholder="Motivo (obligatorio), p. ej. solicitud de supresión" aria-label="Motivo del bloqueo" maxLength={500} />
            <div className="flex flex-wrap gap-2">
              <button className={primaryButton} disabled={busy || reason.trim().length < 5}
                onClick={() => run(() => apiClient.blockPatient(patient.id, reason.trim()), 'Datos bloqueados.')}>
                Bloquear
              </button>
              <button className={secondaryButton} onClick={reset}>Cancelar</button>
            </div>
          </div>
        )}

        {action === 'request' && (
          <div className={cn(cardClass, 'p-6 space-y-3')}>
            <div className="grid sm:grid-cols-3 gap-2">
              <div>
                <label className={labelClass} htmlFor="pr-type">Tipo</label>
                <select id="pr-type" className={inputClass} value={reqType} onChange={(e) => setReqType(e.target.value as DataRequestType)}>
                  {REQUEST_TYPES.map((t) => <option key={t} value={t}>{DATA_REQUEST_TYPE_LABELS[t]}</option>)}
                </select>
              </div>
              <div>
                <label className={labelClass} htmlFor="pr-date">Recibida el (opcional)</label>
                <input id="pr-date" type="date" className={inputClass} value={reqDate} max={new Date().toISOString().slice(0, 10)}
                  onChange={(e) => setReqDate(e.target.value)} />
              </div>
            </div>
            <textarea className={inputClass} rows={2} value={reason} onChange={(e) => setReason(e.target.value)}
              placeholder="Detalle de la solicitud" aria-label="Detalle de la solicitud" maxLength={1000} />
            <div className="flex flex-wrap gap-2">
              <button className={primaryButton} disabled={busy} onClick={submitRequest}>Registrar solicitud</button>
              <button className={secondaryButton} onClick={reset}>Cancelar</button>
            </div>
          </div>
        )}

          <section className={cn(cardClass, 'overflow-hidden')} aria-labelledby="pp-requests">
            <h2 id="pp-requests" className={cn(sectionTitle, 'px-6 pt-5 pb-3')}>Solicitudes{` (${requests.length})`}</h2>
            <RequestsTable requests={requests} showPatient={false} onChanged={(err) => { if (err) setError(err); load(); }} />
          </section>

          <section className={cn(cardClass, 'p-6 space-y-4')} aria-labelledby="pp-actions">
            <h2 id="pp-actions" className={sectionTitle}>Datos del paciente</h2>
            <div className="flex flex-wrap gap-2">
              {patient.consent_given && !blocked && (
                <button className={secondaryButton} onClick={() => { reset(); setAction('withdraw'); }}>
                  <UserX aria-hidden className="w-4 h-4" /> Retirar consentimiento
                </button>
              )}
              {blocked ? (
                <button className={secondaryButton} disabled={busy}
                  onClick={() => run(() => apiClient.unblockPatient(patient.id), 'Bloqueo levantado.')}>
                  <Unlock aria-hidden className="w-4 h-4" /> Levantar bloqueo
                </button>
              ) : (
                <button className={secondaryButton} onClick={() => { reset(); setAction('block'); }}>
                  <Lock aria-hidden className="w-4 h-4" /> Bloquear datos
                </button>
              )}
              {me.role === 'MEDICO' && (
                <button className={secondaryButton} disabled={busy} onClick={exportData}>
                  <Download aria-hidden className="w-4 h-4" /> Exportar datos (JSON)
                </button>
              )}
              {!blocked && (
                <button className={secondaryButton} onClick={() => { reset(); setAction('delete'); }}>
                  <Trash2 aria-hidden className="w-4 h-4" /> Eliminar paciente
                </button>
              )}
            </div>
          </section>
        </div>

        <section className={cn(cardClass, 'p-6')} aria-labelledby="pp-consent">
          <h2 id="pp-consent" className={sectionTitle}>Consentimiento</h2>
          {events.length === 0 ? (
            <p className="mt-3 text-sm text-muted-foreground">Sin registros.</p>
          ) : (
            <ol className="mt-4 relative border-l border-border ml-3">
              {events.map((e) => {
                const granted = e.action === 'OTORGADO';
                const Icon = granted ? ShieldCheck : UserX;
                return (
                  <li key={e.id} className="relative pl-6 pb-5 last:pb-0">
                    <span className="absolute -left-3 top-0 grid place-items-center w-6 h-6 rounded-full bg-card ring-1 ring-border">
                      <Icon aria-hidden className={cn('w-3.5 h-3.5', granted ? 'text-baja' : 'text-media')} />
                    </span>
                    <p className="text-sm font-bold leading-6">{granted ? 'Consentimiento otorgado' : 'Consentimiento retirado'}</p>
                    <p className="text-sm text-foreground/90">
                      {e.consent_text_version ? `Texto versión ${e.consent_text_version}` : 'Sin versión (registro anterior)'}
                    </p>
                    {e.note && <p className="text-sm text-muted-foreground">{e.note}</p>}
                    <p className="text-xs text-muted-foreground tabular-nums">
                      <time dateTime={e.occurred_at}>{formatDateTime(e.occurred_at)}</time>
                    </p>
                  </li>
                );
              })}
            </ol>
          )}
        </section>
      </div>
    </div>
  );
}

function PatientPage({ me, patientId, onBack }: { me: Me; patientId: number; onBack: () => void }) {
  const [patient, setPatient] = useState<Patient | null>(null);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    let active = true;
    setPatient(null);
    setNotFound(false);
    apiClient.getPatient(patientId).then((r) => {
      if (!active) return;
      if (r.data) setPatient(r.data);
      else setNotFound(true);
    });
    return () => {
      active = false;
    };
  }, [patientId]);

  if (notFound) {
    return (
      <>
        <button className={cn(ghostButton, '-ml-3 mb-4')} onClick={onBack}>
          <ChevronLeft aria-hidden className="w-4 h-4" /> Privacidad
        </button>
        <EmptyState title="No existe la ficha" icon={<Users aria-hidden className="w-8 h-8" />}>
          No hay un paciente con ese número.
        </EmptyState>
      </>
    );
  }
  if (!patient) return <Loading label="Cargando…" />;
  return (
    <PatientPrivacy
      key={patient.id}
      patient={patient}
      me={me}
      onBack={onBack}
      onChanged={setPatient}
      onDeleted={() => {
        toast.success('Paciente eliminado.');
        onBack();
      }}
    />
  );
}

interface PrivacyPanelProps {
  me: Me;
  /** Paciente abierto, tomado de la dirección /privacidad/pacientes/:id */
  patientId?: number | null;
  onOpenPatient: (patientId: number) => void;
  onBack: () => void;
}

export default function PrivacyPanel({ me, patientId = null, onOpenPatient, onBack }: PrivacyPanelProps) {
  const [params, setParams] = useSearchParams();
  const view: View = params.get('vista') === 'pacientes' ? 'pacientes' : 'solicitudes';

  if (patientId !== null) {
    return (
      <div className={pageClass}>
        <PatientPage me={me} patientId={patientId} onBack={onBack} />
      </div>
    );
  }

  return (
    <div className={pageClass}>
      <ListHeader title="Privacidad" />
      <Segmented
        className="mt-6"
        label="Vista"
        value={view}
        onChange={(v) => setParams(v === 'pacientes' ? { vista: 'pacientes' } : {}, { replace: true })}
        options={[
          { value: 'solicitudes', label: <><FileText aria-hidden className="w-4 h-4" /> Solicitudes</> },
          { value: 'pacientes', label: <><ShieldCheck aria-hidden className="w-4 h-4" /> Pacientes</> },
        ]}
      />
      {view === 'solicitudes' ? <RequestsView onOpenPatient={onOpenPatient} /> : <PatientsView onOpenPatient={onOpenPatient} />}
    </div>
  );
}
