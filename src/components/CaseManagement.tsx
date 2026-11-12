import { useCallback, useEffect, useState } from 'react';
import { ChevronLeft, ChevronRight, FolderOpen, Loader2, Plus, X } from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '../services/api';
import type { CaseStatus, CaseSymptoms, ClinicalCase, Me, Page, Patient, TriageLevel } from '../types';
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
  ghostButton,
  iconButton,
  inputClass,
  pageClass,
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

type LevelFilter = TriageLevel | 'TODOS';
const LEVEL_TABS: LevelFilter[] = ['TODOS', 'ALTA', 'MEDIA', 'BAJA'];

export default function CaseManagement({ me, initialCaseId = null, newCasePatient = null }: CaseManagementProps) {
  const [data, setData] = useState<Page<ClinicalCase> | null>(null);
  const [counts, setCounts] = useState<Record<LevelFilter, number> | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(initialCaseId);
  const [level, setLevel] = useState<LevelFilter>('TODOS');
  const [statusFilter, setStatusFilter] = useState<CaseStatus | ''>('');
  const [page, setPage] = useState(1);
  const [creating, setCreating] = useState(newCasePatient !== null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const size = 20;

  const loadCases = useCallback(async () => {
    setLoading(true);
    const status = statusFilter || undefined;
    const [list, ...totals] = await Promise.all([
      apiClient.getCases({ status, level: level === 'TODOS' ? undefined : level, page, size }),
      ...LEVEL_TABS.map((l) => apiClient.getCases({ status, level: l === 'TODOS' ? undefined : l, page: 1, size: 1 })),
    ]);
    if (list.data) {
      setData(list.data);
      setError(null);
    } else setError(list.error || 'No se pudieron cargar los casos.');
    setCounts(Object.fromEntries(LEVEL_TABS.map((l, i) => [l, totals[i].data?.total ?? 0])) as Record<LevelFilter, number>);
    setLoading(false);
  }, [statusFilter, level, page]);

  useEffect(() => {
    loadCases();
  }, [loadCases]);

  const totalPages = data ? Math.max(1, Math.ceil(data.total / size)) : 1;

  const openCase = (id: number) => {
    setCreating(false);
    setSelectedId(id);
    window.scrollTo(0, 0);
  };

  const backToList = () => {
    setSelectedId(null);
    setCreating(false);
    loadCases();
  };

  // El siguiente caso de la cola queda a una acción de distancia al terminar una revisión
  const openNextCase = async () => {
    const r = await apiClient.getQueue(false);
    const next = r.data?.find((q) => q.case_id && q.case_id !== selectedId);
    if (next?.case_id) openCase(next.case_id);
    else toast('No quedan casos pendientes en la cola.');
  };

  if (creating || selectedId) {
    return (
      <div className={pageClass}>
        <button className={cn(ghostButton, '-ml-3 mb-4')} onClick={backToList}>
          <ChevronLeft aria-hidden className="w-4 h-4" /> Casos
        </button>
        {creating ? (
          <div className="max-w-3xl">
            <NewCaseForm
              initialPatient={newCasePatient}
              onCancel={backToList}
              onCreated={(c) => openCase(c.id)}
            />
          </div>
        ) : (
          <CaseDetail
            key={selectedId}
            caseId={selectedId!}
            me={me}
            onChanged={loadCases}
            onNextCase={me.role === 'MEDICO' ? openNextCase : undefined}
          />
        )}
      </div>
    );
  }

  return (
    <div className={pageClass}>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <h1 className={pageTitle}>Casos</h1>
        <button className={primaryButton} onClick={() => setCreating(true)}>
          <Plus aria-hidden className="w-4 h-4" /> Nuevo caso
        </button>
      </div>

      <ErrorMessage className="mt-4">{error}</ErrorMessage>

      <div className="mt-6 flex flex-wrap items-center justify-between gap-3">
        <div role="tablist" aria-label="Filtrar por nivel de triage" className="inline-flex p-1 rounded-lg bg-muted">
          {LEVEL_TABS.map((l) => {
            const on = level === l;
            return (
              <button
                key={l}
                role="tab"
                aria-selected={on}
                onClick={() => {
                  setPage(1);
                  setLevel(l);
                }}
                className={cn(
                  'inline-flex items-center gap-2 h-8 px-3 rounded-md text-sm transition-colors',
                  on ? 'bg-card text-foreground font-bold ring-1 ring-border' : 'text-muted-foreground hover:text-foreground',
                )}
              >
                {l === 'TODOS' ? 'Todos' : <LevelBadge level={l} />}
                <span className="tabular-nums text-muted-foreground">{counts ? counts[l] : '—'}</span>
              </button>
            );
          })}
        </div>
        <label className="flex items-center gap-2 text-sm text-muted-foreground">
          Estado
          <select
            className={cn(inputClass, 'h-9 w-44')}
            value={statusFilter}
            onChange={(e) => {
              setPage(1);
              setStatusFilter(e.target.value as CaseStatus | '');
            }}
          >
            <option value="">Todos</option>
            {(Object.keys(CASE_STATUS_LABELS) as CaseStatus[]).map((st) => (
              <option key={st} value={st}>{CASE_STATUS_LABELS[st]}</option>
            ))}
          </select>
        </label>
      </div>

      <div className={cn(cardClass, 'mt-4 overflow-hidden')}>
        {loading && !data ? (
          <Loading label="Cargando casos…" />
        ) : !data || data.items.length === 0 ? (
          <EmptyState title="No hay casos" icon={<FolderOpen aria-hidden className="w-8 h-8" />}>
            {level !== 'TODOS' || statusFilter ? 'No hay casos con estos filtros.' : 'Cree el primero con «Nuevo caso».'}
          </EmptyState>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <caption className="sr-only">Lista de casos</caption>
              <thead className="bg-muted/60">
                <tr>
                  <th scope="col" className={cn(thClass, 'pl-5')}>Código</th>
                  <th scope="col" className={thClass}>Nivel</th>
                  <th scope="col" className={thClass}>Paciente</th>
                  <th scope="col" className={thClass}>Estado</th>
                  <th scope="col" className={thClass}>Creado</th>
                  <th scope="col" className={cn(thClass, 'text-right pr-5')}>Imágenes</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((c) => (
                  <tr key={c.id} onClick={() => openCase(c.id)} className="cursor-pointer hover:bg-accent/60 transition-colors">
                    <td className={cn(tdClass, 'pl-5')}>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          openCase(c.id);
                        }}
                        className="font-bold tabular-nums hover:text-brand hover:underline"
                      >
                        {c.code}
                      </button>
                    </td>
                    <td className={tdClass}><LevelBadge level={c.triage_level} /></td>
                    <td className={cn(tdClass, 'text-muted-foreground')}>
                      {c.patient ? `${c.patient.first_name} ${c.patient.last_name}` : '—'}
                    </td>
                    <td className={tdClass}><StatusBadge status={c.status} /></td>
                    <td className={cn(tdClass, 'text-muted-foreground tabular-nums')}>{formatDate(c.created_at)}</td>
                    <td className={cn(tdClass, 'text-right pr-5 tabular-nums text-muted-foreground')}>{c.image_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="px-5 py-3 border-t border-border flex items-center justify-between">
          <span className="text-sm text-muted-foreground tabular-nums">{data ? `${data.total} casos` : ''}</span>
          <div className="flex items-center gap-3">
            <span className="text-sm text-muted-foreground tabular-nums">Página {page} de {totalPages}</span>
            <button className={secondaryButton} disabled={page <= 1} onClick={() => setPage((n) => n - 1)} aria-label="Página anterior">
              <ChevronLeft aria-hidden className="w-4 h-4" />
            </button>
            <button className={secondaryButton} disabled={page >= totalPages} onClick={() => setPage((n) => n + 1)} aria-label="Página siguiente">
              <ChevronRight aria-hidden className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
