import { useEffect, useState } from 'react';
import { Upload, X } from 'lucide-react';
import type { ExamType, Laterality } from '../types';
import { EXAM_TYPE_LABELS } from '../types';
import { MAX_UPLOAD_MB, toPending, type PendingImage } from '../utils/imageBatch';
import { cn } from '../lib/cn';
import { PrototypeBadge, SimulatedBadge } from './Badges';
import { iconButton, inputClass } from './ui';

function Preview({ file }: { file: File }) {
  const [url, setUrl] = useState<string | null>(null);
  useEffect(() => {
    const u = URL.createObjectURL(file);
    setUrl(u);
    return () => URL.revokeObjectURL(u);
  }, [file]);
  return (
    <div className="w-16 h-16 shrink-0 rounded-md overflow-hidden bg-[hsl(268_33%_6%)]">
      {url && <img src={url} alt="" className="w-full h-full object-contain" />}
    </div>
  );
}

interface ImageBatchPickerProps {
  items: PendingImage[];
  onChange: (items: PendingImage[]) => void;
  onRejected?: (messages: string[]) => void;
  disabled?: boolean;
  /** Índice y porcentaje de la imagen que se está subiendo */
  progress?: { index: number; percent: number } | null;
}

/** Selector de varias imágenes de un mismo examen (p. ej., CC y MLO de cada lado), con lado y tipo por imagen. */
export default function ImageBatchPicker({ items, onChange, onRejected, disabled, progress }: ImageBatchPickerProps) {
  const [dragging, setDragging] = useState(false);

  const add = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const { items: added, rejected } = toPending(files);
    onChange([...items, ...added]);
    onRejected?.(rejected);
  };
  const update = (key: string, patch: Partial<PendingImage>) =>
    onChange(items.map((it) => (it.key === key ? { ...it, ...patch } : it)));

  return (
    <div className="space-y-3">
      <label
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          if (!disabled) add(e.dataTransfer.files);
        }}
        className={cn(
          'flex flex-col items-center justify-center gap-1.5 p-5 rounded-xl border-2 border-dashed cursor-pointer transition-colors has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-ring',
          dragging ? 'border-brand bg-brand/5' : 'border-input hover:border-brand/60',
          disabled && 'opacity-60 cursor-not-allowed',
        )}
      >
        <Upload aria-hidden className="w-6 h-6 text-brand" />
        <span className="text-sm font-semibold">Arrastre las imágenes del examen o haga clic para elegirlas</span>
        <span className="text-xs text-muted-foreground">
          Puede elegir varias a la vez (p. ej., CC y MLO de cada lado). PNG o JPEG, máx. {MAX_UPLOAD_MB} MB c/u.
        </span>
        <input
          type="file"
          multiple
          accept="image/png,image/jpeg"
          className="sr-only"
          disabled={disabled}
          onChange={(e) => {
            add(e.target.files);
            e.target.value = '';
          }}
        />
      </label>

      {items.length > 0 && (
        <ul className="divide-y divide-border border border-border rounded-xl">
          {items.map((it, i) => {
            const uploadingThis = progress?.index === i;
            const done = progress ? i < progress.index : false;
            return (
              <li key={it.key} className="flex items-center gap-3 p-2.5">
                <Preview file={it.file} />
                <div className="min-w-0 flex-1 space-y-1.5">
                  <p className="text-sm font-medium truncate" title={it.file.name}>{it.file.name}</p>
                  <div className="flex flex-wrap gap-2">
                    <select
                      aria-label={`Lado de ${it.file.name}`}
                      className={cn(inputClass, 'h-8 w-36 text-sm')}
                      value={it.laterality}
                      disabled={disabled}
                      onChange={(e) => update(it.key, { laterality: e.target.value as Laterality | '' })}
                    >
                      <option value="R">Derecha</option>
                      <option value="L">Izquierda</option>
                      <option value="">Lado no indicado</option>
                    </select>
                    <select
                      aria-label={`Tipo de examen de ${it.file.name}`}
                      className={cn(inputClass, 'h-8 w-40 text-sm')}
                      value={it.examType}
                      disabled={disabled}
                      onChange={(e) => update(it.key, { examType: e.target.value as ExamType })}
                    >
                      {(Object.keys(EXAM_TYPE_LABELS) as ExamType[]).map((t) => (
                        <option key={t} value={t}>{EXAM_TYPE_LABELS[t]}</option>
                      ))}
                    </select>
                  </div>
                  {uploadingThis && (
                    <div role="status" aria-live="polite" className="w-full bg-muted rounded-full h-1.5 overflow-hidden">
                      <div className="bg-primary h-1.5 rounded-full transition-[width]" style={{ width: `${progress?.percent ?? 0}%` }} />
                    </div>
                  )}
                  {done && <p className="text-xs text-baja">Subida</p>}
                </div>
                <button
                  type="button"
                  className={iconButton}
                  aria-label={`Quitar ${it.file.name}`}
                  disabled={disabled}
                  onClick={() => onChange(items.filter((x) => x.key !== it.key))}
                >
                  <X className="w-4 h-4" />
                </button>
              </li>
            );
          })}
        </ul>
      )}

      <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
        <PrototypeBadge />
        <SimulatedBadge />
        <span>Se guardan cifradas y se analizan en segundo plano. Apoyo al criterio médico, no lo reemplaza.</span>
      </div>
    </div>
  );
}
