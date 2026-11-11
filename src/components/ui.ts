// Clases de Tailwind compartidas para mantener formularios y botones consistentes.

export const inputClass =
  'w-full h-10 px-3 bg-background border border-input rounded-lg text-sm text-foreground placeholder:text-muted-foreground transition-colors hover:border-brand/50 focus:outline-none focus:ring-2 focus:ring-ring/40 focus:border-brand disabled:opacity-60 disabled:cursor-not-allowed aria-[invalid=true]:border-destructive';

export const textareaClass = inputClass.replace('h-10', 'min-h-[5rem] py-2');

export const labelClass = 'block text-sm font-medium text-foreground mb-1.5';

export const hintClass = 'mt-1 text-xs text-muted-foreground';

const buttonBase =
  'inline-flex items-center justify-center gap-2 h-10 px-4 rounded-lg text-sm font-semibold transition-colors disabled:cursor-not-allowed whitespace-nowrap';

export const primaryButton = `${buttonBase} bg-primary text-primary-foreground hover:bg-primary/90 active:bg-primary/80 disabled:bg-muted disabled:text-muted-foreground`;

export const secondaryButton = `${buttonBase} border border-input bg-card text-foreground hover:bg-accent disabled:opacity-50`;

export const ghostButton = `${buttonBase} text-muted-foreground hover:text-foreground hover:bg-accent disabled:opacity-50`;

export const dangerButton = `${buttonBase} bg-destructive text-destructive-foreground hover:bg-destructive/90 disabled:opacity-50`;

export const iconButton =
  'inline-flex items-center justify-center w-9 h-9 rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent transition-colors';

/** Panel con regla fina: sin sombra (la profundidad queda para diálogos y menús). */
export const cardClass = 'bg-card border border-border rounded-xl';

export const errorBox =
  'flex items-start gap-2 px-3 py-2.5 bg-destructive/10 border border-destructive/30 text-foreground rounded-lg text-sm';

export const successBox =
  'flex items-start gap-2 px-3 py-2.5 bg-baja/10 border border-baja/30 text-foreground rounded-lg text-sm';

export const thClass = 'px-3 h-10 text-left text-xs font-semibold text-muted-foreground border-b border-border';

export const tdClass = 'px-3 py-2.5 whitespace-nowrap text-sm border-b border-border';

export const pageClass = 'px-6 lg:px-8 py-6 max-w-[1440px]';

export const pageTitle = 'text-2xl font-extrabold text-foreground';

export const pageSubtitle = 'mt-1 text-sm text-muted-foreground';

export const sectionTitle = 'text-base font-bold text-foreground';

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
