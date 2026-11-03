import { useCallback, useEffect, useState } from 'react';
import { Eye, FolderOpen, Loader2, Plus, X } from 'lucide-react';
import { apiClient } from '../services/api';
import type { CaseStatus, CaseSymptoms, ClinicalCase, Me, Page, Patient } from '../types';
import { CASE_STATUS_LABELS } from '../types';
import { LevelBadge, StatusBadge } from './Badges';
import CaseDetail from './CaseDetail';
import PatientModal from './PatientModal';
import SymptomsForm from './SymptomsForm';
import {
  cardClass,
  errorBox,
  formatDate,
  inputClass,
  primaryButton,
  secondaryButton,
  tdClass,
  thClass,
} from './ui';

const EMPTY_SYMPTOMS: CaseSymptoms = {
  palpable_mass: false,
  nipple_discharge: false,
  skin_or_nipple_changes: false,
  birads_reported: null,
};

function NewCaseForm({ onCreated, onCancel }: { onCreated: (c: ClinicalCase) => void; onCancel: () => void }) {
  const [patient, setPatient] = useState<Patient | null>(null);
  const [symptoms, setSymptoms] = useState<CaseSymptoms>(EMPTY_SYMPTOMS);
  const [showModal, setShowModal] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const submit = async () => {
    if (!patient) return;
    setSaving(true);
    const r = await apiClient.createCase({ patient_id: patient.id, ...symptoms });
    setSaving(false);
    if (r.data) onCreated(r.data);
    else setError(r.error || 'No se pudo crear el caso');
  };

  return (
    <div className={`${cardClass} p-4 space-y-3`}>
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-foreground">Nuevo caso</h3>
        <button onClick={onCancel} aria-label="Cerrar" className="text-muted-foreground hover:text-foreground">
          <X className="w-4 h-4" />
        </button>
      </div>
      {error && <div className={errorBox}>{error}</div>}
      <div>
        {patient ? (
          <div className="p-2 bg-primary/10 border border-primary/20 rounded text-xs flex justify-between items-center">
            <span>
              <strong>{patient.first_name} {patient.last_name}</strong> · RUT {patient.rut}
              {!patient.consent_given && <span className="ml-2 text-orange-400">(sin consentimiento)</span>}
            </span>
            <button className="text-[10px] text-primary" onClick={() => setShowModal(true)}>Cambiar</button>
          </div>
        ) : (
          <button className={secondaryButton} onClick={() => setShowModal(true)}>
            Seleccionar o registrar paciente
          </button>
        )}
      </div>
      <SymptomsForm value={symptoms} onChange={setSymptoms} />
      <button className={`${primaryButton} w-full`} disabled={!patient || saving} onClick={submit}>
        {saving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Crear caso'}
      </button>
      <PatientModal isOpen={showModal} onClose={() => setShowModal(false)} onSelectPatient={setPatient} />
    </div>
  );
}

interface CaseManagementProps {
  me: Me;
  initialCaseId?: number | null;
}

export default function CaseManagement({ me, initialCaseId = null }: CaseManagementProps) {
  const [data, setData] = useState<Page<ClinicalCase> | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(initialCaseId);
  const [statusFilter, setStatusFilter] = useState<CaseStatus | ''>('');
  const [page, setPage] = useState(1);
  const [creating, setCreating] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const size = 15;

  const loadCases = useCallback(async () => {
    setLoading(true);
    const r = await apiClient.getCases({ status: statusFilter || undefined, page, size });
    if (r.data) {
      setData(r.data);
      setError(null);
    } else setError(r.error || 'Error al cargar casos');
    setLoading(false);
  }, [statusFilter, page]);

  useEffect(() => {
    loadCases();
  }, [loadCases]);

  const totalPages = data ? Math.max(1, Math.ceil(data.total / size)) : 1;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-foreground">Casos clínicos</h2>
          <p className="mt-0.5 text-xs text-muted-foreground">
            Registro de casos, síntomas y BI-RADS. Cada caso queda identificado por un código anónimo.
          </p>
        </div>
        <button className={primaryButton} onClick={() => setCreating(true)}>
          <Plus className="w-3.5 h-3.5" /> Nuevo caso
        </button>
      </div>

      {error && <div className={`${errorBox} mb-3`}>{error}</div>}

      <div className="grid lg:grid-cols-5 gap-4">
        <div className="lg:col-span-3">
          <div className={`${cardClass} overflow-hidden`}>
            <div className="p-3 border-b border-border flex items-center gap-2">
              <label className="text-xs text-muted-foreground" htmlFor="status-filter">Estado</label>
              <select
                id="status-filter"
                className={`${inputClass} max-w-[180px] py-1`}
                value={statusFilter}
                onChange={(e) => {
                  setPage(1);
                  setStatusFilter(e.target.value as CaseStatus | '');
                }}
              >
                <option value="">Todos</option>
                {(Object.keys(CASE_STATUS_LABELS) as CaseStatus[]).map((s) => (
                  <option key={s} value={s}>{CASE_STATUS_LABELS[s]}</option>
                ))}
              </select>
              {data && <span className="ml-auto text-[10px] text-muted-foreground">{data.total} casos</span>}
            </div>
            {loading ? (
              <div className="text-center py-8">
                <Loader2 className="w-6 h-6 mx-auto text-primary animate-spin" />
              </div>
            ) : !data || data.items.length === 0 ? (
              <div className="text-center py-8">
                <FolderOpen className="w-10 h-10 mx-auto mb-2 text-muted-foreground" />
                <p className="text-xs text-muted-foreground">No hay casos registrados</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-secondary/50 border-b border-border">
                    <tr>
                      <th className={thClass}>Código</th>
                      <th className={thClass}>Paciente</th>
                      <th className={thClass}>Fecha</th>
                      <th className={thClass}>Estado</th>
                      <th className={thClass}>Triage</th>
                      <th className={thClass}>Imágenes</th>
                      <th className={thClass}></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {data.items.map((c) => (
                      <tr
                        key={c.id}
                        className={`hover:bg-secondary/30 transition-colors ${selectedId === c.id ? 'bg-primary/5' : ''}`}
                      >
                        <td className={`${tdClass} font-mono text-foreground`}>{c.code}</td>
                        <td className={`${tdClass} text-muted-foreground`}>
                          {c.patient ? `${c.patient.first_name} ${c.patient.last_name}` : '—'}
                        </td>
                        <td className={`${tdClass} text-muted-foreground`}>{formatDate(c.created_at)}</td>
                        <td className={tdClass}><StatusBadge status={c.status} /></td>
                        <td className={tdClass}><LevelBadge level={c.triage_level} /></td>
                        <td className={`${tdClass} text-muted-foreground`}>{c.image_count}</td>
                        <td className={tdClass}>
                          <button
                            onClick={() => {
                              setCreating(false);
                              setSelectedId(c.id);
                            }}
                            className="flex items-center gap-1 text-primary hover:text-primary/80 font-medium text-xs"
                          >
                            <Eye className="w-3.5 h-3.5" /> Ver
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            <div className="px-3 py-2 border-t border-border flex items-center justify-between">
              <button className={secondaryButton} disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>Anterior</button>
              <span className="text-xs text-muted-foreground">Página {page} de {totalPages}</span>
              <button className={secondaryButton} disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>Siguiente</button>
            </div>
          </div>
        </div>

        <div className="lg:col-span-2">
          {creating ? (
            <NewCaseForm
              onCancel={() => setCreating(false)}
              onCreated={(c) => {
                setCreating(false);
                setSelectedId(c.id);
                loadCases();
              }}
            />
          ) : selectedId ? (
            <CaseDetail key={selectedId} caseId={selectedId} me={me} onChanged={loadCases} />
          ) : (
            <div className={`${cardClass} p-4 text-center py-12`}>
              <Eye className="w-10 h-10 mx-auto mb-2 text-muted-foreground" />
              <p className="text-xs text-muted-foreground">Selecciona un caso para ver su detalle</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
