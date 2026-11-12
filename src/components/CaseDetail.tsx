import { useEffect, useState } from 'react';
import { ImagePlus, Loader2, Save, X } from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '../services/api';
import type { CaseSymptoms, ClinicalCase, Me } from '../types';
import { cn } from '../lib/cn';
import { LevelBadge, StatusBadge } from './Badges';
import CaseImages from './CaseImages';
import { ErrorMessage, Loading } from './Feedback';
import ImageBatchPicker from './ImageBatchPicker';
import { uploadBatch, type PendingImage } from '../utils/imageBatch';
import SymptomsForm from './SymptomsForm';
import ReviewPanel from './ReviewPanel';
import TriageDetail from './TriageDetail';
import { cardClass, formatDateTime, iconButton, primaryButton, secondaryButton, sectionTitle } from './ui';

interface CaseDetailProps {
  caseId: number;
  me: Me;
  onChanged: () => void;
  onNextCase?: () => void;
}

function ageFrom(birthDate: string): number {
  const b = new Date(birthDate);
  const now = new Date();
  let age = now.getFullYear() - b.getFullYear();
  const m = now.getMonth() - b.getMonth();
  if (m < 0 || (m === 0 && now.getDate() < b.getDate())) age--;
  return age;
}

function symptomsOf(c: ClinicalCase): CaseSymptoms {
  return {
    palpable_mass: c.palpable_mass,
    nipple_discharge: c.nipple_discharge,
    skin_or_nipple_changes: c.skin_or_nipple_changes,
    birads_reported: c.birads_reported,
  };
}

/** Agrega imágenes a un caso abierto (p. ej., una vista o una ecografía que llegó después). */
function AddImages({ caseId, onUploaded }: { caseId: number; onUploaded: () => void }) {
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState<PendingImage[]>([]);
  const [progress, setProgress] = useState<{ index: number; percent: number } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const busy = progress !== null;

  const submit = async () => {
    setError(null);
    setProgress({ index: 0, percent: 0 });
    const failed = await uploadBatch(caseId, items, (index, percent) => setProgress({ index, percent }));
    setProgress(null);
    const uploaded = items.length - failed.length;
    if (uploaded > 0) toast.success(`${uploaded} ${uploaded === 1 ? 'imagen' : 'imágenes'} agregada${uploaded === 1 ? '' : 's'}. El análisis corre en segundo plano.`);
    if (failed.length > 0) setError(`No se pudieron subir: ${failed.join('; ')}`);
    else {
      setItems([]);
      setOpen(false);
    }
    onUploaded();
  };

  if (!open) {
    return (
      <button className={secondaryButton} onClick={() => setOpen(true)}>
        <ImagePlus aria-hidden className="w-4 h-4" /> Agregar imágenes
      </button>
    );
  }
  return (
    <div className="space-y-3 p-4 rounded-xl border border-border">
      <div className="flex items-center justify-between">
        <p className="text-sm font-bold">Agregar imágenes al caso</p>
        <button className={iconButton} aria-label="Cerrar" disabled={busy} onClick={() => setOpen(false)}>
          <X className="w-4 h-4" />
        </button>
      </div>
      <ErrorMessage>{error}</ErrorMessage>
      <ImageBatchPicker
        items={items}
        onChange={setItems}
        onRejected={(msgs) => setError(msgs.length ? `Imágenes no agregadas: ${msgs.join('; ')}` : null)}
        disabled={busy}
        progress={progress}
      />
      <button className={primaryButton} disabled={items.length === 0 || busy} onClick={submit}>
        {busy && <Loader2 aria-hidden className="w-4 h-4 animate-spin" />}
        {busy
          ? `Subiendo ${(progress?.index ?? 0) + 1} de ${items.length}…`
          : `Subir y analizar${items.length ? ` (${items.length})` : ''}`}
      </button>
    </div>
  );
}

export default function CaseDetail({ caseId, me, onChanged, onNextCase }: CaseDetailProps) {
  const [data, setData] = useState<ClinicalCase | null>(null);
  const [symptoms, setSymptoms] = useState<CaseSymptoms | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [triageKey, setTriageKey] = useState(0);
  const [validationKey, setValidationKey] = useState(0);
  const [imagesKey, setImagesKey] = useState(0);

  const reload = () => {
    apiClient.getCase(caseId).then((r) => {
      if (r.data) {
        setData(r.data);
        setSymptoms(symptomsOf(r.data));
      }
    });
    setTriageKey((k) => k + 1);
    onChanged();
  };

  useEffect(() => {
    let cancelled = false;
    apiClient.getCase(caseId).then((r) => {
      if (cancelled) return;
      if (r.data) {
        setData(r.data);
        setSymptoms(symptomsOf(r.data));
        setError(null);
      } else setError(r.error || 'No se pudo cargar el caso.');
    });
    return () => {
      cancelled = true;
    };
  }, [caseId]);

  if (error && !data) return <ErrorMessage>{error}</ErrorMessage>;
  if (!data || !symptoms) {
    return (
      <div className={cardClass}>
        <Loading label="Cargando el caso…" />
      </div>
    );
  }

  const closed = data.status === 'CERRADO';
  const dirty = JSON.stringify(symptoms) !== JSON.stringify(symptomsOf(data));

  const save = async () => {
    setSaving(true);
    const r = await apiClient.updateCase(data.id, symptoms);
    setSaving(false);
    if (r.data) {
      setData(r.data);
      setSymptoms(symptomsOf(r.data));
      setError(null);
      setTriageKey((k) => k + 1);
      toast.success('Antecedentes guardados. El triage se recalculó.');
      onChanged();
    } else setError(r.error || 'No se pudieron guardar los antecedentes.');
  };

  const p = data.patient;

  const symptomsCard = (
    <section aria-labelledby={`symptoms-${data.id}`} className={cn(cardClass, 'p-6 space-y-4')}>
      <h3 id={`symptoms-${data.id}`} className={sectionTitle}>Síntomas y BI-RADS informado</h3>
      <ErrorMessage>{error}</ErrorMessage>
      <SymptomsForm value={symptoms} onChange={setSymptoms} disabled={closed} />
      {closed ? (
        <p className="text-sm text-muted-foreground">Caso cerrado el {formatDateTime(data.closed_at)}</p>
      ) : (
        <button className={primaryButton} disabled={!dirty || saving} onClick={save}>
          {saving ? <Loader2 aria-hidden className="w-4 h-4 animate-spin" /> : <Save aria-hidden className="w-4 h-4" />}
          Guardar y recalcular triage
        </button>
      )}
    </section>
  );

  return (
    <div className="space-y-6">
      <section aria-labelledby={`case-${data.id}`} className="flex flex-wrap items-start justify-between gap-x-8 gap-y-4 pb-6 border-b border-border">
        <div>
          <div className="flex flex-wrap items-center gap-x-5 gap-y-2">
            <h2 id={`case-${data.id}`} className="text-4xl font-extrabold tabular-nums tracking-tight">{data.code}</h2>
            <LevelBadge level={data.triage_level} size="lg" />
            <StatusBadge status={data.status} />
          </div>
          {p && (
            <p className="mt-2 text-muted-foreground">
              <span className="font-semibold text-foreground">{p.first_name} {p.last_name}</span>
              <span className="tabular-nums"> · RUT {p.rut} · {ageFrom(p.birth_date)} años</span>
              {' · '}Familiar 1er grado: <strong className="text-foreground">{p.family_history_first_degree ? 'Sí' : 'No'}</strong>
              {' · '}Cáncer previo: <strong className="text-foreground">{p.previous_breast_cancer ? 'Sí' : 'No'}</strong>
            </p>
          )}
          <p className="mt-1 text-sm text-muted-foreground">Creado el {formatDateTime(data.created_at)}</p>
        </div>
        {!closed && (
          <AddImages
            caseId={data.id}
            onUploaded={() => {
              setImagesKey((k) => k + 1);
              reload();
            }}
          />
        )}
      </section>

      <div className="grid xl:grid-cols-[minmax(0,7fr)_minmax(0,5fr)] gap-6 items-start">
        <section aria-labelledby={`images-${data.id}`} className={cn(cardClass, 'p-6 min-w-0')}>
          <h3 id={`images-${data.id}`} className="sr-only">Imágenes por lado</h3>
          <CaseImages
            caseId={data.id}
            me={me}
            refreshKey={imagesKey}
            readOnly={closed}
            onValidationChange={() => setValidationKey((k) => k + 1)}
          />
        </section>

        <div className="space-y-6 min-w-0">
          {me.role === 'MEDICO' && (
            <>
              <ReviewPanel
                key={`rv-${data.status}`}
                caseData={data}
                me={me}
                validationKey={validationKey}
                onChanged={reload}
                onNextCase={onNextCase}
              />
              <TriageDetail key={triageKey} caseId={data.id} closed={closed} onChanged={reload} />
            </>
          )}
          {symptomsCard}
        </div>
      </div>
    </div>
  );
}
