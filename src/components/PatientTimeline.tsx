import { useEffect, useState } from 'react';
import {
  Ban,
  CheckCircle2,
  FileCheck2,
  FolderPlus,
  Images,
  Lock,
  ShieldCheck,
  ShieldOff,
  SlidersHorizontal,
  UserPlus,
  type LucideIcon,
} from 'lucide-react';
import { apiClient } from '../services/api';
import type { TimelineEvent, TimelineKind } from '../types';
import { RECOMMENDATION_LABELS } from '../types';
import { LEVEL_LABELS } from '../constants';
import { cn } from '../lib/cn';
import { ErrorMessage, Loading } from './Feedback';
import { cardClass, formatDateTime, sectionTitle } from './ui';

const KIND: Record<TimelineKind, { icon: LucideIcon; title: string; tone: string }> = {
  PATIENT_REGISTERED: { icon: UserPlus, title: 'Paciente registrada', tone: 'text-brand' },
  CONSENT_GRANTED: { icon: ShieldCheck, title: 'Consentimiento otorgado', tone: 'text-baja' },
  CONSENT_WITHDRAWN: { icon: ShieldOff, title: 'Consentimiento retirado', tone: 'text-media' },
  PATIENT_BLOCKED: { icon: Ban, title: 'Datos bloqueados', tone: 'text-alta' },
  CASE_CREATED: { icon: FolderPlus, title: 'Caso creado', tone: 'text-brand' },
  IMAGES_UPLOADED: { icon: Images, title: 'Imágenes cargadas', tone: 'text-muted-foreground' },
  TRIAGE_OVERRIDE: { icon: SlidersHorizontal, title: 'Prioridad ajustada por el médico', tone: 'text-media' },
  REVIEW_REGISTERED: { icon: FileCheck2, title: 'Revisión médica registrada', tone: 'text-baja' },
  CASE_CLOSED: { icon: Lock, title: 'Caso cerrado', tone: 'text-muted-foreground' },
};

function describe(e: TimelineEvent): string | null {
  const d = e.detail;
  switch (e.kind) {
    case 'CONSENT_GRANTED':
      return d.version ? `Texto versión ${d.version}` : null;
    case 'CONSENT_WITHDRAWN':
      return d.note ?? null;
    case 'PATIENT_BLOCKED':
      return d.reason ?? null;
    case 'CASE_CREATED': {
      const parts: string[] = [];
      if (d.triage_level) parts.push(`Prioridad actual: ${LEVEL_LABELS[d.triage_level].toLowerCase()}`);
      if (d.symptoms?.length) parts.push(`Síntomas: ${d.symptoms.join(', ')}`);
      return parts.join(' · ') || null;
    }
    case 'IMAGES_UPLOADED':
      return d.count === 1 ? '1 imagen' : `${d.count} imágenes`;
    case 'TRIAGE_OVERRIDE':
      return d.computed_level && d.final_level
        ? `De ${LEVEL_LABELS[d.computed_level].toLowerCase()} a ${LEVEL_LABELS[d.final_level].toLowerCase()}${d.reason ? ` · ${d.reason}` : ''}`
        : null;
    case 'REVIEW_REGISTERED':
      return d.birads_final !== undefined && d.recommendation
        ? `BI-RADS ${d.birads_final} · ${RECOMMENDATION_LABELS[d.recommendation]}`
        : null;
    default:
      return null;
  }
}

interface PatientTimelineProps {
  patientId: number;
  /** Cambia cuando se recargan los casos o el consentimiento, para volver a pedir la historia. */
  refreshKey?: unknown;
  onOpenCase: (caseId: number) => void;
}

/** Historia del paciente: registro, consentimiento, casos, imágenes, triage y revisión, del más reciente al más antiguo. */
export default function PatientTimeline({ patientId, refreshKey, onOpenCase }: PatientTimelineProps) {
  const [events, setEvents] = useState<TimelineEvent[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setEvents(null);
    apiClient.getPatientTimeline(patientId).then((r) => {
      if (!active) return;
      if (r.data) {
        setEvents(r.data);
        setError(null);
      } else setError(r.error || 'No se pudo cargar la historia del paciente.');
    });
    return () => {
      active = false;
    };
  }, [patientId, refreshKey]);

  return (
    <section className={cn(cardClass, 'p-6')} aria-labelledby="pt-title">
      <h3 id="pt-title" className={sectionTitle}>Historia</h3>
      <ErrorMessage className="mt-3">{error}</ErrorMessage>
      {events === null && !error ? (
        <Loading label="Cargando historia…" />
      ) : events && events.length > 0 ? (
        <ol className="mt-4 relative border-l border-border ml-3">
          {events.map((e, i) => {
            const { icon: Icon, title, tone } = KIND[e.kind] ?? { icon: CheckCircle2, title: e.kind, tone: '' };
            const text = describe(e);
            return (
              <li key={`${e.kind}-${e.at}-${i}`} className="relative pl-6 pb-5 last:pb-0">
                <span className="absolute -left-3 top-0 grid place-items-center w-6 h-6 rounded-full bg-card ring-1 ring-border">
                  <Icon aria-hidden className={cn('w-3.5 h-3.5', tone)} />
                </span>
                <p className="text-sm font-bold leading-6">
                  {title}
                  {e.case_code && e.case_id !== null && (
                    <>
                      {' · '}
                      <button className="tabular-nums hover:text-brand hover:underline" onClick={() => onOpenCase(e.case_id!)}>
                        {e.case_code}
                      </button>
                    </>
                  )}
                </p>
                {text && <p className="text-sm text-foreground/90">{text}</p>}
                <p className="text-xs text-muted-foreground tabular-nums">
                  <time dateTime={e.at}>{formatDateTime(e.at)}</time>
                  {e.actor_name ? ` · ${e.actor_name}` : ''}
                </p>
              </li>
            );
          })}
        </ol>
      ) : (
        events && <p className="mt-3 text-sm text-muted-foreground">Sin movimientos registrados.</p>
      )}
    </section>
  );
}
