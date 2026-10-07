// Clases de Tailwind compartidas para mantener formularios y botones consistentes.

export const inputClass =
  'w-full px-3 py-2 bg-background border border-input rounded text-xs text-foreground focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-60';

export const labelClass = 'block text-xs font-medium text-foreground mb-1';

export const primaryButton =
  'inline-flex items-center justify-center gap-1.5 px-3 py-2 bg-primary hover:bg-primary/90 disabled:bg-muted disabled:text-muted-foreground disabled:cursor-not-allowed text-primary-foreground rounded text-xs font-semibold transition-colors';

export const secondaryButton =
  'inline-flex items-center justify-center gap-1.5 px-3 py-2 bg-secondary hover:bg-secondary/80 disabled:opacity-50 text-foreground rounded text-xs font-medium transition-colors';

export const cardClass = 'bg-card border border-border rounded-lg';

export const errorBox =
  'p-2 bg-destructive/10 border border-destructive/20 text-destructive-foreground rounded text-xs';

export const thClass =
  'px-3 py-2 text-left text-[10px] font-semibold text-muted-foreground uppercase tracking-wider';

export const tdClass = 'px-3 py-2 whitespace-nowrap text-xs';

export function formatDate(value?: string | null): string {
  if (!value) return '—';
  return new Date(value).toLocaleDateString('es-CL', { year: 'numeric', month: '2-digit', day: '2-digit' });
}

export function formatDateTime(value?: string | null): string {
  if (!value) return '—';
  return new Date(value).toLocaleString('es-CL', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}
