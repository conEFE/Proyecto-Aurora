import { useEffect, useState } from 'react';
import { AlertCircle, CheckCircle2, ImageIcon, Loader2 } from 'lucide-react';
import { apiClient } from '../services/api';
import type { AIVerdict, CaseImage, InferenceResult, Me } from '../types';
import { AI_VERDICT_LABELS, EXAM_TYPE_LABELS } from '../types';
import { SimulatedBadge } from './Badges';
import { formatDateTime } from './ui';

/** Carga la imagen con Authorization y libera el object URL al desmontar. */
function useImageUrl(caseId: number, imageId: number, enabled: boolean): string | null {
  const [url, setUrl] = useState<string | null>(null);
  useEffect(() => {
    if (!enabled) return;
    let objectUrl: string | null = null;
    let cancelled = false;
    apiClient.fetchImageBlob(caseId, imageId).then((blob) => {
      if (blob && !cancelled) {
        objectUrl = URL.createObjectURL(blob);
        setUrl(objectUrl);
      }
    });
    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [caseId, imageId, enabled]);
  return url;
}

export function InferenceCard({ result }: { result: InferenceResult }) {
  return (
    <div
      className={`p-2 rounded border text-[10px] space-y-1 ${
        result.detected ? 'bg-orange-500/10 border-orange-500/20' : 'bg-green-500/10 border-green-500/20'
      }`}
    >
      <div className="flex items-center gap-2">
        {result.detected ? (
          <AlertCircle className="w-3.5 h-3.5 text-orange-400" />
        ) : (
          <CheckCircle2 className="w-3.5 h-3.5 text-green-400" />
        )}
        <span className="font-semibold text-foreground">
          {result.detected ? 'Hallazgo' : 'Sin hallazgos'} · {result.confidence.toFixed(1)}%
        </span>
        {result.is_simulated && <SimulatedBadge />}
      </div>
      <p className="text-muted-foreground">{result.message}</p>
      <p className="text-muted-foreground">
        Modelo {result.model_version} · {result.processing_time_ms} ms
      </p>
      {result.is_simulated && (
        <p className="text-amber-300/90">
          Resultado ficticio para probar el flujo. No tiene valor clínico ni diagnóstico.
        </p>
      )}
    </div>
  );
}

const VERDICT_STYLES: Record<AIVerdict, string> = {
  CONCORDANTE: 'bg-green-500/15 text-green-300 border-green-500/40',
  FALSO_POSITIVO: 'bg-red-500/15 text-red-300 border-red-500/40',
  FALSO_NEGATIVO: 'bg-red-500/15 text-red-300 border-red-500/40',
  NO_EVALUABLE: 'bg-slate-500/15 text-slate-300 border-slate-500/40',
};

/** El médico aprueba (concordante) o rechaza (falso positivo/negativo) el resultado de IA. */
function AIValidationBox({
  image,
  readOnly,
  onSaved,
}: {
  image: CaseImage;
  readOnly: boolean;
  onSaved: () => void;
}) {
  const current = image.validation ?? null;
  const [editing, setEditing] = useState(current === null);
  const [comment, setComment] = useState(current?.comment ?? '');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  if (!image.inference) return null;
  // Falso positivo solo si la IA informó hallazgo; falso negativo solo si no
  const options: AIVerdict[] = image.inference.detected
    ? ['CONCORDANTE', 'FALSO_POSITIVO', 'NO_EVALUABLE']
    : ['CONCORDANTE', 'FALSO_NEGATIVO', 'NO_EVALUABLE'];

  const save = async (verdict: AIVerdict) => {
    setBusy(true);
    const r = await apiClient.validateAI(image.case_id, image.id, verdict, comment.trim());
    setBusy(false);
    if (r.data) {
      setError(null);
      setEditing(false);
      onSaved();
    } else setError(r.error || 'No se pudo guardar la validación');
  };

  if (current && !editing) {
    return (
      <div className="flex items-center justify-between gap-2 text-[10px]">
        <span className="text-muted-foreground">
          Validación médica:{' '}
          <span className={`px-1.5 py-0.5 rounded border font-semibold ${VERDICT_STYLES[current.verdict]}`}>
            {AI_VERDICT_LABELS[current.verdict]}
          </span>
          {current.comment && <span className="ml-1">· {current.comment}</span>}
        </span>
        {!readOnly && (
          <button className="text-primary" onClick={() => setEditing(true)}>Cambiar</button>
        )}
      </div>
    );
  }
  if (readOnly) {
    return <p className="text-[10px] text-muted-foreground">Resultado de IA sin validación médica.</p>;
  }
  return (
    <div className="p-2 border border-primary/30 rounded space-y-1.5">
      <p className="text-[10px] font-semibold text-foreground">¿Está de acuerdo con el resultado de la IA?</p>
      <input
        className="w-full px-2 py-1 bg-background border border-input rounded text-[10px] text-foreground"
        placeholder="Comentario (opcional)"
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        aria-label="Comentario de la validación"
      />
      <div className="flex flex-wrap gap-1.5">
        {options.map((v) => (
          <button
            key={v}
            disabled={busy}
            onClick={() => save(v)}
            className={`px-2 py-1 rounded border text-[10px] font-semibold disabled:opacity-50 ${VERDICT_STYLES[v]}`}
          >
            {AI_VERDICT_LABELS[v]}
          </button>
        ))}
      </div>
      {error && <p className="text-[10px] text-red-400">{error}</p>}
    </div>
  );
}

function ImageCard({
  image,
  canView,
  readOnly,
  onChanged,
}: {
  image: CaseImage;
  canView: boolean;
  readOnly: boolean;
  onChanged: () => void;
}) {
  const url = useImageUrl(image.case_id, image.id, canView);
  const detections = image.inference?.detected ? image.inference.detections ?? [] : [];

  return (
    <div className="border border-border rounded p-2 space-y-2">
      <div className="flex items-center justify-between text-[10px] text-muted-foreground">
        <span className="font-semibold text-foreground">
          {EXAM_TYPE_LABELS[image.exam_type]}
          {image.laterality ? ` · ${image.laterality === 'L' ? 'Izquierda' : 'Derecha'}` : ''}
        </span>
        <span>{formatDateTime(image.uploaded_at)}</span>
      </div>
      {canView && (
        <div className="relative aspect-video bg-background border border-border rounded overflow-hidden">
          {url ? (
            <img src={url} alt={image.filename} className="w-full h-full object-contain" />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />
            </div>
          )}
          {url &&
            detections.map((d, i) => (
              <div
                key={i}
                className="absolute border-2 border-amber-400 rounded"
                style={{
                  left: `${d.x * 100}%`,
                  top: `${d.y * 100}%`,
                  width: `${d.width * 100}%`,
                  height: `${d.height * 100}%`,
                }}
                title={`${d.class_name} ${(d.confidence * 100).toFixed(0)}% (simulado)`}
              />
            ))}
        </div>
      )}
      {canView ? (
        image.inference ? (
          <>
            <InferenceCard result={image.inference} />
            <AIValidationBox image={image} readOnly={readOnly} onSaved={onChanged} />
          </>
        ) : (
          <p className="text-[10px] text-muted-foreground flex items-center gap-1">
            <Loader2 className="w-3 h-3 animate-spin" /> Análisis en curso...
          </p>
        )
      ) : (
        <p className="text-[10px] text-muted-foreground">
          {image.filename} · {image.size_kb ?? 0} KB · análisis {image.inference_status === 'LISTO' ? 'listo' : 'pendiente'}
        </p>
      )}
    </div>
  );
}

interface CaseImagesProps {
  caseId: number;
  me: Me;
  refreshKey?: number;
  readOnly?: boolean;
  onValidationChange?: () => void;
}

export default function CaseImages({ caseId, me, refreshKey = 0, readOnly = false, onValidationChange }: CaseImagesProps) {
  const [images, setImages] = useState<CaseImage[] | null>(null);
  const [localKey, setLocalKey] = useState(0);
  const canView = me.role === 'MEDICO';

  useEffect(() => {
    let cancelled = false;
    let timer: number | undefined;
    const load = async () => {
      const r = await apiClient.listImages(caseId);
      if (cancelled || !r.data) return;
      setImages(r.data);
      // Mientras haya inferencias pendientes, volver a consultar
      if (r.data.some((img) => img.inference_status === 'PENDIENTE')) {
        timer = window.setTimeout(load, 1500);
      }
    };
    load();
    return () => {
      cancelled = true;
      if (timer) window.clearTimeout(timer);
    };
  }, [caseId, refreshKey, localKey]);

  if (images === null) return <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />;
  if (images.length === 0) {
    return (
      <p className="text-[10px] text-muted-foreground flex items-center gap-1">
        <ImageIcon className="w-3 h-3" /> El caso aún no tiene imágenes.
      </p>
    );
  }
  return (
    <div className="space-y-2">
      {!canView && (
        <p className="text-[10px] text-muted-foreground">
          Las imágenes y los resultados del análisis solo los ve el personal médico.
        </p>
      )}
      {images.map((img) => (
        <ImageCard
          key={`${img.id}-${img.validation?.verdict ?? 'none'}`}
          image={img}
          canView={canView}
          readOnly={readOnly}
          onChanged={() => {
            setLocalKey((k) => k + 1);
            onValidationChange?.();
          }}
        />
      ))}
    </div>
  );
}
