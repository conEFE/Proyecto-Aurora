import type {
  AdminStats,
  AuditEntry,
  Me,
  Page,
  Patient,
  PatientInput,
  UserAccount,
  UserCreateInput,
  UserUpdateInput,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ApiResponse<T> {
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

  async createCase(patientCode: string, patientId?: number, description?: string) {
    return this.request<{ id: number; code: string; created_at: string; medico_id: number; patient_id?: number }>('/cases', {
      method: 'POST',
      body: JSON.stringify({
        patient_code_anon: patientCode,
        patient_id: patientId,
        descripcion: description,
      }),
    });
  }

  async getCases(page = 1, size = 10, fromDate?: string, toDate?: string) {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    });
    if (fromDate) params.append('from_date', fromDate);
    if (toDate) params.append('to_date', toDate);

    return this.request<Array<{ id: number; code: string; created_at: string; medico_id: number; descripcion?: string }>>(
      `/cases?${params.toString()}`
    );
  }

  async getCase(caseId: number) {
    return this.request<{
      id: number;
      code: string;
      created_at: string;
      medico_id: number;
      descripcion?: string;
    }>(`/cases/${caseId}`);
  }

  async uploadImage(caseId: number, file: File, tipoImagen?: string) {
    const formData = new FormData();
    formData.append('file', file);
    if (tipoImagen) {
      formData.append('tipo_imagen', tipoImagen);
    }

    try {
      const response = await fetch(`${this.baseURL}/cases/${caseId}/images`, {
        method: 'POST',
        headers: this.authHeaders(),
        body: formData,
      });
      const data: unknown = await response.json().catch(() => null);
      if (!response.ok) {
        if (response.status === 401) this.handleUnauthorized();
        return { error: ApiClient.errorMessage(data, response.status), status: response.status };
      }
      return { data: data as { id: number }, status: response.status };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Error de red',
        status: 0,
      };
    }
  }

  async getImageResults(imageId: number) {
    return this.request<{
      image_id: number;
      detected: boolean;
      confidence: number;
      detections: Array<{
        x: number;
        y: number;
        width: number;
        height: number;
        confidence: number;
        class_name: string;
      }>;
      processing_time_ms: number;
      model_version: string;
      message: string;
    }>(`/images/${imageId}/results`, {
      method: 'POST',
    });
  }

  async generateReport(caseId: number) {
    return this.request(`/cases/${caseId}/reports`, {
      method: 'POST',
    });
  }

  async getCaseImages(caseId: number) {
    return this.request<Array<{
      id: number;
      filename: string;
      filepath: string;
      mime_type: string;
      width?: number;
      height?: number;
      size_kb?: number;
      uploaded_at: string;
      case_id: number;
    }>>(`/cases/${caseId}/images`);
  }

  getImageUrl(caseId: number, imageId: number): string {
    const token = this.getToken();
    const url = `${this.baseURL}/cases/${caseId}/images/${imageId}/file`;
    // Si hay token, agregarlo como query param para autenticación
    return token ? `${url}?token=${token}` : url;
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