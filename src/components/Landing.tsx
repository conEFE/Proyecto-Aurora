import type { ReactNode } from 'react';
import { ArrowRight, Moon, Sun } from 'lucide-react';
import { useTheme } from '../lib/theme';
import { cn } from '../lib/cn';
import type { TriageLevel } from '../types';
import { LevelBadge, SimulatedBadge } from './Badges';
import BrandMark from './BrandMark';
import { iconButton, primaryButton } from './ui';

// Ejemplo ilustrativo con códigos ficticios (no son pacientes reales)
const SAMPLE_QUEUE: Array<{ code: string; level: TriageLevel; reason: string; wait: string }> = [
  { code: 'AUR-2026-000412', level: 'ALTA', reason: 'BI-RADS 4 informado', wait: '35 min' },
  { code: 'AUR-2026-000409', level: 'ALTA', reason: 'Masa palpable', wait: '1 h 10 min' },
  { code: 'AUR-2026-000415', level: 'MEDIA', reason: 'Antecedente familiar + edad', wait: '2 h' },
  { code: 'AUR-2026-000417', level: 'BAJA', reason: 'Control sin hallazgos', wait: '20 min' },
];

const STEPS: Array<{ title: string; text: string }> = [
  {
    title: 'Registro con consentimiento',
    text: 'Admisión registra a la paciente con su RUT, antecedentes y consentimiento informado, y abre el caso con sus síntomas.',
  },
  {
    title: 'Imágenes del examen',
    text: 'Se cargan las vistas de la mamografía o la ecografía. Se guardan cifradas y un modelo de IA las analiza en segundo plano.',
  },
  {
    title: 'Triage transparente',
    text: 'Reglas clínicas y factores ponderados asignan ALTA, MEDIA o BAJA, y muestran por qué. La cola ordena primero lo urgente.',
  },
  {
    title: 'Revisión y firma médica',
    text: 'El médico valida cada resultado de la IA, ajusta el nivel si corresponde, registra su revisión y firma el reporte.',
  },
];

const LEVELS: Array<{ level: TriageLevel; text: string }> = [
  { level: 'ALTA', text: 'Revisión prioritaria: hallazgos o síntomas de alarma. Notifica al equipo médico.' },
  { level: 'MEDIA', text: 'Riesgo intermedio: se revisa después de los casos ALTA, dentro del plazo definido.' },
  { level: 'BAJA', text: 'Sin señales de alarma: sigue el flujo habitual de control.' },
];

const PRINCIPLES: Array<{ title: string; text: string }> = [
  {
    title: 'El médico decide',
    text: 'La IA y el triage sugieren. Toda sugerencia se puede corregir con un motivo, y queda registrada.',
  },
  {
    title: 'Transparencia antes que magia',
    text: 'Cada nivel de prioridad muestra los factores que lo explican. Los parámetros los define el equipo médico.',
  },
  {
    title: 'Honestidad sobre la IA',
    text: 'El modelo es un prototipo sin validación clínica. Lo simulado se ve como simulado, y su desempeño se mide contra el juicio médico.',
  },
  {
    title: 'Privacidad por diseño',
    text: 'Imágenes cifradas, bitácora de auditoría de solo agregar, y derechos de los titulares según las leyes 19.628, 21.719 y 20.584.',
  },
];

const FACTS: Array<{ label: string; value: string }> = [
  { label: 'Origen', value: 'Proyecto de título, INACAP · 2026' },
  { label: 'Pensado para', value: 'Equipos de atención primaria (CESFAM y consultorios)' },
  { label: 'Datos', value: 'Ficticios, con RUT de prueba' },
  { label: 'Modelo de IA', value: 'Prototipo, sin validación clínica' },
  { label: 'Normativa', value: 'Consentimiento informado, auditoría y leyes 19.628, 21.719 y 20.584' },
];

const container = 'mx-auto max-w-6xl px-4 sm:px-6';

/** Sección con el título en la columna izquierda y el contenido a la derecha, separada por una regla. */
function Section({ id, title, intro, children }: { id?: string; title: string; intro?: ReactNode; children?: ReactNode }) {
  return (
    <section id={id} className="scroll-mt-16 border-t border-border">
      <div className={cn(container, 'py-16 lg:py-24 grid lg:grid-cols-12 gap-x-12 gap-y-8')}>
        <div className="lg:col-span-4">
          <h2 className="text-3xl font-extrabold tracking-tight leading-tight text-balance">{title}</h2>
          {intro && <p className="mt-4 text-muted-foreground leading-relaxed max-w-md">{intro}</p>}
        </div>
        <div className="lg:col-span-8">{children}</div>
      </div>
    </section>
  );
}

/** Página pública de presentación de Aurora Care, con acceso al inicio de sesión. */
export default function Landing({ onLogin }: { onLogin: () => void }) {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-20 border-b border-border bg-background">
        <div className={cn(container, 'h-16 flex items-center justify-between gap-4')}>
          <a href="#inicio" className="flex items-center gap-2.5 rounded-md">
            <BrandMark alt="" />
            <span className="text-lg font-extrabold">Aurora Care</span>
          </a>
          <nav aria-label="Secciones" className="hidden md:flex items-center gap-7 text-sm font-semibold text-muted-foreground">
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
        <section id="inicio" className={cn(container, 'pt-16 pb-20 lg:pt-28 lg:pb-28')}>
          <h1 className="max-w-4xl text-4xl sm:text-5xl lg:text-[4.25rem] font-extrabold tracking-tight leading-[1.04] text-balance">
            Los casos más urgentes, primero.
          </h1>
          <div className="mt-12 lg:mt-16 grid lg:grid-cols-12 gap-x-12 gap-y-12">
            <div className="lg:col-span-5">
              <p className="text-lg sm:text-xl text-muted-foreground leading-relaxed">
                Aurora Care ayuda a los equipos de atención primaria a priorizar los casos sospechosos de cáncer de mama:
                ordena la espera según el riesgo, explica cada prioridad y deja al médico la última palabra.
              </p>
              <div className="mt-8 flex flex-wrap items-center gap-x-6 gap-y-4">
                <button className={cn(primaryButton, 'h-12 px-6 text-base')} onClick={onLogin}>
                  Ingresar a la plataforma <ArrowRight aria-hidden className="w-4 h-4" />
                </button>
                <a
                  href="#como-funciona"
                  className="text-base font-semibold underline decoration-border underline-offset-4 hover:decoration-current rounded-sm"
                >
                  Cómo funciona
                </a>
              </div>
              <p className="mt-8 text-sm text-muted-foreground">La plataforma apoya, no reemplaza, el criterio médico.</p>
            </div>

            {/* Cola de ejemplo, con la misma forma que la tabla real */}
            <figure className="lg:col-span-7">
              <figcaption className="flex items-baseline justify-between gap-4 pb-3 border-b-2 border-foreground">
                <span className="font-bold">Cola de triage</span>
                <span className="text-xs text-muted-foreground">Ejemplo con datos ficticios</span>
              </figcaption>
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs font-semibold text-muted-foreground">
                    <th scope="col" className="py-2.5 pr-3 font-semibold border-b border-border">Nivel</th>
                    <th scope="col" className="py-2.5 px-3 font-semibold border-b border-border">Caso</th>
                    <th scope="col" className="hidden sm:table-cell py-2.5 px-3 font-semibold border-b border-border">Motivo</th>
                    <th scope="col" className="py-2.5 pl-3 font-semibold border-b border-border text-right">Espera</th>
                  </tr>
                </thead>
                <tbody>
                  {SAMPLE_QUEUE.map((q) => (
                    <tr key={q.code}>
                      <td className="py-3 pr-3 border-b border-border whitespace-nowrap"><LevelBadge level={q.level} /></td>
                      <td className="py-3 px-3 border-b border-border">
                        <span className="block font-extrabold tabular-nums whitespace-nowrap">{q.code}</span>
                        <span className="sm:hidden block text-muted-foreground">{q.reason}</span>
                      </td>
                      <td className="hidden sm:table-cell py-3 px-3 border-b border-border text-muted-foreground">{q.reason}</td>
                      <td className="py-3 pl-3 border-b border-border text-right tabular-nums whitespace-nowrap text-muted-foreground">{q.wait}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="mt-3 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                <SimulatedBadge /> Los resultados de IA de la demostración son simulados.
              </p>
            </figure>
          </div>
        </section>

        <Section title="La espera no es igual para todas">
          <div className="max-w-2xl space-y-5 text-lg leading-relaxed text-muted-foreground">
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
        </Section>

        <Section
          id="como-funciona"
          title="De la admisión a la firma del médico"
          intro="Un caso por examen, con todas sus imágenes, y un nivel de prioridad que cualquiera del equipo puede entender."
        >
          <ol className="border-t-2 border-foreground">
            {STEPS.map((s, i) => (
              <li key={s.title} className="grid grid-cols-[2.5rem_minmax(0,1fr)] sm:grid-cols-[3rem_14rem_minmax(0,1fr)] gap-x-4 gap-y-1 py-5 border-b border-border">
                <span className="font-extrabold tabular-nums text-muted-foreground">{String(i + 1).padStart(2, '0')}</span>
                <h3 className="font-bold">{s.title}</h3>
                <p className="col-start-2 sm:col-start-3 text-muted-foreground leading-relaxed">{s.text}</p>
              </li>
            ))}
          </ol>

          <h3 className="mt-14 font-bold">Tres niveles, una sola escala</h3>
          <dl className="mt-4 border-t-2 border-foreground">
            {LEVELS.map((l) => (
              <div key={l.level} className="grid grid-cols-[6.5rem_minmax(0,1fr)] sm:grid-cols-[17.5rem_minmax(0,1fr)] gap-x-4 py-4 border-b border-border">
                <dt><LevelBadge level={l.level} /></dt>
                <dd className="text-muted-foreground leading-relaxed">{l.text}</dd>
              </div>
            ))}
          </dl>
        </Section>

        <Section id="principios" title="Tecnología al servicio del criterio clínico">
          <dl className="grid sm:grid-cols-2 gap-x-12">
            {PRINCIPLES.map((p) => (
              <div key={p.title} className="py-6 border-t border-border">
                <dt className="text-lg font-bold">{p.title}</dt>
                <dd className="mt-2 text-muted-foreground leading-relaxed">{p.text}</dd>
              </div>
            ))}
          </dl>
        </Section>

        <Section id="quienes-somos" title="Un equipo que quiere ganarle tiempo al diagnóstico">
          <div className="max-w-2xl space-y-5 text-lg leading-relaxed text-muted-foreground">
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
          <dl className="mt-12 border-t-2 border-foreground">
            {FACTS.map((f) => (
              <div key={f.label} className="grid sm:grid-cols-[12rem_minmax(0,1fr)] gap-x-4 gap-y-0.5 py-3.5 border-b border-border">
                <dt className="text-sm font-semibold text-muted-foreground">{f.label}</dt>
                <dd>{f.value}</dd>
              </div>
            ))}
          </dl>
        </Section>

        {/* Acceso */}
        <section className="border-t border-border">
          <div className={cn(container, 'py-16 lg:py-20 flex flex-col md:flex-row md:items-end md:justify-between gap-8')}>
            <div>
              <h2 className="text-3xl font-extrabold tracking-tight">¿Parte del equipo de salud?</h2>
              <p className="mt-3 text-lg text-muted-foreground">Ingrese con el RUT y la contraseña que le entregó el administrador.</p>
            </div>
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
            <span>· Proyecto de título INACAP</span>
          </div>
          <p>La plataforma apoya, no reemplaza, el criterio médico.</p>
        </div>
      </footer>
    </div>
  );
}
