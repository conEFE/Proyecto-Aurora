import { useCallback, useEffect, useState } from 'react';
import { AlertTriangle, Download, FileText, Loader2, Lock, Search, ShieldCheck, Trash2, Unlock, UserX } from 'lucide-react';
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
import {
  cardClass,
  errorBox,
  formatDate,
  formatDateTime,
  inputClass,
  pageClass,
  pageSubtitle,
  pageTitle,
  sectionTitle,
  labelClass,
  primaryButton,
  secondaryButton,
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
  onChanged,
}: {
  requests: DataSubjectRequest[];
  showPatient: boolean;
  onChanged: (error?: string) => void;
}) {
  if (requests.length === 0) {
    return <p className="py-4 text-center text-xs text-muted-foreground">No hay solicitudes con estos filtros.</p>;
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-secondary/50 border-b border-border">
          <tr>
            <th className={thClass}>Recibida</th>
            <th className={thClass}>Vence</th>
            {showPatient && <th className={thClass}>Paciente</th>}
            <th className={thClass}>Tipo</th>
            <th className={thClass}>Estado</th>
            <th className={thClass}>Detalle</th>
            <th className={thClass}>Respuesta</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {requests.map((r) => (
            <tr key={r.id}>
              <td className={`${tdClass} text-muted-foreground`}>{formatDate(r.received_at)}</td>
              <td className={tdClass}>
                <span className={r.overdue ? 'text-alta font-semibold' : 'text-muted-foreground'}>
                  {formatDate(r.due_at)}
                  {r.overdue && ' · vencida'}
                </span>
              </td>
              {showPatient && (
                <td className={`${tdClass} text-foreground`}>
                  {r.patient_name}
                  <span className="block text-xs text-muted-foreground">{r.patient_rut}</span>
                </td>
              )}
              <td className={`${tdClass} text-foreground`}>{DATA_REQUEST_TYPE_LABELS[r.request_type]}</td>
              <td className={tdClass}><StatusBadge status={r.status} /></td>
              <td className={`${tdClass} text-muted-foreground max-w-xs whitespace-normal`}>{r.detail ?? '—'}</td>
              <td className={tdClass}><RequestActions req={r} onChanged={onChanged} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function RequestsView() {
  const [status, setStatus] = useState<DataRequestStatus | ''>('');
  const [overdue, setOverdue] = useState(false);
  const [requests, setRequests] = useState<DataSubjectRequest[] | null>(null);
  const [error, setError] = useState<string | null>(null);

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
    <div className={`${cardClass} p-6`}>
      <div className="flex flex-wrap items-end gap-3 mb-3">
        <div>
          <label className={labelClass} htmlFor="rq-status">Estado</label>
          <select id="rq-status" className={inputClass} value={status}
            onChange={(e) => setStatus(e.target.value as DataRequestStatus | '')}>
            <option value="">Todos</option>
            {REQUEST_STATUSES.map((s) => <option key={s} value={s}>{DATA_REQUEST_STATUS_LABELS[s]}</option>)}
          </select>
        </div>
        <label className="flex items-center gap-1.5 text-xs text-foreground pb-2">
          <input type="checkbox" checked={overdue} onChange={(e) => setOverdue(e.target.checked)} />
          Solo con el plazo vencido
        </label>
        <p className="text-xs text-muted-foreground pb-2">
          Plazo legal: 30 días corridos.
        </p>
      </div>
      {error && <div className={errorBox}>{error}</div>}
      {requests === null ? (
        <div className="flex justify-center py-6"><Loader2 className="w-5 h-5 animate-spin text-primary" /></div>
      ) : (
        <RequestsTable requests={requests} showPatient onChanged={(err) => { if (err) setError(err); load(); }} />
      )}
    </div>
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
  onChanged,
  onDeleted,
}: {
  patient: Patient;
  me: Me;
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
    <div className={`${cardClass} p-6 space-y-4`}>
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <h3 className={sectionTitle}>{patient.first_name} {patient.last_name}</h3>
          <p className="text-xs text-muted-foreground">RUT {patient.rut}</p>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {patient.consent_given ? (
            <span className="px-2 py-0.5 rounded text-xs font-semibold bg-baja/10 text-baja">
              Consentimiento vigente{patient.consent_text_version ? ` · ${patient.consent_text_version}` : ' · sin versión'}
            </span>
          ) : (
            <span className="px-2 py-0.5 rounded text-xs font-semibold bg-media/10 text-media">
              Sin consentimiento vigente
            </span>
          )}
          {blocked && (
            <span className="px-2 py-0.5 rounded text-xs font-semibold bg-alta/10 text-alta" title={patient.block_reason ?? ''}>
              Datos bloqueados desde {formatDate(patient.blocked_at)}
            </span>
          )}
        </div>
      </div>

      {error && <div className={errorBox}>{error}</div>}
      {notice && (
        <div className="p-2 bg-baja/10 border border-baja/20 text-baja rounded text-xs">{notice}</div>
      )}
      {outdatedConsent && (
        <div className="p-2 bg-media/10 border border-media/20 text-media rounded text-xs flex gap-1.5">
          <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
          El consentimiento se registró con otra versión del texto. Conviene mostrarle el texto vigente.
        </div>
      )}

      <div className="flex flex-wrap gap-2">
        {patient.consent_given && !blocked && (
          <button className={secondaryButton} onClick={() => { reset(); setAction('withdraw'); }}>
            <UserX className="w-3.5 h-3.5" /> Retirar consentimiento
          </button>
        )}
        {(!patient.consent_given || outdatedConsent) && !blocked && (
          <button className={secondaryButton} onClick={() => { reset(); setAction('grant'); }}>
            <ShieldCheck className="w-3.5 h-3.5" /> Registrar consentimiento
          </button>
        )}
        {blocked ? (
          <button className={secondaryButton} disabled={busy}
            onClick={() => run(() => apiClient.unblockPatient(patient.id), 'Bloqueo levantado.')}>
            <Unlock className="w-3.5 h-3.5" /> Levantar bloqueo
          </button>
        ) : (
          <button className={secondaryButton} onClick={() => { reset(); setAction('block'); }}>
            <Lock className="w-3.5 h-3.5" /> Bloquear datos
          </button>
        )}
        {me.role === 'MEDICO' && (
          <button className={secondaryButton} disabled={busy} onClick={exportData}>
            <Download className="w-3.5 h-3.5" /> Exportar datos (JSON)
          </button>
        )}
        <button className={secondaryButton} onClick={() => { reset(); setAction('request'); }}>
          <FileText className="w-3.5 h-3.5" /> Registrar solicitud
        </button>
        {!blocked && (
          <button className={secondaryButton} onClick={() => { reset(); setAction('delete'); }}>
            <Trash2 className="w-3.5 h-3.5" /> Eliminar paciente
          </button>
        )}
      </div>

      {action === 'delete' && (
        <div className="p-3 border border-alta/30 rounded space-y-2">
          <p className="text-xs text-foreground">
            Solo se elimina un paciente <strong>sin casos</strong> (por ejemplo, registrado por error). Si ya tiene
            casos, su ficha clínica se conserva por la Ley 20.584 y corresponde «Bloquear datos». La eliminación queda
            en la auditoría y no se puede deshacer.
          </p>
          <div className="flex gap-2">
            <button className={primaryButton} disabled={busy} onClick={remove}>
              Eliminar definitivamente
            </button>
            <button className={secondaryButton} onClick={reset}>Cancelar</button>
          </div>
        </div>
      )}

      {action === 'withdraw' && (
        <div className="p-3 border border-border rounded space-y-2">
          <p className="text-xs text-foreground">
            El retiro impide registrar casos e imágenes nuevos. Los casos abiertos pueden terminar su revisión y la
            ficha clínica se conserva (Ley 20.584).
          </p>
          <input className={inputClass} value={reason} onChange={(e) => setReason(e.target.value)}
            placeholder="Motivo o canal (opcional)" aria-label="Motivo del retiro" maxLength={500} />
          <div className="flex gap-2">
            <button className={primaryButton} disabled={busy}
              onClick={() => run(() => apiClient.withdrawConsent(patient.id, reason.trim()), 'Consentimiento retirado.')}>
              Confirmar retiro
            </button>
            <button className={secondaryButton} onClick={reset}>Cancelar</button>
          </div>
        </div>
      )}

      {action === 'grant' && activeText && (
        <div className="p-3 border border-border rounded space-y-2">
          <p className="text-xs font-semibold text-foreground">Texto vigente · versión {activeText.version}</p>
          <div className="max-h-48 overflow-y-auto whitespace-pre-line rounded border border-border bg-background p-2 text-xs leading-relaxed text-muted-foreground" tabIndex={0}>
            {activeText.body}
          </div>
          <label className="flex items-start gap-2 text-xs text-foreground">
            <input type="checkbox" className="mt-0.5" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)} />
            Declaro que mostré o leí este texto al paciente y que autorizó el tratamiento de sus datos.
          </label>
          <div className="flex gap-2">
            <button className={primaryButton} disabled={busy || !confirmed}
              onClick={() => run(() => apiClient.grantConsent(patient.id, activeText.version), 'Consentimiento registrado.')}>
              Registrar
            </button>
            <button className={secondaryButton} onClick={reset}>Cancelar</button>
          </div>
        </div>
      )}

      {action === 'block' && (
        <div className="p-3 border border-border rounded space-y-2">
          <p className="text-xs text-foreground">
            El bloqueo reemplaza a la supresión mientras la ley obligue a conservar la ficha: los datos se guardan, pero
            no se pueden editar, no aparecen en las búsquedas y no se crean casos nuevos. Exige que sus casos estén
            cerrados.
          </p>
          <input className={inputClass} value={reason} onChange={(e) => setReason(e.target.value)}
            placeholder="Motivo (obligatorio), p. ej. solicitud de supresión" aria-label="Motivo del bloqueo" maxLength={500} />
          <div className="flex gap-2">
            <button className={primaryButton} disabled={busy || reason.trim().length < 5}
              onClick={() => run(() => apiClient.blockPatient(patient.id, reason.trim()), 'Datos bloqueados.')}>
              Bloquear
            </button>
            <button className={secondaryButton} onClick={reset}>Cancelar</button>
          </div>
        </div>
      )}

      {action === 'request' && (
        <div className="p-3 border border-border rounded space-y-2">
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
          <div className="flex gap-2">
            <button className={primaryButton} disabled={busy} onClick={submitRequest}>Registrar solicitud</button>
            <button className={secondaryButton} onClick={reset}>Cancelar</button>
          </div>
        </div>
      )}

      <div>
        <h4 className="text-xs font-semibold text-foreground mb-2">Historial del consentimiento</h4>
        {events.length === 0 ? (
          <p className="text-xs text-muted-foreground">Sin registros.</p>
        ) : (
          <table className="w-full">
            <thead className="bg-secondary/50 border-b border-border">
              <tr>
                <th className={thClass}>Fecha</th>
                <th className={thClass}>Acción</th>
                <th className={thClass}>Texto</th>
                <th className={thClass}>Nota</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {events.map((e) => (
                <tr key={e.id}>
                  <td className={`${tdClass} text-muted-foreground`}>{formatDateTime(e.occurred_at)}</td>
                  <td className={tdClass}>
                    <span className={e.action === 'OTORGADO' ? 'text-baja' : 'text-media'}>
                      {e.action === 'OTORGADO' ? 'Otorgado' : 'Retirado'}
                    </span>
                  </td>
                  <td className={`${tdClass} text-muted-foreground`}>{e.consent_text_version ?? 'Sin versión (registro anterior)'}</td>
                  <td className={`${tdClass} text-muted-foreground whitespace-normal`}>{e.note ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div>
        <h4 className="text-xs font-semibold text-foreground mb-2">Solicitudes del paciente</h4>
        <RequestsTable requests={requests} showPatient={false} onChanged={(err) => { if (err) setError(err); load(); }} />
      </div>
    </div>
  );
}

function PatientView({ me }: { me: Me }) {
  const [term, setTerm] = useState('');
  const [results, setResults] = useState<Patient[] | null>(null);
  const [selected, setSelected] = useState<Patient | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const search = async (e: React.FormEvent) => {
    e.preventDefault();
    const r = await apiClient.searchPatients(term.trim() || undefined, true);
    setNotice(null);
    if (r.data) {
      setResults(r.data);
      setError(null);
    } else setError(r.error || 'Error al buscar');
  };

  return (
    <div className="space-y-4">
      <form onSubmit={search} className={`${cardClass} p-6 flex gap-2`}>
        <input className={inputClass} value={term} onChange={(e) => setTerm(e.target.value)}
          placeholder="Buscar paciente por RUT o nombre (incluye datos bloqueados)" aria-label="Buscar paciente" />
        <button type="submit" className={primaryButton}><Search className="w-3.5 h-3.5" /> Buscar</button>
      </form>
      {error && <div className={errorBox}>{error}</div>}
      {notice && (
        <div className="p-2 bg-baja/10 border border-baja/20 text-baja rounded text-xs">{notice}</div>
      )}
      {results && !selected && (
        <div className={`${cardClass} divide-y divide-border`}>
          {results.length === 0 && <p className="p-4 text-xs text-muted-foreground">Sin resultados.</p>}
          {results.map((p) => (
            <button key={p.id} onClick={() => setSelected(p)}
              className="w-full text-left px-4 py-2 hover:bg-accent flex items-center justify-between">
              <span className="text-xs text-foreground">{p.first_name} {p.last_name} · {p.rut}</span>
              <span className="text-xs text-muted-foreground">
                {p.blocked_at ? 'Bloqueado' : p.consent_given ? 'Con consentimiento' : 'Sin consentimiento'}
              </span>
            </button>
          ))}
        </div>
      )}
      {selected && (
        <>
          <button className={secondaryButton} onClick={() => setSelected(null)}>← Volver a los resultados</button>
          <PatientPrivacy
            key={selected.id}
            patient={selected}
            me={me}
            onChanged={setSelected}
            onDeleted={(id) => {
              setSelected(null);
              setResults((prev) => prev?.filter((p) => p.id !== id) ?? null);
              setNotice('Paciente eliminado.');
            }}
          />
        </>
      )}
    </div>
  );
}

export default function PrivacyPanel({ me }: { me: Me }) {
  const [tab, setTab] = useState<'requests' | 'patient'>('requests');
  return (
    <div className={cn(pageClass, "space-y-6")}>
      <div>
        <h1 className={pageTitle}>Privacidad</h1>
        <p className={pageSubtitle}>Consentimiento, bloqueo y solicitudes de los titulares.</p>
      </div>
      <div role="group" aria-label="Vista" className="inline-flex p-1 rounded-lg bg-muted">
        {([['requests', 'Solicitudes', FileText], ['patient', 'Por paciente', ShieldCheck]] as const).map(([id, label, Icon]) => (
          <button
            key={id}
            onClick={() => setTab(id)}
            aria-pressed={tab === id}
            className={cn(
              'inline-flex items-center gap-2 h-9 px-3 rounded-md text-sm transition-colors',
              tab === id ? 'bg-card text-foreground font-bold ring-1 ring-border' : 'text-muted-foreground hover:text-foreground',
            )}
          >
            <Icon aria-hidden className="w-4 h-4" /> {label}
          </button>
        ))}
      </div>
      {tab === 'requests' ? <RequestsView /> : <PatientView me={me} />}
    </div>
  );
}
