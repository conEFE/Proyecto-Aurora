import type { AIVerdict, AuditEntry, ExamType, Recommendation, Role, TriageAssessment } from '../types';
import {
  AI_VERDICT_LABELS,
  DATA_REQUEST_STATUS_LABELS,
  DATA_REQUEST_TYPE_LABELS,
  EXAM_TYPE_LABELS,
  RECOMMENDATION_LABELS,
  ROLE_LABELS,
  TRIAGE_ASSESSMENT_LABELS,
} from '../types';
import type { DataRequestStatus, DataRequestType } from '../types';

/** Grupos de acciones para filtrar la bitácora sin conocer sus códigos. */
export const AUDIT_GROUPS = {
  ingresos: { label: 'Ingresos', actions: ['LOGIN_OK', 'LOGIN_FAIL'] },
  seguridad: { label: 'Alertas de seguridad', actions: ['LOGIN_FAIL', 'PASSWORD_CHANGE_FAIL', 'SIGN_FAIL'] },
  cambios: {
    label: 'Cambios',
    actions: ['CREATE', 'UPDATE', 'DELETE', 'OVERRIDE', 'CONFIG_CHANGE', 'SIGN', 'PASSWORD_CHANGE', 'CONSENT_GRANT', 'CONSENT_WITHDRAW', 'BLOCK', 'UNBLOCK'],
  },
  consultas: { label: 'Consultas y descargas', actions: ['VIEW', 'DOWNLOAD', 'EXPORT'] },
} as const;
export type AuditGroup = keyof typeof AUDIT_GROUPS;

/** Acciones que conviene destacar: fallas de seguridad. */
export const SECURITY_ACTIONS = new Set<string>(AUDIT_GROUPS.seguridad.actions);

const FAIL_REASONS: Record<string, string> = {
  credenciales: 'RUT o contraseña incorrectos',
  bloqueado: 'cuenta bloqueada por intentos fallidos',
  inactivo: 'cuenta desactivada',
  limite_ip: 'demasiados intentos desde la misma red',
  actual_incorrecta: 'contraseña actual incorrecta',
  politica: 'la nueva no cumple la política',
  password: 'contraseña incorrecta',
};

const FIELD_LABELS: Record<string, string> = {
  role: 'rol',
  is_active: 'estado',
  email: 'email',
  full_name: 'nombre',
  password: 'contraseña',
  locked_until: 'bloqueo',
  palpable_mass: 'síntomas',
  nipple_discharge: 'síntomas',
  skin_or_nipple_changes: 'síntomas',
  birads_reported: 'BI-RADS informado',
};

const n = (v: unknown) => (typeof v === 'number' ? v.toLocaleString('es-CL') : String(v));
const fields = (list: unknown) =>
  Array.isArray(list) ? [...new Set(list.map((f) => FIELD_LABELS[String(f)] ?? String(f).replace(/_/g, ' ')))].join(', ') : '';

export interface AuditText {
  title: string;
  detail?: string;
}

/** Describe un registro de la bitácora en lenguaje simple, sin códigos internos ni JSON. */
export function describeAudit(e: AuditEntry): AuditText {
  const d = (e.detail ?? {}) as Record<string, unknown>;
  const reason = d.reason ? FAIL_REASONS[String(d.reason)] ?? String(d.reason) : undefined;
  const caseRef = d.case_id ? `caso n.º ${d.case_id}` : e.entity === 'case' && e.entity_id ? `caso n.º ${e.entity_id}` : '';

  switch (e.action) {
    case 'LOGIN_OK':
      return { title: 'Inició sesión' };
    case 'LOGIN_FAIL':
      return { title: 'Ingreso fallido', detail: reason };
    case 'PASSWORD_CHANGE':
      return { title: 'Cambió su contraseña', detail: d.forced ? 'Cambio obligatorio del primer ingreso' : undefined };
    case 'PASSWORD_CHANGE_FAIL':
      return { title: 'Cambio de contraseña fallido', detail: reason };
    case 'SIGN':
      return { title: 'Firmó un reporte', detail: caseRef };
    case 'SIGN_FAIL':
      return { title: 'Firma fallida', detail: [reason, caseRef].filter(Boolean).join(' · ') };
    case 'OVERRIDE':
      return {
        title: 'Ajustó el nivel de triage',
        detail: [d.from && d.to ? `${d.from} → ${d.to}` : '', caseRef].filter(Boolean).join(' · '),
      };
    case 'CONFIG_CHANGE':
      return { title: 'Cambió los parámetros de triage', detail: d.version ? `Versión ${d.previous_version} → ${d.version}` : undefined };
    case 'CONSENT_GRANT':
      return { title: 'Registró un consentimiento', detail: d.version ? `Texto ${d.version}` : undefined };
    case 'CONSENT_WITHDRAW':
      return { title: 'Registró el retiro de un consentimiento' };
    case 'BLOCK':
      return { title: 'Bloqueó los datos de un paciente' };
    case 'UNBLOCK':
      return { title: 'Levantó el bloqueo de un paciente' };
    case 'DELETE':
      return { title: e.entity === 'patient' ? 'Eliminó un paciente sin casos' : 'Eliminó un registro' };
    case 'DOWNLOAD':
      return { title: 'Descargó un archivo', detail: caseRef };
    case 'EXPORT':
      return e.entity === 'patient'
        ? { title: 'Exportó los datos de un paciente', detail: d.cases !== undefined ? `${n(d.cases)} casos` : undefined }
        : { title: 'Generó el PDF de un reporte', detail: caseRef };
  }

  if (e.action === 'VIEW') {
    if (e.entity === 'triage') {
      if (d.queue) return { title: 'Consultó la cola de triage', detail: d.results !== undefined ? `${n(d.results)} casos` : undefined };
      return { title: d.history ? 'Vio el historial de triage' : 'Vio el triage de un caso', detail: caseRef };
    }
    if (e.entity === 'patient') {
      if (d.list) return { title: 'Buscó pacientes', detail: d.results !== undefined ? `${n(d.results)} resultados` : undefined };
      if (d.timeline) return { title: 'Vio la historia de un paciente' };
      return { title: 'Abrió la ficha de un paciente' };
    }
    if (e.entity === 'case') return { title: d.review ? 'Vio la revisión de un caso' : 'Abrió un caso', detail: caseRef };
    if (e.entity === 'image') return { title: d.inference ? 'Vio el resultado de IA de una imagen' : 'Vio una imagen', detail: caseRef };
    return { title: 'Consultó un registro' };
  }

  if (e.action === 'CREATE' || e.action === 'UPDATE') {
    const created = e.action === 'CREATE';
    switch (e.entity) {
      case 'user':
        if (created) return { title: 'Creó un usuario', detail: d.role ? ROLE_LABELS[d.role as Role] : undefined };
        if (d.unlock) return { title: 'Desbloqueó una cuenta' };
        if (d.self_service) return { title: 'Cambió su email' };
        if (d.is_active === false) return { title: 'Desactivó un usuario' };
        if (d.is_active === true) return { title: 'Activó un usuario' };
        if (d.role) return { title: 'Cambió el rol de un usuario', detail: ROLE_LABELS[d.role as Role] };
        if (Array.isArray(d.fields) && d.fields.includes('password')) return { title: 'Asignó una contraseña temporal' };
        return { title: 'Modificó un usuario', detail: fields(d.fields) };
      case 'case':
        if (d.review_id)
          return {
            title: 'Registró la revisión médica y cerró el caso',
            detail: [
              d.recommendation ? RECOMMENDATION_LABELS[d.recommendation as Recommendation] : '',
              d.triage_assessment ? `triage ${TRIAGE_ASSESSMENT_LABELS[d.triage_assessment as TriageAssessment].split(' (')[0].toLowerCase()}` : '',
            ]
              .filter(Boolean)
              .join(' · '),
          };
        if (created) return { title: 'Creó un caso', detail: d.code ? String(d.code) : undefined };
        if (d.assigned) return { title: 'Tomó un caso para revisión', detail: caseRef };
        return { title: 'Editó un caso', detail: [fields(d.fields), caseRef].filter(Boolean).join(' · ') };
      case 'image':
        if (d.ai_validation)
          return {
            title: d.previous ? 'Corrigió la validación de un resultado de IA' : 'Validó un resultado de IA',
            detail: [AI_VERDICT_LABELS[d.ai_validation as AIVerdict], d.ai_simulated ? 'IA simulada' : '', caseRef].filter(Boolean).join(' · '),
          };
        if (d.reanalyzed) return { title: 'Volvió a analizar una imagen con el modelo', detail: caseRef };
        return {
          title: 'Cargó una imagen',
          detail: [d.exam_type ? EXAM_TYPE_LABELS[d.exam_type as ExamType] : '', caseRef].filter(Boolean).join(' · '),
        };
      case 'triage':
        return { title: 'Recalculó el triage', detail: caseRef };
      case 'patient':
        return { title: created ? 'Registró un paciente' : 'Editó la ficha de un paciente' };
      case 'data_subject_request':
        return created
          ? { title: 'Registró una solicitud de titular', detail: d.type ? DATA_REQUEST_TYPE_LABELS[d.type as DataRequestType] : undefined }
          : { title: 'Actualizó una solicitud de titular', detail: d.status ? DATA_REQUEST_STATUS_LABELS[d.status as DataRequestStatus] : undefined };
    }
  }
  return { title: 'Acción registrada' };
}

/** Quién aparece cuando el registro no tiene usuario (p. ej., un ingreso con un RUT que no existe). */
export function actorFallback(e: AuditEntry): string {
  return e.action === 'LOGIN_FAIL' ? 'RUT no registrado' : 'Sistema';
}

/** «hace 5 min», «hace 3 h», «ayer», o la fecha. */
export function relativeTime(iso: string, now = Date.now()): string {
  const diff = (now - new Date(iso).getTime()) / 1000;
  if (diff < 60) return 'recién';
  if (diff < 3600) return `hace ${Math.floor(diff / 60)} min`;
  if (diff < 86400) return `hace ${Math.floor(diff / 3600)} h`;
  if (diff < 172800) return 'ayer';
  if (diff < 30 * 86400) return `hace ${Math.floor(diff / 86400)} días`;
  return new Date(iso).toLocaleDateString('es-CL');
}
