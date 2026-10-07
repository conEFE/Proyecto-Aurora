import { useEffect, useState } from 'react';
import { AlertCircle, CheckCircle2, ImageIcon, Loader2 } from 'lucide-react';
import { apiClient } from '../services/api';
import type { CaseImage, InferenceResult, Me } from '../types';
import { EXAM_TYPE_LABELS } from '../types';
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

function ImageCard({ image, canView }: { image: CaseImage; canView: boolean }) {
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
          <InferenceCard result={image.inference} />
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
}

export default function CaseImages({ caseId, me, refreshKey = 0 }: CaseImagesProps) {
  const [images, setImages] = useState<CaseImage[] | null>(null);
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
  }, [caseId, refreshKey]);

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
        <ImageCard key={img.id} image={img} canView={canView} />
      ))}
    </div>
  );
}
