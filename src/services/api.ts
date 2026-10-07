import type {
  AdminStats,
  AuditEntry,
  CaseImage,
  ExamType,
  InferenceResult,
  Laterality,
  CaseStatus,
  CaseSymptoms,
  ClinicalCase,
  TriageLevel,
  Me,
  Page,
  Patient,
  PatientInput,
  UserAccount,
  UserCreateInput,
  UserUpdateInput,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private getToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  setToken(token: string | null) {
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }

  /** Ante un 401 con sesión activa: cerrar sesión y volver al login. */
  private handleUnauthorized() {
    if (this.getToken()) {
      this.setToken(null);
      window.location.reload();
    }
  }

  private authHeaders(): Record<string, string> {
    const token = this.getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  private static errorMessage(data: unknown, status: number): string {
    if (data && typeof data === 'object' && 'detail' in data) {
      const detail = (data as { detail: unknown }).detail;
      if (typeof detail === 'string') return detail;
      if (Array.isArray(detail) && detail.length > 0) {
        const first = detail[0] as { msg?: string };
        return first.msg ? `Datos inválidos: ${first.msg}` : 'Datos inválidos';
      }
    }
    return `Error ${status}`;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> | undefined),
      ...this.authHeaders(),
    };

    try {
      const response = await fetch(url, { ...options, headers });

      const contentType = response.headers.get('content-type');
      let data: unknown = null;
      if (contentType && contentType.includes('application/json')) {
        try {
          data = await response.json();
        } catch {
          return { error: 'Respuesta inválida del servidor', status: response.status };
        }
      } else if (response.status !== 204) {
        return {
          error: `Error del servidor (${response.status})`,
          status: response.status,
        };
      }

      if (!response.ok) {
        if (response.status === 401) this.handleUnauthorized();
        return { error: ApiClient.errorMessage(data, response.status), status: response.status };
      }

      return { data: data as T, status: response.status };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Error de red',
        status: 0,
      };
    }
  }

  async login(rut: string, password: string) {
    return this.request<{
      access_token: string;
      token_type: string;
      role: string;
      full_name?: string | null;
    }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ rut, password }),
    });
  }

  async getMe() {
    return this.request<Me>('/auth/me');
  }

  // --- Pacientes -----------------------------------------------------------
  async createPatient(data: PatientInput) {
    return this.request<Patient>('/patients', { method: 'POST', body: JSON.stringify(data) });
  }

  async updatePatient(id: number, data: Partial<PatientInput>) {
    return this.request<Patient>(`/patients/${id}`, { method: 'PUT', body: JSON.stringify(data) });
  }

  async getPatient(id: number) {
    return this.request<Patient>(`/patients/${id}`);
  }

  async searchPatients(search?: string) {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    return this.request<Patient[]>(`/patients?${params.toString()}`);
  }

  // --- Casos ---------------------------------------------------------------
  async createCase(data: CaseSymptoms & { patient_id: number }) {
    return this.request<ClinicalCase>('/cases', { method: 'POST', body: JSON.stringify(data) });
  }

  async getCases(filters: { status?: CaseStatus; level?: TriageLevel; patient_id?: number; page?: number; size?: number } = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => {
      if (v !== undefined) params.append(k, String(v));
    });
    return this.request<Page<ClinicalCase>>(`/cases?${params.toString()}`);
  }

  async getCase(caseId: number) {
    return this.request<ClinicalCase>(`/cases/${caseId}`);
  }

  async updateCase(caseId: number, data: Partial<CaseSymptoms>) {
    return this.request<ClinicalCase>(`/cases/${caseId}`, { method: 'PATCH', body: JSON.stringify(data) });
  }

  // --- Imágenes ------------------------------------------------------------
  /** Sube una imagen con progreso real (XMLHttpRequest expone upload.onprogress; fetch no). */
  uploadImage(
    caseId: number,
    file: Blob,
    filename: string,
    meta: { exam_type: ExamType; laterality?: Laterality | null },
    onProgress?: (percent: number) => void
  ): Promise<ApiResponse<CaseImage>> {
    const form = new FormData();
    form.append('file', file, filename);
    form.append('exam_type', meta.exam_type);
    if (meta.laterality) form.append('laterality', meta.laterality);

    return new Promise((resolve) => {
      const xhr = new XMLHttpRequest();
      xhr.open('POST', `${this.baseURL}/cases/${caseId}/images`);
      const headers = this.authHeaders();
      Object.entries(headers).forEach(([k, v]) => xhr.setRequestHeader(k, v));
      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable && onProgress) onProgress(Math.round((e.loaded / e.total) * 100));
      };
      xhr.onload = () => {
        let data: unknown = null;
        try {
          data = JSON.parse(xhr.responseText);
        } catch {
          data = null;
        }
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve({ data: data as CaseImage, status: xhr.status });
        } else {
          if (xhr.status === 401) this.handleUnauthorized();
          resolve({ error: ApiClient.errorMessage(data, xhr.status), status: xhr.status });
        }
      };
      xhr.onerror = () => resolve({ error: 'Error de red al subir la imagen', status: 0 });
      xhr.send(form);
    });
  }

  async listImages(caseId: number) {
    return this.request<CaseImage[]>(`/cases/${caseId}/images`);
  }

  async getInference(caseId: number, imageId: number) {
    return this.request<InferenceResult>(`/cases/${caseId}/images/${imageId}/inference`);
  }

  /** Descarga la imagen con el header Authorization y devuelve un object URL (no se expone el token en la URL). */
  async fetchImageBlob(caseId: number, imageId: number): Promise<Blob | null> {
    try {
      const response = await fetch(`${this.baseURL}/cases/${caseId}/images/${imageId}/file`, {
        headers: this.authHeaders(),
      });
      if (response.status === 401) this.handleUnauthorized();
      if (!response.ok) return null;
      return await response.blob();
    } catch {
      return null;
    }
  }

  async getStatistics() {
    return this.request<{
      total_cases: number;
      positive_cases: number;
      negative_cases: number;
      average_confidence: number;
      average_processing_time_ms: number;
      total_detections: number;
    }>('/reports/statistics');
  }

  async getMonthlyData(year?: number) {
    const params = new URLSearchParams();
    if (year) params.append('year', year.toString());
    return this.request<Array<{
      month: string;
      cases: number;
      positive: number;
      negative: number;
    }>>(`/reports/monthly?${params.toString()}`);
  }

  // --- Administración (solo ADMIN) ---------------------------------------
  async getAdminStats() {
    return this.request<AdminStats>('/admin/stats');
  }

  async listUsers() {
    return this.request<UserAccount[]>('/admin/users');
  }

  async createUser(data: UserCreateInput) {
    return this.request<UserAccount>('/admin/users', { method: 'POST', body: JSON.stringify(data) });
  }

  async updateUser(id: number, data: UserUpdateInput) {
    return this.request<UserAccount>(`/admin/users/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async listAudit(filters: { action?: string; entity?: string; user_id?: number; from?: string; to?: string; page?: number; size?: number }) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => {
      if (v !== undefined && v !== '') params.append(k, String(v));
    });
    return this.request<Page<AuditEntry>>(`/admin/audit?${params.toString()}`);
  }

  // Para el panel de usuario
  async getUserInfo() {
    return this.request<{
      id: number;
      rut: string;
      email: string;
      role: string;
    }>('/user/info');
  }

  async getUserPatients() {
    return this.request<Array<{
      id: number;
      rut: string;
      first_name?: string;
      last_name?: string;
    }>>('/user/patients');
  }

  async getSupportTickets() {
    return this.request<Array<{
      id: number;
      title: string;
      description: string;
      status: string;
      created_at: string;
    }>>('/user/tickets');
  }
}

export const apiClient = new ApiClient(API_BASE_URL);