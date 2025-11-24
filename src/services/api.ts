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

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      // Verificar si la respuesta es JSON antes de intentar parsearla
      const contentType = response.headers.get('content-type');
      let data: any = {};

      if (contentType && contentType.includes('application/json')) {
        try {
          data = await response.json();
        } catch (e) {
          console.error('Error parsing JSON response:', e);
          return {
            error: 'Invalid JSON response from server',
            status: response.status,
          };
        }
      } else {
        // Si no es JSON, probablemente es HTML (página de error)
        const text = await response.text();
        console.error('Server returned non-JSON response:', text.substring(0, 200));
        return {
          error: `Server error (${response.status}): Expected JSON but received ${contentType || 'unknown'}`,
          status: response.status,
        };
      }

      if (!response.ok) {
        if (response.status === 401) {
          this.setToken(null);
          window.location.reload();
        }
        return {
          error: data.detail || data.message || `Error ${response.status}`,
          status: response.status,
        };
      }

      return { data, status: response.status };
    } catch (error) {
      console.error('Network error:', error);
      return {
        error: error instanceof Error ? error.message : 'Network error',
        status: 0,
      };
    }
  }

  async login(rut: string, password: string) {
    return this.request<{ token: string; role: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ rut, password }),
    });
  }

  async getMe() {
    return this.request<{ role: string; message: string; rut?: string; email?: string }>('/auth/me');
  }
  
  async signup(rut: string, email: string, password: string, role: string = "MEDICO") {
    return this.request('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ rut, email, password, role }),
    });
  }
  async createPatient(data: {
    rut: string;
    first_name?: string;
    last_name?: string;
    birth_date?: string;
    sex?: string;
    medical_history?: string;
  }) {
    return this.request<{
      id: number;
      rut: string;
      first_name?: string;
      last_name?: string;
      birth_date?: string;
      sex?: string;
      medical_history?: string;
      created_at: string;
    }>('/patients', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async searchPatients(search?: string) {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    return this.request<Array<{
      id: number;
      rut: string;
      first_name?: string;
      last_name?: string;
      birth_date?: string;
      sex?: string;
      medical_history?: string;
      created_at: string;
    }>>(`/patients?${params.toString()}`);
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

    return this.request(`/cases?${params.toString()}`);
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

    const url = `${this.baseURL}/cases/${caseId}/images`;
    const headers: HeadersInit = {};
    
    const token = this.getToken(); // Leer del localStorage en cada petición
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: formData,
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        // Si es error 401, limpiar token
        if (response.status === 401) {
          this.setToken(null);
          window.location.reload();
        }
        return {
          error: data.detail || `Error ${response.status}`,
          status: response.status,
        };
      }

      return { data, status: response.status };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Network error',
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

  // Para el panel de administración
  async getAdminStats() {
    return this.request<{
      total_users: number;
      total_cases: number;
      total_patients: number;
      active_sessions: number;
    }>('/admin/stats');
  }

  async getRecentUsers() {
    return this.request<Array<{
      id: number;
      rut: string;
      email: string;
      role: string;
      created_at: string;
    }>>('/admin/users/recent');
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