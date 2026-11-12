import { useEffect, useRef, useState } from 'react';
import { ArrowRight, Moon, Sun } from 'lucide-react';
import { useTheme } from '../lib/theme';
import { cn } from '../lib/cn';
import BrandMark from './BrandMark';
import { iconButton, primaryButton } from './ui';
import colaImg from '../assets/landing/cola.webp';
import prioridadImg from '../assets/landing/prioridad.webp';
import iaImg from '../assets/landing/ia.webp';
import laminaImg from '../assets/landing/lamina.webp';

interface Feature {
  id: string;
  title: string;
  text: string;
  img: string;
  alt: string;
  width: string;
}

const FEATURES: Feature[] = [
  {
    id: 'prioridad',
    title: 'Cada prioridad, explicada',
    text: 'Reglas clínicas y factores visibles. Nada de cajas negras.',
    img: prioridadImg,
    alt: 'Desglose del puntaje de triage de un caso ALTA',
    width: 'max-w-[26rem]',
  },
  {
    id: 'ia',
    title: 'La IA señala, el médico decide',
    text: 'Cada resultado de la IA se valida antes de cerrar el caso.',
    img: iaImg,
    alt: 'Resultado de la IA con la validación del médico',
    width: 'max-w-[36rem]',
  },
  {
    id: 'lamina',
    title: 'La orden, como la conoce',
    text: 'Ambas mamas y todas sus vistas en una sola lámina.',
    img: laminaImg,
    alt: 'Lámina bilateral con las vistas CC y MLO de cada lado',
    width: 'max-w-[36rem]',
  },
];

const AUTOPLAY_MS = 6000;
const container = 'mx-auto max-w-6xl px-4 sm:px-6';

function prefersReducedMotion() {
  return typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
}

/** Lista de funciones que cambia la captura del producto; avanza sola y se pausa al interactuar. */
function FeatureShowcase() {
  const [active, setActive] = useState(0);
  const [paused, setPaused] = useState(prefersReducedMotion);
  const [cycle, setCycle] = useState(0);
  const timer = useRef<number>();

  useEffect(() => {
    if (paused) return;
    timer.current = window.setTimeout(() => {
      setActive((i) => (i + 1) % FEATURES.length);
      setCycle((c) => c + 1);
    }, AUTOPLAY_MS);
    return () => window.clearTimeout(timer.current);
  }, [active, paused, cycle]);

  const select = (i: number) => {
    setActive(i);
    setPaused(true);
  };

  return (
    <div
      className="grid lg:grid-cols-[minmax(0,5fr)_minmax(0,7fr)] gap-8 lg:gap-14 items-center"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(prefersReducedMotion())}
    >
      <div role="tablist" aria-label="Funciones de Aurora Care" aria-orientation="vertical" className="flex flex-col gap-1">
        {FEATURES.map((f, i) => {
          const on = i === active;
          return (
            <button
              key={f.id}
              role="tab"
              id={`tab-${f.id}`}
              aria-selected={on}
              aria-controls={`panel-${f.id}`}
              tabIndex={on ? 0 : -1}
              onClick={() => select(i)}
              onKeyDown={(e) => {
                if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                  e.preventDefault();
                  const next = (i + (e.key === 'ArrowDown' ? 1 : FEATURES.length - 1)) % FEATURES.length;
                  select(next);
                  document.getElementById(`tab-${FEATURES[next].id}`)?.focus();
                }
              }}
              className={cn(
                'relative text-left rounded-xl px-5 py-4 transition-colors',
                on ? 'bg-muted' : 'hover:bg-muted/60',
              )}
            >
              <span className={cn('block text-lg font-bold', on ? 'text-foreground' : 'text-muted-foreground')}>{f.title}</span>
              <span
                className={cn(
                  'grid transition-[grid-template-rows] duration-300 ease-out',
                  on ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]',
                )}
              >
                <span className="overflow-hidden">
                  <span className="block pt-1 text-muted-foreground leading-relaxed">{f.text}</span>
                </span>
              </span>
              {/* Progreso del avance automático */}
              {on && !paused && (
                <span aria-hidden className="absolute left-5 right-5 bottom-0 h-0.5 rounded-full bg-border overflow-hidden">
                  <span
                    key={cycle}
                    className="block h-full bg-brand origin-left animate-[landing-progress_linear_forwards]"
                    style={{ animationDuration: `${AUTOPLAY_MS}ms` }}
                  />
                </span>
              )}
            </button>
          );
        })}
      </div>

      <div className="relative rounded-2xl bg-muted border border-border aspect-[4/3] overflow-hidden">
        {FEATURES.map((f, i) => (
          <div
            key={f.id}
            id={`panel-${f.id}`}
            role="tabpanel"
            aria-labelledby={`tab-${f.id}`}
            aria-hidden={i !== active}
            className={cn(
              'absolute inset-0 flex items-center justify-center p-6 sm:p-10 transition-all duration-500 ease-out',
              i === active ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2 pointer-events-none',
            )}
          >
            <img
              src={f.img}
              alt={f.alt}
              loading={i === 0 ? 'eager' : 'lazy'}
              className={cn('w-full h-auto max-h-full object-contain rounded-xl', f.width)}
            />
          </div>
        ))}
      </div>
    </div>
  );
}

/** Página pública de Aurora Care, con acceso al inicio de sesión. */
export default function Landing({ onLogin }: { onLogin: () => void }) {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="min-h-screen bg-background text-foreground">
      <style>{'@keyframes landing-progress{from{transform:scaleX(0)}to{transform:scaleX(1)}}'}</style>
      <header className="sticky top-0 z-20 border-b border-border/70 bg-background/90 backdrop-blur">
        <div className={cn(container, 'h-16 flex items-center justify-between gap-4')}>
          <a href="#inicio" className="flex items-center gap-2.5 rounded-md">
            <BrandMark alt="" />
            <span className="text-lg font-extrabold">Aurora Care</span>
          </a>
          <div className="flex items-center gap-2">
            <a href="#funciones" className="hidden sm:inline-flex h-10 items-center px-3 rounded-lg text-sm font-semibold text-muted-foreground hover:text-foreground">
              Funciones
            </a>
            <button
              onClick={toggleTheme}
              className={iconButton}
              aria-label={theme === 'dark' ? 'Usar tema claro' : 'Usar tema oscuro'}
            >
              {theme === 'dark' ? <Sun className="w-[18px] h-[18px]" /> : <Moon className="w-[18px] h-[18px]" />}
            </button>
            <button className={primaryButton} onClick={onLogin}>Ingresar</button>
          </div>
        </div>
      </header>

      <main>
        <section id="inicio" className="relative">
          <div className={cn(container, 'pt-16 sm:pt-24 text-center')}>
            <h1 className="mx-auto max-w-3xl text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight leading-[1.02] text-balance">
              Los casos urgentes, primero.
            </h1>
            <p className="mx-auto mt-6 max-w-xl text-lg sm:text-xl text-muted-foreground text-balance">
              Triage de cáncer de mama asistido por IA para la atención primaria.
            </p>
            <div className="mt-9 flex flex-wrap justify-center gap-3">
              <button className={cn(primaryButton, 'h-12 px-6 text-base')} onClick={onLogin}>
                Ingresar <ArrowRight aria-hidden className="w-4 h-4" />
              </button>
              <a
                href="#funciones"
                className="inline-flex items-center h-12 px-6 rounded-lg border border-input bg-card text-base font-semibold hover:bg-accent"
              >
                Ver funciones
              </a>
            </div>
          </div>

          <div className="relative mt-14 sm:mt-20">
            <div aria-hidden className="absolute inset-x-0 top-24 bottom-0 bg-muted border-t border-border" />
            <div className={cn(container, 'relative')}>
              <div className="rounded-2xl border border-border bg-card overflow-hidden shadow-[0_30px_60px_-30px_hsl(var(--shadow)/0.35)]">
                <div className="h-9 flex items-center gap-2 px-4 border-b border-border">
                  <span className="w-2.5 h-2.5 rounded-full bg-border" />
                  <span className="w-2.5 h-2.5 rounded-full bg-border" />
                  <span className="w-2.5 h-2.5 rounded-full bg-border" />
                  <span className="ml-3 text-xs text-muted-foreground">demo.auroracare.cl</span>
                </div>
                <img src={colaImg} alt="Cola de triage de Aurora Care con casos ordenados por prioridad" className="block w-full h-auto" />
              </div>
            </div>
            <div className="h-16 sm:h-20 relative" />
          </div>
        </section>

        <section id="funciones" className="scroll-mt-16">
          <div className={cn(container, 'py-20 sm:py-28')}>
            <FeatureShowcase />
          </div>
        </section>

        <section className={cn(container, 'pb-20 sm:pb-28')}>
          <div className="rounded-2xl bg-foreground text-background px-8 py-12 sm:px-14 sm:py-16 flex flex-col md:flex-row md:items-center md:justify-between gap-8">
            <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight leading-tight">
              Prioridades claras <br className="hidden sm:block" />
              para su equipo.
            </h2>
            <button className={cn(primaryButton, 'h-12 px-6 text-base self-start md:self-auto')} onClick={onLogin}>
              Ingresar a Aurora Care <ArrowRight aria-hidden className="w-4 h-4" />
            </button>
          </div>
        </section>
      </main>

      <footer className="border-t border-border">
        <div className={cn(container, 'py-8 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-sm text-muted-foreground')}>
          <div className="flex items-center gap-2">
            <BrandMark alt="" />
            <span className="font-bold text-foreground">Aurora Care</span>
            <span>© 2026</span>
          </div>
          <p>Apoya, no reemplaza, el criterio médico.</p>
        </div>
      </footer>
    </div>
  );
}
