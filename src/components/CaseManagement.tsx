import { useCallback, useEffect, useState } from 'react';
import { ChevronLeft, ChevronRight, FolderOpen, Loader2, Plus, X } from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '../services/api';
import type { CaseStatus, CaseSymptoms, ClinicalCase, Me, Page, Patient } from '../types';
import { CASE_STATUS_LABELS } from '../types';
import { cn } from '../lib/cn';
import { LevelBadge, StatusBadge } from './Badges';
import CaseDetail from './CaseDetail';
import { EmptyState, ErrorMessage, Loading } from './Feedback';
import ImageBatchPicker from './ImageBatchPicker';
import { uploadBatch, type PendingImage } from '../utils/imageBatch';
import PatientModal from './PatientModal';
import SymptomsForm from './SymptomsForm';
import {
  cardClass,
  formatDate,
  iconButton,
  inputClass,
  pageClass,
  pageSubtitle,
  pageTitle,
  primaryButton,
  secondaryButton,
  sectionTitle,
  tdClass,
  thClass,
} from './ui';

const EMPTY_SYMPTOMS: CaseSymptoms = {
  palpable_mass: false,
  nipple_discharge: false,
  skin_or_nipple_changes: false,
  birads_reported: null,
};

function NewCaseForm({
  onCreated,
  onCancel,
  initialPatient = null,
}: {
  onCreated: (c: ClinicalCase) => void;
  onCancel: () => void;
  initialPatient?: Patient | null;
}) {
  const [patient, setPatient] = useState<Patient | null>(initialPatient);
  const [symptoms, setSymptoms] = useState<CaseSymptoms>(EMPTY_SYMPTOMS);
  const [images, setImages] = useState<PendingImage[]>([]);
  const [progress, setProgress] = useState<{ index: number; percent: number } | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  // Crea el caso y, si se eligieron imágenes, las sube al mismo caso (un examen = un caso con varias imágenes)
  const submit = async () => {
    if (!patient) return;
    setSaving(true);
    setError(null);
    const r = await apiClient.createCase({ patient_id: patient.id, ...symptoms });
    if (!r.data) {
      setSaving(false);
      setError(r.error || 'No se pudo crear el caso. Revise los datos e intente de nuevo.');
      return;
    }
    let failed: string[] = [];
    if (images.length > 0) {
      setProgress({ index: 0, percent: 0 });
      failed = await uploadBatch(r.data.id, images, (index, percent) => setProgress({ index, percent }));
      setProgress(null);
    }
    setSaving(false);
    const uploaded = images.length - failed.length;
    if (failed.length > 0) toast.error(`No se pudieron subir ${failed.length} imagen(es): ${failed.join('; ')}`);
    toast.success(
      `Caso ${r.data.code} creado${uploaded > 0 ? ` con ${uploaded} ${uploaded === 1 ? 'imagen' : 'imágenes'}` : ''}.`,
    );
    onCreated(r.data);
  };

  return (
    <section aria-labelledby="new-case-title" className={cn(cardClass, 'p-6 space-y-5')}>
      <div className="flex items-center justify-between">
        <h2 id="new-case-title" className={sectionTitle}>Nuevo caso</h2>
        <button onClick={onCancel} aria-label="Cancelar nuevo caso" className={iconButton}>
          <X className="w-5 h-5" />
        </button>
      </div>
      <ErrorMessage>{error}</ErrorMessage>
      <div>
        <p className="text-sm font-medium mb-1.5">Paciente</p>
        {patient ? (
          <div className="flex items-center justify-between gap-3 px-4 py-3 rounded-lg bg-muted border border-border">
            <div className="text-sm">
              <p className="font-bold">{patient.first_name} {patient.last_name}</p>
              <p className="text-muted-foreground tabular-nums">RUT {patient.rut}</p>
              {!patient.consent_given && <p className="text-media font-semibold">Sin consentimiento registrado</p>}
            </div>
            <button className={secondaryButton} onClick={() => setShowModal(true)}>Cambiar</button>
          </div>
        ) : (
          <button className={secondaryButton} onClick={() => setShowModal(true)}>
            Buscar o registrar paciente
          </button>
        )}
      </div>
      <SymptomsForm value={symptoms} onChange={setSymptoms} disabled={saving} />
      <div>
        <p className="text-sm font-medium mb-1.5">Imágenes del examen <span className="text-muted-foreground font-normal">(opcional; también se pueden agregar después)</span></p>
        <ImageBatchPicker
          items={images}
          onChange={setImages}
          onRejected={(msgs) => setError(msgs.length ? `Imágenes no agregadas: ${msgs.join('; ')}` : null)}
          disabled={saving}
          progress={progress}
        />
      </div>
      <button className={cn(primaryButton, 'w-full')} disabled={!patient || saving} onClick={submit}>
        {saving && <Loader2 aria-hidden className="w-4 h-4 animate-spin" />}
        {saving
          ? progress
            ? `Subiendo imagen ${progress.index + 1} de ${images.length}…`
            : 'Creando…'
          : images.length > 0
            ? `Crear caso y subir ${images.length} ${images.length === 1 ? 'imagen' : 'imágenes'}`
            : 'Crear caso'}
      </button>
      <PatientModal isOpen={showModal} onClose={() => setShowModal(false)} onSelectPatient={setPatient} />
    </section>
  );
}

interface CaseManagementProps {
  me: Me;
  initialCaseId?: number | null;
  /** Si viene, se abre «Nuevo caso» con este paciente ya elegido (desde Pacientes) */
  newCasePatient?: Patient | null;
}

export default function CaseManagement({ me, initialCaseId = null, newCasePatient = null }: CaseManagementProps) {
  const [data, setData] = useState<Page<ClinicalCase> | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(initialCaseId);
  const [statusFilter, setStatusFilter] = useState<CaseStatus | ''>('');
  const [page, setPage] = useState(1);
  const [creating, setCreating] = useState(newCasePatient !== null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const size = 15;

  const loadCases = useCallback(async () => {
    setLoading(true);
    const r = await apiClient.getCases({ status: statusFilter || undefined, page, size });
    if (r.data) {
      setData(r.data);
      setError(null);
    } else setError(r.error || 'No se pudieron cargar los casos.');
    setLoading(false);
  }, [statusFilter, page]);

  useEffect(() => {
    loadCases();
  }, [loadCases]);

  const totalPages = data ? Math.max(1, Math.ceil(data.total / size)) : 1;

  // El siguiente caso de la cola queda a una acción de distancia al terminar una revisión
  const openNextCase = async () => {
    const r = await apiClient.getQueue(false);
    const next = r.data?.find((q) => q.case_id && q.case_id !== selectedId);
    if (next?.case_id) setSelectedId(next.case_id);
    else toast('No quedan casos pendientes en la cola.');
  };

  return (
    <div className={pageClass}>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className={pageTitle}>Casos</h1>
          <p className={pageSubtitle}>Cada caso se identifica por un código anónimo. Seleccione uno para ver su detalle.</p>
        </div>
        <button className={primaryButton} onClick={() => setCreating(true)}>
          <Plus aria-hidden className="w-4 h-4" /> Nuevo caso
        </button>
      </div>

      <ErrorMessage className="mt-4">{error}</ErrorMessage>

      <div className="mt-6 grid xl:grid-cols-[minmax(0,31rem)_minmax(0,1fr)] 2xl:grid-cols-[minmax(0,34rem)_minmax(0,1fr)] gap-6 items-start">
        <div className={cn(cardClass, 'overflow-hidden')}>
          <div className="px-4 py-3 border-b border-border flex items-center gap-3">
            <label className="text-sm text-muted-foreground" htmlFor="status-filter">Estado</label>
            <select
              id="status-filter"
              className={cn(inputClass, 'h-9 w-48')}
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
            {data && <span className="ml-auto text-sm text-muted-foreground tabular-nums">{data.total} casos</span>}
          </div>
          {loading ? (
            <Loading label="Cargando casos…" />
          ) : !data || data.items.length === 0 ? (
            <EmptyState title="No hay casos" icon={<FolderOpen aria-hidden className="w-8 h-8" />}>
              {statusFilter ? 'No hay casos en este estado.' : 'Cree el primer caso con «Nuevo caso».'}
            </EmptyState>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <caption className="sr-only">Lista de casos</caption>
                <thead className="bg-muted/60">
                  <tr>
                    <th scope="col" className={thClass}>Código</th>
                    <th scope="col" className={thClass}>Paciente</th>
                    <th scope="col" className={cn(thClass, "hidden 2xl:table-cell")}>Fecha</th>
                    <th scope="col" className={thClass}>Estado</th>
                    <th scope="col" className={thClass}>Triage</th>
                    <th scope="col" className={cn(thClass, "hidden 2xl:table-cell text-right")}>Imág.</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((c) => {
                    const selected = selectedId === c.id && !creating;
                    return (
                      <tr key={c.id} className={cn('transition-colors', selected ? 'bg-accent' : 'hover:bg-accent/60')}>
                        <td className={tdClass}>
                          <button
                            onClick={() => {
                              setCreating(false);
                              setSelectedId(c.id);
                            }}
                            aria-current={selected ? 'true' : undefined}
                            className={cn('font-bold tabular-nums hover:text-brand hover:underline', selected && 'text-brand')}
                          >
                            {c.code}
                          </button>
                        </td>
                        <td className={cn(tdClass, "text-muted-foreground max-w-[9rem] truncate")}>
                          {c.patient ? `${c.patient.first_name} ${c.patient.last_name}` : '—'}
                        </td>
                        <td className={cn(tdClass, "hidden 2xl:table-cell text-muted-foreground tabular-nums")}>{formatDate(c.created_at)}</td>
                        <td className={tdClass}><StatusBadge status={c.status} /></td>
                        <td className={tdClass}><LevelBadge level={c.triage_level} /></td>
                        <td className={cn(tdClass, "hidden 2xl:table-cell text-right tabular-nums text-muted-foreground")}>{c.image_count}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
          <div className="px-4 py-3 border-t border-border flex items-center justify-between">
            <button className={secondaryButton} disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
              <ChevronLeft aria-hidden className="w-4 h-4" /> Anterior
            </button>
            <span className="text-sm text-muted-foreground tabular-nums">Página {page} de {totalPages}</span>
            <button className={secondaryButton} disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
              Siguiente <ChevronRight aria-hidden className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="min-w-0">
          {creating ? (
            <NewCaseForm
              initialPatient={newCasePatient}
              onCancel={() => setCreating(false)}
              onCreated={(c) => {
                setCreating(false);
                setSelectedId(c.id);
                loadCases();
              }}
            />
          ) : selectedId ? (
            <CaseDetail
              key={selectedId}
              caseId={selectedId}
              me={me}
              onChanged={loadCases}
              onNextCase={me.role === 'MEDICO' ? openNextCase : undefined}
            />
          ) : (
            <div className={cn(cardClass, 'border-dashed')}>
              <EmptyState title="Ningún caso seleccionado">Elija un caso de la lista para ver su detalle.</EmptyState>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
