export type Role = 'ADMIN' | 'MEDICO' | 'ADMINISTRATIVO';

export const ROLE_LABELS: Record<Role, string> = {
  ADMIN: 'Administrador',
  MEDICO: 'Médico',
  ADMINISTRATIVO: 'Administrativo',
};

export interface Me {
  id: number;
  rut: string;
  email: string;
  full_name: string;
  role: Role;
  must_change_password: boolean;
  created_at?: string | null;
  last_login_at?: string | null;
  password_changed_at?: string | null;
}

export interface UserAccount {
  id: number;
  rut: string;
  email: string;
  full_name: string;
  role: Role;
  is_active: boolean;
  created_at?: string | null;
  last_login_at?: string | null;
  must_change_password?: boolean;
  locked_until?: string | null;
}

export interface UserCreateInput {
  rut: string;
  email: string;
  full_name: string;
  password: string;
  role: Role;
}

export type UserUpdateInput = Partial<Omit<UserCreateInput, 'rut'>> & { is_active?: boolean };

export type Sex = 'F' | 'M' | 'O';

export interface Patient {
  id: number;
  rut: string;
  first_name: string;
  last_name: string;
  birth_date: string;
  sex?: Sex | null;
  medical_history?: string | null;
  family_history_first_degree: boolean;
  previous_breast_cancer: boolean;
  consent_given: boolean;
  consent_at?: string | null;
  consent_registered_by?: number | null;
  consent_text_version?: string | null;
  blocked_at?: string | null;
  block_reason?: string | null;
  created_by?: number | null;
  created_at?: string | null;
}

export interface PatientInput {
  rut: string;
  first_name: string;
  last_name: string;
  birth_date: string;
  sex?: Sex | null;
  medical_history?: string | null;
  family_history_first_degree: boolean;
  previous_breast_cancer: boolean;
  consent_given: boolean;
  /** Versión del texto de consentimiento mostrado al paciente (obligatoria al registrar). */
  consent_text_version?: string;
}

export interface AuditEntry {
  id: number;
  user_id: number | null;
  action: string;
  entity: string;
  entity_id: number | null;
  ip_address: string | null;
  detail: Record<string, unknown> | null;
  created_at: string;
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}

export type CaseStatus = 'ABIERTO' | 'PRIORIZADO' | 'EN_REVISION' | 'CERRADO';

export const CASE_STATUS_LABELS: Record<CaseStatus, string> = {
  ABIERTO: 'Abierto',
  PRIORIZADO: 'Priorizado',
  EN_REVISION: 'En revisión',
  CERRADO: 'Cerrado',
};

export interface CaseSymptoms {
  palpable_mass: boolean;
  nipple_discharge: boolean;
  skin_or_nipple_changes: boolean;
  birads_reported: number | null;
}

export interface PatientSummary {
  id: number;
  rut: string;
  first_name: string;
  last_name: string;
  birth_date: string;
  family_history_first_degree: boolean;
  previous_breast_cancer: boolean;
}

export interface ClinicalCase extends CaseSymptoms {
  id: number;
  code: string;
  status: CaseStatus;
  patient_id: number;
  patient?: PatientSummary | null;
  created_by: number;
  assigned_medico_id?: number | null;
  created_at: string;
  updated_at?: string | null;
  closed_at?: string | null;
  image_count: number;
  triage_level?: TriageLevel | null;
}

export type TriageLevel = 'ALTA' | 'MEDIA' | 'BAJA';

export interface TriageFactor {
  value: number | boolean;
  normalized: number;
  weight: number;
  points: number;
}

export interface TriageBreakdown {
  ai: TriageFactor;
  age: TriageFactor;
  family_history: TriageFactor;
  previous_cancer: TriageFactor;
  wait_time: TriageFactor;
  escalation_rule: string | null;
  ai_is_simulated: boolean | null;
  ai_is_prototype?: boolean | null;
  images_analyzed?: number;
}

export interface TriageResult {
  id: number;
  case_id: number;
  config_version: number;
  score: number;
  computed_level: TriageLevel;
  escalation_rule: string | null;
  breakdown: TriageBreakdown | null;
  final_level: TriageLevel;
  override_by: number | null;
  override_reason: string | null;
  is_current: boolean;
  computed_at: string;
}

export interface QueueItem {
  code: string;
  level: TriageLevel;
  status: CaseStatus;
  waiting_hours: number;
  case_id?: number;
  score?: number;
  escalation_rule?: string | null;
  overridden?: boolean;
  patient_name?: string;
  created_at?: string;
}

export interface TriageParams {
  escalation: { birads_alta: number[]; symptoms_alta: boolean };
  weights: { ai: number; age: number; family_history: number; previous_cancer: number; wait_time: number };
  age_bands: { high: [number, number]; medium: Array<[number, number]> };
  max_wait_days: number;
  thresholds: { alta: number; media: number };
}

export interface TriageConfig {
  id: number;
  version: number;
  params: TriageParams;
  is_active: boolean;
  created_by: number | null;
  created_at: string | null;
  change_reason: string;
}

export interface AppNotification {
  id: number;
  case_id: number;
  message: string;
  read_at: string | null;
  created_at: string | null;
}

export type ExamType = 'MAMOGRAFIA' | 'ECOGRAFIA' | 'OTRO';

export const EXAM_TYPE_LABELS: Record<ExamType, string> = {
  MAMOGRAFIA: 'Mamografía',
  ECOGRAFIA: 'Ecografía',
  OTRO: 'Otro',
};

export type Laterality = 'L' | 'R';

export interface Detection {
  x: number;
  y: number;
  width: number;
  height: number;
  confidence: number;
  class_name: string;
  /** Área de la caja sobre el área de la imagen (0 a 1). Solo en resultados del modelo real. */
  relative_area?: number;
}

export interface InferenceResult {
  image_id: number;
  detected: boolean;
  confidence: number;
  detections?: Detection[] | null;
  processing_time_ms: number;
  model_version: string;
  is_simulated: boolean;
  /** Solo un modelo con validación clínica formal; el prototipo actual no la tiene. */
  clinically_validated?: boolean;
  message: string;
  created_at?: string | null;
}

export interface InferenceStatus {
  provider: 'simulated' | 'http';
  reachable: boolean | null;
  fallback: boolean;
  model_version?: string | null;
  device?: string | null;
  clinically_validated?: boolean;
  error?: string | null;
}

export interface CaseImage {
  id: number;
  case_id: number;
  filename: string;
  mime_type: string;
  width?: number | null;
  height?: number | null;
  size_kb?: number | null;
  exam_type: ExamType;
  laterality?: Laterality | null;
  uploaded_by?: number | null;
  sha256?: string | null;
  uploaded_at: string;
  inference_status: 'PENDIENTE' | 'LISTO';
  inference?: InferenceResult | null;
  validation?: AIValidation | null;
}

export type AIVerdict = 'CONCORDANTE' | 'FALSO_POSITIVO' | 'FALSO_NEGATIVO' | 'NO_EVALUABLE';

export const AI_VERDICT_LABELS: Record<AIVerdict, string> = {
  CONCORDANTE: 'Concordante',
  FALSO_POSITIVO: 'Falso positivo',
  FALSO_NEGATIVO: 'Falso negativo',
  NO_EVALUABLE: 'No evaluable',
};

export interface AIValidation {
  id: number;
  image_id: number;
  inference_result_id: number;
  medico_id: number;
  verdict: AIVerdict;
  comment: string | null;
  ai_detected: boolean;
  ai_model_version: string;
  ai_was_simulated: boolean;
  created_at: string | null;
  updated_at: string | null;
}

export type TriageAssessment = 'APROPIADO' | 'SOBREESTIMADO' | 'SUBESTIMADO';

export const TRIAGE_ASSESSMENT_LABELS: Record<TriageAssessment, string> = {
  APROPIADO: 'Apropiado',
  SOBREESTIMADO: 'Sobreestimado (más prioridad de la necesaria)',
  SUBESTIMADO: 'Subestimado (menos prioridad de la necesaria)',
};

export type Recommendation =
  | 'CONTROL_RUTINA'
  | 'CONTROL_6_MESES'
  | 'ESTUDIO_COMPLEMENTARIO'
  | 'BIOPSIA'
  | 'DERIVACION';

export const RECOMMENDATION_LABELS: Record<Recommendation, string> = {
  CONTROL_RUTINA: 'Control de rutina',
  CONTROL_6_MESES: 'Control en 6 meses',
  ESTUDIO_COMPLEMENTARIO: 'Estudio complementario',
  BIOPSIA: 'Biopsia',
  DERIVACION: 'Derivación a especialista',
};

export interface ReviewInput {
  birads_final: number;
  findings: string;
  recommendation: Recommendation;
  triage_assessment: TriageAssessment;
  triage_comment?: string | null;
}

export interface ClinicalReview extends ReviewInput {
  id: number;
  case_id: number;
  medico_id: number;
  triage_level_at_review: TriageLevel | null;
  triage_config_version_at_review: number | null;
  created_at: string | null;
}

/** Bloque de firma que el backend agrega a los metadatos una vez que el médico firma el reporte. */
export interface MedicalSignatureBlock {
  SignedBy: string;
  SignedAt: string;
  VerificationCode: string;
  ContentSHA256: string;
}

export type DicomMetadata = Record<string, string | number | boolean | string[] | null | MedicalSignatureBlock>;

export interface ReportRecord {
  id: number;
  case_id: number;
  generated_by: number;
  generated_at: string | null;
  dicom_metadata: DicomMetadata;
  content_hash: string;
  signature_id: number | null;
}

export interface ReportSignature {
  id: number;
  case_id: number;
  medico_id: number;
  medico_name: string;
  signed_at: string;
  content_hash: string;
  verification_code: string;
  /** HMAC válido y contenido del reporte sin cambios desde la firma */
  valid: boolean;
}

export interface ModelVersionPerformance {
  model_version: string;
  is_simulated: boolean;
  validations: number;
  evaluable: number;
  not_evaluable: number;
  true_positives: number;
  true_negatives: number;
  false_positives: number;
  false_negatives: number;
  accuracy: number | null;
  accuracy_ci95: [number, number] | null;
  sensitivity: number | null;
  sensitivity_ci95: [number, number] | null;
  specificity: number | null;
  specificity_ci95: [number, number] | null;
  ppv: number | null;
  npv: number | null;
  meets_k5: boolean | null;
}

export interface ModelPerformanceReport {
  date_from: string | null;
  date_to: string | null;
  k5_target: number;
  min_sample: number;
  reference_standard: string;
  versions: ModelVersionPerformance[];
}

export interface DashboardMetrics {
  date_from: string | null;
  date_to: string | null;
  total_cases: number;
  cases_by_status: Record<CaseStatus, number>;
  cases_by_level: Record<TriageLevel, number>;
  avg_creation_to_triage_seconds: number | null;
  kpi_creation_to_triage_target_seconds: number;
  avg_triage_to_review_hours_by_level: Record<TriageLevel, number | null>;
  alta_pending_over_hours: number;
  alta_pending_threshold_hours: number;
  api_p95_ms: number | null;
  api_requests: number;
  server_errors: number;
  server_error_rate: number | null;
  kpi_api_p95_target_ms: number;
  override_ratio: number | null;
  triage_total: number;
  triage_overrides: number;
  cases_per_week: Array<{ week_start: string; cases: number; by_level?: Record<TriageLevel, number> }>;
  ai_validations_total: number;
  ai_validations_by_verdict: Record<AIVerdict, number>;
  ai_agreement_rate: number | null;
  ai_validations_simulated: number;
  triage_assessments_total: number;
  triage_assessments_by_value: Record<TriageAssessment, number>;
  triage_agreement_rate: number | null;
}

export interface AdminStats {
  total_users: number;
  active_users: number;
  total_cases: number;
  total_patients: number;
}

export interface ErrorLogEntry {
  id: number;
  occurred_at: string;
  method: string;
  path: string;
  status_code: number;
  error_type: string;
  message: string | null;
  location: string | null;
  user_id: number | null;
  request_id: string;
}

export interface ErrorTypeCount {
  error_type: string;
  count: number;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  role: string;
  full_name?: string | null;
  must_change_password: boolean;
}

// --- Privacidad (Ley 21.719) -------------------------------------------------

export interface ConsentText {
  version: string;
  body: string;
  is_active: boolean;
  created_at?: string | null;
}

export interface ConsentEvent {
  id: number;
  action: 'OTORGADO' | 'RETIRADO';
  consent_text_version: string | null;
  occurred_at: string;
  registered_by: number | null;
  note: string | null;
}

export type DataRequestType = 'ACCESO' | 'RECTIFICACION' | 'SUPRESION' | 'OPOSICION' | 'PORTABILIDAD' | 'BLOQUEO';
export type DataRequestStatus = 'RECIBIDA' | 'EN_PROCESO' | 'RESUELTA' | 'RECHAZADA';

export const DATA_REQUEST_TYPE_LABELS: Record<DataRequestType, string> = {
  ACCESO: 'Acceso',
  RECTIFICACION: 'Rectificación',
  SUPRESION: 'Supresión',
  OPOSICION: 'Oposición',
  PORTABILIDAD: 'Portabilidad',
  BLOQUEO: 'Bloqueo',
};

export const DATA_REQUEST_STATUS_LABELS: Record<DataRequestStatus, string> = {
  RECIBIDA: 'Recibida',
  EN_PROCESO: 'En proceso',
  RESUELTA: 'Resuelta',
  RECHAZADA: 'Rechazada',
};

export interface DataSubjectRequest {
  id: number;
  patient_id: number;
  patient_name: string | null;
  patient_rut: string | null;
  request_type: DataRequestType;
  status: DataRequestStatus;
  detail: string | null;
  received_at: string;
  due_at: string;
  overdue: boolean;
  registered_by: number;
  resolved_at: string | null;
  resolved_by: number | null;
  resolution: string | null;
}

export interface DataRequestSummary {
  by_status: Record<DataRequestStatus, number>;
  open_total: number;
  overdue: number;
}

export type TimelineKind =
  | 'PATIENT_REGISTERED'
  | 'CONSENT_GRANTED'
  | 'CONSENT_WITHDRAWN'
  | 'PATIENT_BLOCKED'
  | 'CASE_CREATED'
  | 'IMAGES_UPLOADED'
  | 'TRIAGE_OVERRIDE'
  | 'REVIEW_REGISTERED'
  | 'CASE_CLOSED';

/** Hito de la historia del paciente. `detail` depende del tipo (y del rol: el ADMINISTRATIVO no recibe los clínicos). */
export interface TimelineEvent {
  kind: TimelineKind;
  at: string;
  case_id: number | null;
  case_code: string | null;
  actor_name: string | null;
  detail: {
    version?: string | null;
    note?: string;
    reason?: string | null;
    triage_level?: TriageLevel | null;
    symptoms?: string[];
    count?: number;
    computed_level?: TriageLevel;
    final_level?: TriageLevel;
    birads_final?: number;
    recommendation?: Recommendation;
  };
}
