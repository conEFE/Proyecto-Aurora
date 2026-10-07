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

export interface AdminStats {
  total_users: number;
  active_users: number;
  total_cases: number;
  total_patients: number;
}
