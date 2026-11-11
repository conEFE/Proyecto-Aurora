import type { ReactNode } from 'react';
import {
  ArrowRight,
  ClipboardList,
  FileSignature,
  GraduationCap,
  Images,
  LockKeyhole,
  Moon,
  ScanEye,
  Scale,
  ShieldCheck,
  Stethoscope,
  Sun,
  UserRoundCheck,
} from 'lucide-react';
import { useTheme } from '../lib/theme';
import { cn } from '../lib/cn';
import type { TriageLevel } from '../types';
import { LevelBadge, SimulatedBadge } from './Badges';
import BrandMark from './BrandMark';
import { iconButton, primaryButton, secondaryButton } from './ui';

// Ejemplo ilustrativo con códigos ficticios (no son pacientes reales)
const SAMPLE_QUEUE: Array<{ code: string; level: TriageLevel; reason: string; wait: string }> = [
  { code: 'AUR-2026-000412', level: 'ALTA', reason: 'BI-RADS 4 informado', wait: '35 min' },
  { code: 'AUR-2026-000409', level: 'ALTA', reason: 'Masa palpable', wait: '1 h 10 min' },
  { code: 'AUR-2026-000415', level: 'MEDIA', reason: 'Antecedente familiar + edad', wait: '2 h' },
  { code: 'AUR-2026-000417', level: 'BAJA', reason: 'Control sin hallazgos', wait: '20 min' },
];

const STEPS: Array<{ icon: ReactNode; title: string; text: string }> = [
  {
    icon: <ClipboardList aria-hidden className="w-5 h-5" />,
    title: 'Registro con consentimiento',
    text: 'Admisión registra a la paciente con su RUT, antecedentes y consentimiento informado, y abre el caso con sus síntomas.',
  },
  {
    icon: <Images aria-hidden className="w-5 h-5" />,
    title: 'Imágenes del examen',
    text: 'Se cargan las vistas de la mamografía o la ecografía. Se guardan cifradas y un modelo de IA las analiza en segundo plano.',
  },
  {
    icon: <ScanEye aria-hidden className="w-5 h-5" />,
    title: 'Triage transparente',
    text: 'Reglas clínicas y factores ponderados asignan ALTA, MEDIA o BAJA, y muestran por qué. La cola ordena primero lo urgente.',
  },
  {
    icon: <FileSignature aria-hidden className="w-5 h-5" />,
    title: 'Revisión y firma médica',
    text: 'El médico valida cada resultado de la IA, ajusta el nivel si corresponde, registra su revisión y firma el reporte.',
  },
];

const PRINCIPLES: Array<{ icon: ReactNode; title: string; text: string }> = [
  {
    icon: <Stethoscope aria-hidden className="w-5 h-5" />,
    title: 'El médico decide',
    text: 'La IA y el triage sugieren. Toda sugerencia se puede corregir con un motivo, y queda registrada.',
  },
  {
    icon: <Scale aria-hidden className="w-5 h-5" />,
    title: 'Transparencia antes que magia',
    text: 'Cada nivel de prioridad muestra los factores que lo explican. Los parámetros los define el equipo médico.',
  },
  {
    icon: <UserRoundCheck aria-hidden className="w-5 h-5" />,
    title: 'Honestidad sobre la IA',
    text: 'El modelo es un prototipo sin validación clínica. Lo simulado se ve como simulado, y su desempeño se mide contra el juicio médico.',
  },
  {
    icon: <LockKeyhole aria-hidden className="w-5 h-5" />,
    title: 'Privacidad por diseño',
    text: 'Imágenes cifradas, bitácora de auditoría de solo agregar, y derechos de los titulares según las leyes 19.628, 21.719 y 20.584.',
  },
];

function SectionHeading({ eyebrow, title, children }: { eyebrow: string; title: string; children?: ReactNode }) {
  return (
    <div className="max-w-2xl">
      <p className="text-sm font-bold uppercase tracking-wider text-brand">{eyebrow}</p>
      <h2 className="mt-2 text-3xl sm:text-4xl font-extrabold tracking-tight">{title}</h2>
      {children && <p className="mt-4 text-lg text-muted-foreground leading-relaxed">{children}</p>}
    </div>
  );
}

/** Página pública de presentación de Aurora Care, con acceso al inicio de sesión. */
export default function Landing({ onLogin }: { onLogin: () => void }) {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-20 border-b border-border bg-background/85 backdrop-blur">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
          <a href="#inicio" className="flex items-center gap-2.5">
            <BrandMark alt="" />
            <span className="text-lg font-extrabold">Aurora Care</span>
          </a>
          <nav aria-label="Secciones" className="hidden md:flex items-center gap-6 text-sm font-semibold text-muted-foreground">
            <a href="#como-funciona" className="hover:text-foreground">Cómo funciona</a>
            <a href="#principios" className="hover:text-foreground">Principios</a>
            <a href="#quienes-somos" className="hover:text-foreground">Quiénes somos</a>
          </nav>
          <div className="flex items-center gap-2">
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
        {/* Portada */}
        <section id="inicio" className="relative overflow-hidden">
          <div aria-hidden className="pointer-events-none absolute inset-0">
            <div className="absolute -top-40 -left-32 w-[36rem] h-[36rem] rounded-full bg-brand/15 blur-3xl" />
            <div className="absolute top-10 right-[-10rem] w-[32rem] h-[32rem] rounded-full bg-[hsl(262_83%_58%/0.14)] blur-3xl" />
            <div className="absolute bottom-[-12rem] left-1/3 w-[28rem] h-[28rem] rounded-full bg-[hsl(190_80%_45%/0.10)] blur-3xl" />
          </div>
          <div className="relative mx-auto max-w-6xl px-4 sm:px-6 pt-16 pb-20 lg:pt-24 lg:pb-28 grid lg:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)] gap-12 items-center">
            <div>
              <p className="inline-flex items-center gap-2 rounded-full border border-border bg-card/70 px-3 py-1 text-sm font-semibold text-muted-foreground">
                <span aria-hidden className="w-2 h-2 rounded-full bg-brand" />
                Detección temprana de cáncer de mama
              </p>
              <h1 className="mt-6 text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-[1.05]">
                Los casos más urgentes, <span className="text-brand">primero</span>.
              </h1>
              <p className="mt-6 text-lg sm:text-xl text-muted-foreground leading-relaxed max-w-xl">
                Aurora Care ayuda a los equipos de atención primaria a priorizar los casos sospechosos de cáncer de mama:
                ordena la espera según el riesgo, explica cada prioridad y deja al médico la última palabra.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <button className={cn(primaryButton, 'h-12 px-6 text-base')} onClick={onLogin}>
                  Ingresar a la plataforma <ArrowRight aria-hidden className="w-4 h-4" />
                </button>
                <a href="#como-funciona" className={cn(secondaryButton, 'h-12 px-6 text-base')}>Cómo funciona</a>
              </div>
              <p className="mt-6 text-sm text-muted-foreground">La plataforma apoya, no reemplaza, el criterio médico.</p>
            </div>

            <div className="relative">
              <div className="relative rounded-2xl border border-border bg-card p-5 shadow-[0_24px_60px_-24px_hsl(var(--shadow)/0.45)]">
                <div className="flex items-center justify-between">
                  <p className="font-bold">Cola de triage</p>
                  <span className="text-xs text-muted-foreground">Ejemplo con datos ficticios</span>
                </div>
                <ul className="mt-4 divide-y divide-border">
                  {SAMPLE_QUEUE.map((q) => (
                    <li key={q.code} className="py-3 flex items-center gap-3">
                      <LevelBadge level={q.level} />
                      <span className="min-w-0 flex-1">
                        <span className="block font-bold tabular-nums">{q.code}</span>
                        <span className="block text-sm text-muted-foreground truncate">{q.reason}</span>
                      </span>
                      <span className="text-sm text-muted-foreground tabular-nums">{q.wait}</span>
                    </li>
                  ))}
                </ul>
                <div className="mt-3 pt-3 border-t border-border flex items-center gap-2 text-xs text-muted-foreground">
                  <SimulatedBadge /> Los resultados de IA de la demostración son simulados.
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* El problema */}
        <section className="border-y border-border bg-muted/50">
          <div className="mx-auto max-w-6xl px-4 sm:px-6 py-16 grid md:grid-cols-3 gap-10">
            <div className="md:col-span-1">
              <SectionHeading eyebrow="El problema" title="La espera no es igual para todas" />
            </div>
            <div className="md:col-span-2 space-y-4 text-lg text-muted-foreground leading-relaxed">
              <p>
                En un consultorio con alta demanda, una mamografía sospechosa puede quedar en la misma fila que un control de
                rutina. Cada día de espera importa cuando el diagnóstico es temprano.
              </p>
              <p>
                Aurora Care no diagnostica: <strong className="text-foreground">ordena</strong>. Reúne síntomas,
                antecedentes, el BI-RADS informado y el análisis de las imágenes para que el equipo médico vea primero los
                casos de mayor riesgo, sin perder la trazabilidad de ninguna decisión.
              </p>
            </div>
          </div>
        </section>

        {/* Cómo funciona */}
        <section id="como-funciona" className="mx-auto max-w-6xl px-4 sm:px-6 py-20 scroll-mt-16">
          <SectionHeading eyebrow="Cómo funciona" title="De la admisión a la firma del médico">
            Un caso por examen, con todas sus imágenes, y un nivel de prioridad que cualquiera del equipo puede entender.
          </SectionHeading>
          <ol className="mt-12 grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {STEPS.map((s, i) => (
              <li key={s.title} className="relative rounded-2xl border border-border bg-card p-6">
                <span className="absolute top-5 right-5 text-4xl font-extrabold text-border tabular-nums" aria-hidden>
                  {i + 1}
                </span>
                <span className="inline-flex items-center justify-center w-10 h-10 rounded-xl bg-brand/10 text-brand">
                  {s.icon}
                </span>
                <h3 className="mt-4 text-lg font-bold">{s.title}</h3>
                <p className="mt-2 text-muted-foreground leading-relaxed">{s.text}</p>
              </li>
            ))}
          </ol>
          <div className="mt-10 grid sm:grid-cols-3 gap-4">
            {(['ALTA', 'MEDIA', 'BAJA'] as TriageLevel[]).map((l) => (
              <div key={l} className="flex items-start gap-3 rounded-xl border border-border p-4">
                <LevelBadge level={l} />
                <p className="text-sm text-muted-foreground">
                  {l === 'ALTA' && 'Revisión prioritaria: hallazgos o síntomas de alarma. Notifica al equipo médico.'}
                  {l === 'MEDIA' && 'Riesgo intermedio: se revisa después de los casos ALTA, dentro del plazo definido.'}
                  {l === 'BAJA' && 'Sin señales de alarma: sigue el flujo habitual de control.'}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* Principios */}
        <section id="principios" className="border-y border-border bg-muted/50 scroll-mt-16">
          <div className="mx-auto max-w-6xl px-4 sm:px-6 py-20">
            <SectionHeading eyebrow="Principios" title="Tecnología al servicio del criterio clínico" />
            <div className="mt-12 grid sm:grid-cols-2 gap-5">
              {PRINCIPLES.map((p) => (
                <div key={p.title} className="flex gap-4 rounded-2xl border border-border bg-card p-6">
                  <span className="inline-flex items-center justify-center w-10 h-10 shrink-0 rounded-xl bg-brand/10 text-brand">
                    {p.icon}
                  </span>
                  <div>
                    <h3 className="text-lg font-bold">{p.title}</h3>
                    <p className="mt-1.5 text-muted-foreground leading-relaxed">{p.text}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Quiénes somos */}
        <section id="quienes-somos" className="mx-auto max-w-6xl px-4 sm:px-6 py-20 scroll-mt-16">
          <div className="grid lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] gap-12 items-center">
            <div>
              <SectionHeading eyebrow="Quiénes somos" title="Un equipo que quiere ganarle tiempo al diagnóstico" />
              <div className="mt-6 space-y-4 text-lg text-muted-foreground leading-relaxed">
                <p>
                  Aurora Care nace como proyecto de título en INACAP. Somos un equipo de estudiantes que unió desarrollo de
                  software, ciencia de datos e inteligencia artificial para un problema concreto de la atención primaria en
                  Chile: que los casos de mayor riesgo no esperen de más.
                </p>
                <p>
                  El nombre viene de la aurora, el primer momento del día: queremos que cada caso sospechoso se mire lo antes
                  posible. Trabajamos con datos ficticios y un modelo de IA en etapa de prototipo, con la mirada puesta en un
                  piloto responsable junto a equipos de salud.
                </p>
              </div>
            </div>
            <div className="grid sm:grid-cols-2 gap-4">
              <div className="rounded-2xl border border-border bg-card p-6">
                <GraduationCap aria-hidden className="w-6 h-6 text-brand" />
                <p className="mt-3 font-bold">Proyecto de título</p>
                <p className="mt-1 text-sm text-muted-foreground">INACAP · 2026</p>
              </div>
              <div className="rounded-2xl border border-border bg-card p-6">
                <ShieldCheck aria-hidden className="w-6 h-6 text-brand" />
                <p className="mt-3 font-bold">Normativa chilena</p>
                <p className="mt-1 text-sm text-muted-foreground">Consentimiento, auditoría y derechos de los titulares.</p>
              </div>
              <div className="sm:col-span-2 rounded-2xl border border-border bg-card p-6 flex items-center gap-5">
                <BrandMark alt="" size="lg" className="w-28 h-20" />
                <p className="text-muted-foreground">
                  Hecho para el día a día de un CESFAM: claro para admisión, completo para el médico y trazable para la
                  institución.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Llamado final */}
        <section className="mx-auto max-w-6xl px-4 sm:px-6 pb-20">
          <div className="relative overflow-hidden rounded-3xl bg-primary px-6 py-14 sm:px-12 text-center text-primary-foreground">
            <div aria-hidden className="pointer-events-none absolute -top-24 -right-24 w-80 h-80 rounded-full bg-white/10 blur-2xl" />
            <h2 className="relative text-3xl sm:text-4xl font-extrabold tracking-tight">¿Parte del equipo de salud?</h2>
            <p className="relative mt-3 text-lg opacity-90">Ingrese con el RUT y la contraseña que le entregó el administrador.</p>
            <button
              onClick={onLogin}
              className="relative mt-8 inline-flex items-center gap-2 h-12 px-7 rounded-lg bg-white text-[hsl(324_31%_12%)] font-bold hover:bg-white/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-primary"
            >
              Ingresar a Aurora Care <ArrowRight aria-hidden className="w-4 h-4" />
            </button>
          </div>
        </section>
      </main>

      <footer className="border-t border-border">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 py-8 flex flex-col sm:flex-row items-center justify-between gap-3 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <BrandMark alt="" />
            <span className="font-bold text-foreground">Aurora Care</span>
            <span>· Proyecto de título INACAP</span>
          </div>
          <p>La plataforma apoya, no reemplaza, el criterio médico.</p>
        </div>
      </footer>
    </div>
  );
}
