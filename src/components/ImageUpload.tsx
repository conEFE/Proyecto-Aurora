import { useEffect, useState } from 'react';
import { ImageUp, Loader2, Upload } from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '../services/api';
import type { ClinicalCase, ExamType, InferenceStatus, Laterality, Me } from '../types';
import { EXAM_TYPE_LABELS } from '../types';
import { compressionEnabled, prepareForUpload } from '../utils/compress';
import { cn } from '../lib/cn';
import { PrototypeBadge, SimulatedBadge } from './Badges';
import { BreastDiagram } from './BilateralPlate';
import CaseImages from './CaseImages';
import { ErrorMessage } from './Feedback';
import { cardClass, hintClass, inputClass, labelClass, pageClass, pageSubtitle, pageTitle, primaryButton, sectionTitle } from './ui';

const MAX_UPLOAD_MB = Number(import.meta.env.VITE_MAX_UPLOAD_MB || 60);

const SIDES: Array<{ value: Laterality | ''; label: string }> = [
  { value: 'R', label: 'Derecha' },
  { value: 'L', label: 'Izquierda' },
  { value: '', label: 'No indicada' },
];

export default function ImageUpload({ me }: { me: Me }) {
  const [cases, setCases] = useState<ClinicalCase[]>([]);
  const [caseId, setCaseId] = useState<number | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [examType, setExamType] = useState<ExamType>('MAMOGRAFIA');
  const [laterality, setLaterality] = useState<Laterality | ''>('');
  const [progress, setProgress] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [dragging, setDragging] = useState(false);
  const [inference, setInference] = useState<InferenceStatus | null>(null);

  useEffect(() => {
    apiClient.getInferenceStatus().then((r) => setInference(r.data ?? null));
  }, []);
  const modelText =
    inference?.provider === 'http'
      ? inference.reachable
        ? 'el modelo de IA (prototipo, conectado)'
        : 'la IA simulada: el modelo de IA no responde en este momento'
      : 'la IA simulada (el modelo de IA no está configurado)';

  useEffect(() => {
    apiClient.getCases({ size: 100 }).then((r) => {
      if (r.data) setCases(r.data.items.filter((c) => c.status !== 'CERRADO'));
    });
  }, []);

  useEffect(() => {
    if (!file) {
      setPreview(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const pick = (f: File | null) => {
    setError(null);
    if (f && !['image/png', 'image/jpeg'].includes(f.type)) {
      setError('Formato no permitido. Use PNG o JPEG.');
      return;
    }
    if (f && !compressionEnabled && f.size > MAX_UPLOAD_MB * 1024 * 1024) {
      setError(`La imagen supera el máximo de ${MAX_UPLOAD_MB} MB.`);
      setFile(null);
      return;
    }
    setFile(f);
  };

  const submit = async () => {
    if (!file || !caseId) return;
    setError(null);
    setProgress(0);
    const prepared = await prepareForUpload(file);
    const r = await apiClient.uploadImage(
      caseId,
      prepared.blob,
      prepared.filename,
      { exam_type: examType, laterality: laterality || null },
      setProgress,
    );
    setProgress(null);
    if (r.data) {
      toast.success(`Imagen cargada${prepared.compressed ? ' (comprimida en el navegador)' : ''}. El análisis corre en segundo plano.`);
      setFile(null);
      setRefreshKey((k) => k + 1);
    } else {
      setError(r.error || 'No se pudo subir la imagen. Intente de nuevo.');
    }
  };

  const uploading = progress !== null;

  return (
    <div className={pageClass}>
      <h1 className={pageTitle}>Cargar imágenes</h1>
      <p className={pageSubtitle}>
        Mamografías o ecografías en PNG o JPEG (máx. {MAX_UPLOAD_MB} MB). Se guardan cifradas y se analizan con {modelText}.
      </p>

      <div className="mt-6 grid xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] gap-6 items-start">
        <section aria-labelledby="upload-title" className={cn(cardClass, 'p-6 space-y-5')}>
          <h2 id="upload-title" className={sectionTitle}>Nueva imagen</h2>
          <div>
            <label className={labelClass} htmlFor="up-case">Caso</label>
            <select
              id="up-case"
              className={inputClass}
              value={caseId ?? ''}
              onChange={(e) => setCaseId(e.target.value ? Number(e.target.value) : null)}
              disabled={uploading}
              aria-describedby="up-case-hint"
            >
              <option value="">Seleccione un caso abierto</option>
              {cases.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.code} · {c.patient ? `${c.patient.first_name} ${c.patient.last_name}` : ''}
                </option>
              ))}
            </select>
            <p id="up-case-hint" className={hintClass}>Los casos se crean en la sección Casos.</p>
          </div>

          <div>
            <label className={labelClass} htmlFor="up-exam">Tipo de examen</label>
            <select id="up-exam" className={cn(inputClass, 'w-60')} value={examType}
              onChange={(e) => setExamType(e.target.value as ExamType)} disabled={uploading}>
              {(Object.keys(EXAM_TYPE_LABELS) as ExamType[]).map((t) => (
                <option key={t} value={t}>{EXAM_TYPE_LABELS[t]}</option>
              ))}
            </select>
          </div>

          <fieldset disabled={uploading}>
            <legend className={labelClass}>Lado</legend>
            <div className="grid grid-cols-3 gap-3">
              {SIDES.map((s) => {
                const selected = laterality === s.value;
                return (
                  <label
                    key={s.label}
                    className={cn(
                      'flex flex-col items-center gap-1 py-3 rounded-xl border cursor-pointer transition-colors has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-ring',
                      selected ? 'border-brand bg-brand/5' : 'border-border hover:bg-accent',
                    )}
                  >
                    <input
                      type="radio"
                      name="laterality"
                      value={s.value}
                      checked={selected}
                      onChange={() => setLaterality(s.value)}
                      className="sr-only"
                    />
                    {s.value ? (
                      <BreastDiagram side={s.value === 'R' ? 'DERECHA' : 'IZQUIERDA'} active={selected} className="w-16 h-16" />
                    ) : (
                      <span aria-hidden className="w-16 h-16 flex items-center justify-center text-2xl text-muted-foreground">—</span>
                    )}
                    <span className={cn('text-sm', selected ? 'font-bold' : 'text-muted-foreground')}>{s.label}</span>
                  </label>
                );
              })}
            </div>
          </fieldset>

          <label
            onDragOver={(e) => {
              e.preventDefault();
              setDragging(true);
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragging(false);
              pick(e.dataTransfer.files?.[0] ?? null);
            }}
            className={cn(
              'flex flex-col items-center justify-center gap-2 p-6 rounded-xl border-2 border-dashed cursor-pointer transition-colors has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-ring',
              dragging ? 'border-brand bg-brand/5' : 'border-input hover:border-brand/60',
            )}
          >
            <Upload aria-hidden className="w-6 h-6 text-brand" />
            <span className="text-sm font-semibold">{file ? file.name : 'Arrastre la imagen aquí o haga clic para elegirla'}</span>
            {file && <span className="text-xs text-muted-foreground tabular-nums">{(file.size / 1024 / 1024).toFixed(1).replace('.', ',')} MB</span>}
            <input type="file" accept="image/png,image/jpeg" className="sr-only" onChange={(e) => pick(e.target.files?.[0] ?? null)} disabled={uploading} />
          </label>

          {preview && (
            <div className="aspect-[4/3] bg-[hsl(268_33%_6%)] rounded-xl overflow-hidden">
              <img src={preview} alt="Vista previa de la imagen seleccionada" className="w-full h-full object-contain" />
            </div>
          )}

          {uploading && (
            <div role="status" aria-live="polite">
              <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
                <div className="bg-primary h-2 rounded-full transition-[width]" style={{ width: `${progress}%` }} />
              </div>
              <p className="mt-1 text-sm text-muted-foreground tabular-nums">Subiendo… {progress} %</p>
            </div>
          )}

          <ErrorMessage>{error}</ErrorMessage>

          <button className={cn(primaryButton, 'w-full')} disabled={!file || !caseId || uploading} onClick={submit}>
            {uploading ? <Loader2 aria-hidden className="w-4 h-4 animate-spin" /> : <ImageUp aria-hidden className="w-4 h-4" />}
            Subir y analizar
          </button>

          <div className="pt-4 border-t border-border text-sm text-muted-foreground space-y-2">
            <div className="flex flex-wrap gap-2">
              <PrototypeBadge />
              <SimulatedBadge />
            </div>
            <p>
              Herramienta de apoyo: no reemplaza el criterio médico. Los resultados del modelo real aún no tienen
              validación clínica. Si el modelo no responde, se usa la IA simulada y el médico puede volver a analizar la
              imagen después.
            </p>
          </div>
        </section>

        <section aria-labelledby="case-images-title" className={cn(cardClass, 'p-6')}>
          <h2 id="case-images-title" className={cn(sectionTitle, 'mb-4')}>Imágenes del caso</h2>
          {caseId ? (
            <CaseImages caseId={caseId} me={me} refreshKey={refreshKey} />
          ) : (
            <p className="text-sm text-muted-foreground">Seleccione un caso para ver sus imágenes.</p>
          )}
        </section>
      </div>
    </div>
  );
}
