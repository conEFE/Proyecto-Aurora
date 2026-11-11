import { AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import type { ReactNode } from 'react';
import { cn } from '../lib/cn';
import { errorBox, successBox } from './ui';

/** Error anunciado al lector de pantalla (role="alert"). */
export function ErrorMessage({ children, className }: { children: ReactNode; className?: string }) {
  if (!children) return null;
  return (
    <div role="alert" className={cn(errorBox, className)}>
      <AlertCircle aria-hidden className="w-4 h-4 mt-0.5 shrink-0 text-destructive" />
      <div>{children}</div>
    </div>
  );
}

export function SuccessMessage({ children, className }: { children: ReactNode; className?: string }) {
  if (!children) return null;
  return (
    <div role="status" className={cn(successBox, className)}>
      <CheckCircle2 aria-hidden className="w-4 h-4 mt-0.5 shrink-0 text-baja" />
      <div>{children}</div>
    </div>
  );
}

/** Estado de carga anunciado sin interrumpir (aria-live="polite"). */
export function Loading({ label = 'Cargando…', className }: { label?: string; className?: string }) {
  return (
    <div role="status" aria-live="polite" className={cn('flex items-center justify-center gap-2 py-10 text-sm text-muted-foreground', className)}>
      <Loader2 aria-hidden className="w-5 h-5 animate-spin text-brand" />
      {label}
    </div>
  );
}

export function EmptyState({ title, children, icon }: { title: string; children?: ReactNode; icon?: ReactNode }) {
  return (
    <div className="flex flex-col items-center text-center py-12 px-6">
      {icon && <div className="mb-3 text-muted-foreground">{icon}</div>}
      <p className="text-base font-bold text-foreground">{title}</p>
      {children && <div className="mt-1 max-w-md text-sm text-muted-foreground">{children}</div>}
    </div>
  );
}
