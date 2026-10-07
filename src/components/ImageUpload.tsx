import { useEffect, useState } from 'react';
import { Upload, Image as ImageIcon, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import { apiClient } from '../services/api';
import type { ClinicalCase, ExamType, Laterality, Me } from '../types';
import { EXAM_TYPE_LABELS } from '../types';
import { compressionEnabled, prepareForUpload } from '../utils/compress';
import CaseImages from './CaseImages';
import { cardClass, errorBox, inputClass, labelClass, primaryButton } from './ui';

const MAX_UPLOAD_MB = Number(import.meta.env.VITE_MAX_UPLOAD_MB || 60);

export default function ImageUpload({ me }: { me: Me }) {
  const [cases, setCases] = useState<ClinicalCase[]>([]);
  const [caseId, setCaseId] = useState<number | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [examType, setExamType] = useState<ExamType>('MAMOGRAFIA');
  const [laterality, setLaterality] = useState<Laterality | ''>('');
  const [progress, setProgress] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

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

  const onFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0] ?? null;
    setSuccess(null);
    setError(null);
    if (f && !compressionEnabled && f.size > MAX_UPLOAD_MB * 1024 * 1024) {
      setError(`La imagen supera el máximo de ${MAX_UPLOAD_MB} MB`);
      setFile(null);
      return;
    }
    setFile(f);
  };

  const submit = async () => {
    if (!file || !caseId) return;
    setError(null);
    setSuccess(null);
    setProgress(0);
    const prepared = await prepareForUpload(file);
    const r = await apiClient.uploadImage(
      caseId,
      prepared.blob,
      prepared.filename,
      { exam_type: examType, laterality: laterality || null },
      setProgress
    );
    setProgress(null);
    if (r.data) {
      setSuccess(
        `Imagen cargada${prepared.compressed ? ' (comprimida en el navegador)' : ''}. El análisis corre en segundo plano.`
      );
      setFile(null);
      setRefreshKey((k) => k + 1);
    } else {
      setError(r.error || 'Error al subir la imagen');
    }
  };

  const uploading = progress !== null;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      <div className="mb-4">
        <h2 className="text-lg font-bold text-foreground">Carga de imágenes</h2>
        <p className="mt-1 text-xs text-muted-foreground">
          Mamografías o ecografías en PNG o JPEG (máx. {MAX_UPLOAD_MB} MB). Se guardan cifradas y se analizan
          automáticamente con el proveedor de IA configurado (hoy: simulado).
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        <div className={`${cardClass} p-4 space-y-3`}>
          <div>
            <label className={labelClass} htmlFor="up-case">Caso</label>
            <select
              id="up-case"
              className={inputClass}
              value={caseId ?? ''}
              onChange={(e) => setCaseId(e.target.value ? Number(e.target.value) : null)}
              disabled={uploading}
            >
              <option value="">Seleccione un caso abierto...</option>
              {cases.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.code} · {c.patient ? `${c.patient.first_name} ${c.patient.last_name}` : ''}
                </option>
              ))}
            </select>
            <p className="mt-1 text-[10px] text-muted-foreground">Los casos se crean en la sección Casos.</p>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className={labelClass} htmlFor="up-exam">Tipo de examen</label>
              <select id="up-exam" className={inputClass} value={examType}
                onChange={(e) => setExamType(e.target.value as ExamType)} disabled={uploading}>
                {(Object.keys(EXAM_TYPE_LABELS) as ExamType[]).map((t) => (
                  <option key={t} value={t}>{EXAM_TYPE_LABELS[t]}</option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass} htmlFor="up-lat">Lateralidad</label>
              <select id="up-lat" className={inputClass} value={laterality}
                onChange={(e) => setLaterality(e.target.value as Laterality | '')} disabled={uploading}>
                <option value="">No indicada</option>
                <option value="L">Izquierda</option>
                <option value="R">Derecha</option>
              </select>
            </div>
          </div>

          <label className="flex flex-col items-center justify-center gap-2 p-4 border-2 border-dashed border-border rounded cursor-pointer hover:border-primary/50">
            <Upload className="w-6 h-6 text-primary" />
            <span className="text-xs text-foreground">{file ? file.name : 'Seleccionar imagen'}</span>
            {file && <span className="text-[10px] text-muted-foreground">{(file.size / 1024 / 1024).toFixed(1)} MB</span>}
            <input type="file" accept="image/png,image/jpeg" className="hidden" onChange={onFile} disabled={uploading} />
          </label>

          {preview && (
            <div className="aspect-video bg-background border border-border rounded overflow-hidden">
              <img src={preview} alt="Vista previa" className="w-full h-full object-contain" />
            </div>
          )}

          {uploading && (
            <div>
              <div className="w-full bg-secondary rounded-full h-2">
                <div className="bg-primary h-2 rounded-full transition-all" style={{ width: `${progress}%` }} />
              </div>
              <p className="mt-1 text-[10px] text-muted-foreground">Subiendo... {progress}%</p>
            </div>
          )}

          {error && <div className={errorBox}>{error}</div>}
          {success && (
            <div className="p-2 bg-green-500/10 border border-green-500/20 text-green-300 rounded text-xs flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5" /> {success}
            </div>
          )}

          <button className={`${primaryButton} w-full`} disabled={!file || !caseId || uploading} onClick={submit}>
            {uploading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <ImageIcon className="w-3.5 h-3.5" />}
            Subir y analizar
          </button>
        </div>

        <div className="space-y-4">
          <div className={`${cardClass} p-4`}>
            <h4 className="text-sm font-semibold text-foreground mb-3">Imágenes del caso</h4>
            {caseId ? (
              <CaseImages caseId={caseId} me={me} refreshKey={refreshKey} />
            ) : (
              <p className="text-xs text-muted-foreground">Seleccione un caso para ver sus imágenes.</p>
            )}
          </div>
          <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3 flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-blue-400 flex-shrink-0 mt-0.5" />
            <p className="text-[10px] text-muted-foreground">
              Herramienta de apoyo: no reemplaza el criterio médico. Mientras el modelo YOLO no esté integrado,
              todo resultado se marca como <strong className="text-amber-300">IA SIMULADA</strong> y no tiene valor
              clínico.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
