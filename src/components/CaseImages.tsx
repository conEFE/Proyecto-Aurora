import { useEffect, useState, type ReactNode } from 'react';
import { AlertTriangle, CheckCircle2, ImageIcon, Loader2, RefreshCw } from 'lucide-react';
import { apiClient } from '../services/api';
import type { AIVerdict, CaseImage, InferenceResult, InferenceStatus, Laterality, Me } from '../types';
import { AI_VERDICT_LABELS, EXAM_TYPE_LABELS } from '../types';
import { cn } from '../lib/cn';
import { AiOriginBadge } from './Badges';
import { BreastDiagram } from './BilateralPlate';
import { ErrorMessage, Loading } from './Feedback';
import { formatDateTime, ghostButton, inputClass } from './ui';

/** Carga las imágenes visibles con Authorization y libera los object URL al desmontar. */
function useImageUrls(caseId: number, images: CaseImage[] | null, enabled: boolean): Record<number, string> {
  const [urls, setUrls] = useState<Record<number, string>>({});
  const ids = (images ?? []).map((i) => i.id).join(',');
  useEffect(() => {
    if (!enabled || !ids) return;
    let cancelled = false;
    const created: string[] = [];
    Promise.all(
      ids.split(',').map(async (id) => {
        const blob = await apiClient.fetchImageBlob(caseId, Number(id));
        if (!blob) return null;
        const url = URL.createObjectURL(blob);
        created.push(url);
        return [Number(id), url] as const;
      }),
    ).then((pairs) => {
      if (!cancelled) setUrls(Object.fromEntries(pairs.filter((p): p is readonly [number, string] => p !== null)));
    });
    return () => {
      cancelled = true;
      created.forEach((u) => URL.revokeObjectURL(u));
    };
  }, [caseId, ids, enabled]);
  return urls;
}

export function InferenceCard({ result }: { result: InferenceResult }) {
  return (
    <div
      className={cn(
        'px-4 py-3 rounded-lg border text-sm space-y-1.5',
        result.detected ? 'bg-media/10 border-media/30' : 'bg-baja/10 border-baja/30',
      )}
    >
      <div className="flex flex-wrap items-center gap-2">
        {result.detected ? (
          <AlertTriangle aria-hidden className="w-4 h-4 text-media" />
        ) : (
          <CheckCircle2 aria-hidden className="w-4 h-4 text-baja" />
        )}
        <span className="font-bold">
          {result.detected ? 'Sospecha de malignidad según la IA' : 'Baja probabilidad de malignidad según la IA'}
        </span>
        <span className="tabular-nums text-muted-foreground">probabilidad de malignidad {result.confidence.toFixed(1).replace('.', ',')} %</span>
        <AiOriginBadge isSimulated={result.is_simulated} clinicallyValidated={result.clinically_validated} />
      </div>
      <p className="text-muted-foreground">{result.message}</p>
      <p className="text-xs text-muted-foreground">
        Modelo {result.model_version} · {result.processing_time_ms} ms
        {result.is_simulated ? (
          <span className="font-semibold text-sim"> · Resultado ficticio, sin valor clínico ni diagnóstico.</span>
        ) : (
          !result.clinically_validated && (
            <span className="font-semibold text-proto"> · Modelo en etapa de prototipo, sin validación clínica. Apoya, no reemplaza, el criterio médico.</span>
          )
        )}
      </p>
    </div>
  );
}

const VERDICT_TONE: Record<AIVerdict, string> = {
  CONCORDANTE: 'text-baja border-baja/40 bg-baja/10',
  FALSO_POSITIVO: 'text-alta border-alta/40 bg-alta/10',
  FALSO_NEGATIVO: 'text-alta border-alta/40 bg-alta/10',
  NO_EVALUABLE: 'text-muted-foreground border-input bg-muted',
};

/** El médico aprueba (concordante) o rechaza (falso positivo/negativo) el resultado de IA. */
function AIValidationBox({ image, readOnly, onSaved }: { image: CaseImage; readOnly: boolean; onSaved: () => void }) {
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
    } else setError(r.error || 'No se pudo guardar la validación. Intente de nuevo.');
  };

  if (current && !editing) {
    return (
      <div className="flex flex-wrap items-center justify-between gap-2 text-sm">
        <span className="text-muted-foreground">
          Validación médica:{' '}
          <span className={cn('px-2 py-0.5 rounded-md border font-bold', VERDICT_TONE[current.verdict])}>
            {AI_VERDICT_LABELS[current.verdict]}
          </span>
          {current.comment && <span className="ml-2">{current.comment}</span>}
        </span>
        {!readOnly && (
          <button className={cn(ghostButton, 'h-8 px-2')} onClick={() => setEditing(true)}>Cambiar</button>
        )}
      </div>
    );
  }
  if (readOnly) return <p className="text-sm text-muted-foreground">Resultado de IA sin validación médica.</p>;
  const commentId = `ai-comment-${image.id}`;
  return (
    <fieldset className="space-y-3" disabled={busy}>
      <legend className="text-sm font-bold mb-2">¿Está de acuerdo con el resultado de la IA?</legend>
      <div className="flex flex-wrap gap-2">
        {options.map((v) => (
          <button
            key={v}
            onClick={() => save(v)}
            className={cn('h-9 px-3 rounded-lg border text-sm font-bold transition-opacity hover:opacity-80 disabled:opacity-50', VERDICT_TONE[v])}
          >
            {AI_VERDICT_LABELS[v]}
          </button>
        ))}
      </div>
      <label htmlFor={commentId} className="sr-only">Comentario de la validación</label>
      <input id={commentId} className={inputClass} placeholder="Comentario (opcional)" value={comment} onChange={(e) => setComment(e.target.value)} />
      <ErrorMessage>{error}</ErrorMessage>
    </fieldset>
  );
}

/** Reanaliza con el modelo real una imagen que quedó con el respaldo simulado (el modelo estaba apagado). */
function RetryInference({ image, onDone }: { image: CaseImage; onDone: () => void }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const run = async () => {
    setBusy(true);
    setError(null);
    const r = await apiClient.retryInference(image.case_id, image.id);
    setBusy(false);
    if (r.data) onDone();
    else setError(r.error || 'No se pudo analizar con el modelo. Intente más tarde.');
  };
  return (
    <div className="flex flex-wrap items-center gap-3 text-sm">
      <button onClick={run} disabled={busy} className={cn(ghostButton, 'h-9 border border-input')}>
        {busy ? <Loader2 aria-hidden className="w-4 h-4 animate-spin" /> : <RefreshCw aria-hidden className="w-4 h-4" />}
        Analizar con el modelo
      </button>
      <span className="text-muted-foreground">El modelo no estaba disponible cuando se subió la imagen.</span>
      <ErrorMessage className="w-full">{error}</ErrorMessage>
    </div>
  );
}

function sideLabel(l?: Laterality | null): string {
  if (l === 'L') return 'Izquierda';
  if (l === 'R') return 'Derecha';
  return 'Lado no indicado';
}

function statusOf(img: CaseImage, canView: boolean): { label: string; pending: boolean } {
  if (img.inference_status === 'PENDIENTE') return { label: 'analizando', pending: false };
  if (canView && img.inference && !img.validation) return { label: 'por validar', pending: true };
  if (img.validation) return { label: 'validada', pending: false };
  return { label: 'lista', pending: false };
}

/** Miniatura dentro de la lámina: elige la imagen que se muestra en el visor. */
function Thumb({ img, url, active, canView, onSelect }: { img: CaseImage; url?: string; active: boolean; canView: boolean; onSelect: () => void }) {
  const st = statusOf(img, canView);
  return (
    <button
      onClick={onSelect}
      aria-pressed={active}
      aria-label={`${EXAM_TYPE_LABELS[img.exam_type]}, ${sideLabel(img.laterality).toLowerCase()}, ${st.label}`}
      className={cn('w-24 text-left rounded-lg p-1 transition-colors', active ? 'ring-2 ring-brand bg-brand/5' : 'hover:bg-accent')}
    >
      <span className="block aspect-[4/5] rounded-md overflow-hidden bg-[hsl(268_33%_6%)]">
        {canView && url ? (
          <img src={url} alt="" className="w-full h-full object-cover" />
        ) : (
          <span className="w-full h-full flex items-center justify-center text-white/50">
            <ImageIcon aria-hidden className="w-5 h-5" />
          </span>
        )}
      </span>
      <span className="block mt-1 text-xs font-semibold truncate">{EXAM_TYPE_LABELS[img.exam_type]}</span>
      <span className={cn('block text-xs', st.pending ? 'text-media font-semibold' : 'text-muted-foreground')}>{st.label}</span>
    </button>
  );
}

function PlateColumn({
  side,
  images,
  urls,
  selectedId,
  canView,
  onSelect,
}: {
  side: 'R' | 'L';
  images: CaseImage[];
  urls: Record<number, string>;
  selectedId: number | null;
  canView: boolean;
  onSelect: (id: number) => void;
}) {
  const finding = canView && images.some((i) => i.inference?.detected);
  return (
    <div className="min-w-0 flex flex-col items-center text-center">
      <BreastDiagram side={side === 'R' ? 'DERECHA' : 'IZQUIERDA'} active={images.length > 0} className="w-24 h-24" />
      <p className="mt-1.5 text-sm">
        <span className={cn('font-bold', images.length === 0 && 'text-muted-foreground')}>{side === 'R' ? 'Derecha' : 'Izquierda'}</span>
        <span className="text-muted-foreground"> · {images.length === 0 ? 'sin imágenes' : images.length === 1 ? '1 imagen' : `${images.length} imágenes`}</span>
      </p>
      {finding && (
        <p className="mt-1 inline-flex items-center gap-1.5 text-xs font-bold text-media">
          <AlertTriangle aria-hidden className="w-3.5 h-3.5" /> Sospecha IA en este lado
        </p>
      )}
      {images.length > 0 && (
        <div className="mt-3 flex flex-wrap justify-center gap-2">
          {images.map((img) => (
            <Thumb key={img.id} img={img} url={urls[img.id]} active={selectedId === img.id} canView={canView} onSelect={() => onSelect(img.id)} />
          ))}
        </div>
      )}
    </div>
  );
}

/** Visor de una imagen con su resultado de IA y la validación médica. */
function Viewer({
  image,
  url,
  canView,
  readOnly,
  modelAvailable,
  onChanged,
}: {
  image: CaseImage;
  url?: string;
  canView: boolean;
  readOnly: boolean;
  modelAvailable: boolean;
  onChanged: () => void;
}) {
  const [showBoxes, setShowBoxes] = useState(true);
  // Las cajas se muestran siempre (también si la CNN no supera el umbral): YOLO marca masas aparte
  const detections = image.inference?.detections ?? [];
  const canRetry = modelAvailable && !readOnly && !!image.inference?.is_simulated && !image.validation;
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h4 className="text-base font-bold">{EXAM_TYPE_LABELS[image.exam_type]} · {sideLabel(image.laterality)}</h4>
        <span className="text-xs text-muted-foreground tabular-nums">{image.filename} · {formatDateTime(image.uploaded_at)}</span>
      </div>
      {canView ? (
        <>
          <div className="relative flex items-center justify-center min-h-[18rem] bg-[hsl(268_33%_6%)] rounded-lg overflow-hidden">
            {url ? (
              // El contenedor toma el tamaño real de la imagen: las cajas quedan sobre la mamografía
              <div className="relative inline-block">
                <img
                  src={url}
                  alt={`${EXAM_TYPE_LABELS[image.exam_type]}, ${sideLabel(image.laterality).toLowerCase()}`}
                  className="block max-w-full max-h-[32rem]"
                />
                {/* Capa del hallazgo: se puede ocultar para leer la imagen sin marcas */}
                {showBoxes &&
                  detections.map((d, i) => (
                    <div
                      key={i}
                      className="absolute border-2 border-[hsl(38_91%_55%)] rounded"
                      style={{ left: `${d.x * 100}%`, top: `${d.y * 100}%`, width: `${d.width * 100}%`, height: `${d.height * 100}%` }}
                      title={`Masa · confianza de detección ${(d.confidence * 100).toFixed(0)} %${image.inference?.is_simulated ? ' (simulado)' : ''}`}
                    />
                  ))}
              </div>
            ) : (
              <Loader2 aria-label="Cargando imagen" className="w-6 h-6 animate-spin text-white/60" />
            )}
            {url && detections.length > 0 && (
              <button
                onClick={() => setShowBoxes((v) => !v)}
                aria-pressed={showBoxes}
                className="absolute top-3 right-3 h-8 px-3 rounded-md bg-[hsl(268_33%_6%/0.8)] text-white text-xs font-semibold border border-white/20 hover:bg-[hsl(268_33%_6%)]"
              >
                {showBoxes ? 'Ocultar marcas de la IA' : 'Mostrar marcas de la IA'}
              </button>
            )}
          </div>
          {image.inference ? (
            <>
              <InferenceCard result={image.inference} />
              {canRetry && <RetryInference image={image} onDone={onChanged} />}
              <AIValidationBox key={`${image.id}-${image.validation?.verdict ?? 'none'}`} image={image} readOnly={readOnly} onSaved={onChanged} />
            </>
          ) : (
            <p role="status" className="text-sm text-muted-foreground flex items-center gap-2">
              <Loader2 aria-hidden className="w-4 h-4 animate-spin" /> Análisis en curso…
            </p>
          )}
        </>
      ) : (
        <p className="text-sm text-muted-foreground">
          {image.size_kb ?? 0} KB · análisis {image.inference_status === 'LISTO' ? 'listo' : 'pendiente'}. Las imágenes y
          sus resultados solo los ve el personal médico.
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
  /** Contenido que va entre la lámina y el visor (p. ej., la acción principal del caso). */
  afterPlate?: ReactNode;
}

/** Lámina bilateral D/I con las imágenes de cada lado, y debajo el visor de la imagen elegida. */
export default function CaseImages({ caseId, me, refreshKey = 0, readOnly = false, onValidationChange, afterPlate }: CaseImagesProps) {
  const [images, setImages] = useState<CaseImage[] | null>(null);
  const [localKey, setLocalKey] = useState(0);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const canView = me.role === 'MEDICO';
  const urls = useImageUrls(caseId, images, canView);
  const [status, setStatus] = useState<InferenceStatus | null>(null);

  useEffect(() => {
    if (!canView) return;
    apiClient.getInferenceStatus().then((r) => setStatus(r.data ?? null));
  }, [canView, localKey]);
  const modelAvailable = status?.provider === 'http' && status.reachable === true;

  useEffect(() => {
    let cancelled = false;
    let timer: number | undefined;
    const load = async () => {
      const r = await apiClient.listImages(caseId);
      if (cancelled || !r.data) return;
      setImages(r.data);
      // Mientras haya inferencias pendientes, volver a consultar
      if (r.data.some((img) => img.inference_status === 'PENDIENTE')) timer = window.setTimeout(load, 1500);
    };
    load();
    return () => {
      cancelled = true;
      if (timer) window.clearTimeout(timer);
    };
  }, [caseId, refreshKey, localKey]);

  if (images === null) return <Loading label="Cargando imágenes…" className="py-6" />;

  const right = images.filter((i) => i.laterality === 'R');
  const left = images.filter((i) => i.laterality === 'L');
  const unknown = images.filter((i) => !i.laterality);
  // Por defecto, la primera imagen que falta validar; si no hay, la primera
  const fallback = images.find((i) => statusOf(i, canView).pending) ?? images[0];
  const selected = images.find((i) => i.id === selectedId) ?? fallback ?? null;

  return (
    <div className="space-y-6">
      <div>
        <div className="grid grid-cols-2 divide-x divide-border">
          <div className="pr-4">
            <PlateColumn side="R" images={right} urls={urls} selectedId={selected?.id ?? null} canView={canView} onSelect={setSelectedId} />
          </div>
          <div className="pl-4">
            <PlateColumn side="L" images={left} urls={urls} selectedId={selected?.id ?? null} canView={canView} onSelect={setSelectedId} />
          </div>
        </div>
        {unknown.length > 0 && (
          <div className="mt-4 pt-4 border-t border-border">
            <p className="text-sm text-muted-foreground mb-2">Sin lado indicado</p>
            <div className="flex flex-wrap gap-2">
              {unknown.map((img) => (
                <Thumb key={img.id} img={img} url={urls[img.id]} active={selected?.id === img.id} canView={canView} onSelect={() => setSelectedId(img.id)} />
              ))}
            </div>
          </div>
        )}
        {images.length === 0 && (
          <p className="mt-4 text-sm text-muted-foreground text-center">El caso aún no tiene imágenes. Agréguelas con «Agregar imágenes».</p>
        )}
      </div>

      {afterPlate}

      {selected && (
        <div className="pt-6 border-t border-border">
          <Viewer
            image={selected}
            url={urls[selected.id]}
            canView={canView}
            readOnly={readOnly}
            modelAvailable={modelAvailable}
            onChanged={() => {
              setLocalKey((k) => k + 1);
              onValidationChange?.();
            }}
          />
        </div>
      )}
    </div>
  );
}
