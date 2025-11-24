import { useState, useEffect } from 'react';
import { X, Search, UserPlus, User, Loader2 } from 'lucide-react';
import { apiClient } from '../services/api';

interface Patient {
  id: number;
  rut: string;
  first_name?: string;
  last_name?: string;
  birth_date?: string;
  sex?: string;
  medical_history?: string;
}

interface PatientModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectPatient: (patientId: number) => void;
  onCreatePatient: (patient: Patient) => void;
}

export default function PatientModal({ isOpen, onClose, onSelectPatient, onCreatePatient }: PatientModalProps) {
  const [mode, setMode] = useState<'select' | 'create'>('select');
  const [searchTerm, setSearchTerm] = useState('');
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Formulario para crear paciente
  const [formData, setFormData] = useState({
    rut: '',
    first_name: '',
    last_name: '',
    birth_date: '',
    sex: '',
    medical_history: '',
  });

  useEffect(() => {
    if (isOpen && mode === 'select') {
      searchPatients();
    }
  }, [isOpen, mode]);

  const searchPatients = async () => {
    if (!searchTerm.trim()) {
      setPatients([]);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.searchPatients(searchTerm);
      if (response.data) {
        setPatients(response.data);
      } else {
        setError(response.error || 'Error al buscar pacientes');
      }
    } catch (err) {
      setError('Error al buscar pacientes');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePatient = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.createPatient({
        rut: formData.rut,
        first_name: formData.first_name || undefined,
        last_name: formData.last_name || undefined,
        birth_date: formData.birth_date || undefined,
        sex: formData.sex || undefined,
        medical_history: formData.medical_history || undefined,
      });

      if (response.data) {
        onCreatePatient(response.data);
        onSelectPatient(response.data.id);
        onClose();
      } else {
        setError(response.error || 'Error al crear paciente');
      }
    } catch (err) {
      setError('Error al crear paciente');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-card border border-border rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-card border-b border-border px-4 py-3 flex items-center justify-between">
          <h2 className="text-sm font-bold text-foreground">
            {mode === 'select' ? 'Buscar Paciente' : 'Crear Nuevo Paciente'}
          </h2>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4">
          {/* Tabs */}
          <div className="flex space-x-2 mb-4">
            <button
              onClick={() => setMode('select')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                mode === 'select'
                  ? 'bg-primary/20 text-primary border border-primary/30'
                  : 'bg-secondary text-muted-foreground hover:text-foreground hover:bg-secondary/80'
              }`}
            >
              <Search className="w-3.5 h-3.5" />
              <span>Buscar Existente</span>
            </button>
            <button
              onClick={() => setMode('create')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                mode === 'create'
                  ? 'bg-primary/20 text-primary border border-primary/30'
                  : 'bg-secondary text-muted-foreground hover:text-foreground hover:bg-secondary/80'
              }`}
            >
              <UserPlus className="w-3.5 h-3.5" />
              <span>Crear Nuevo</span>
            </button>
          </div>

          {mode === 'select' ? (
            <div>
              <div className="flex space-x-2 mb-3">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && searchPatients()}
                  placeholder="Buscar por RUT o nombre..."
                  className="flex-1 px-3 py-2 bg-background border border-input rounded text-xs text-foreground focus:ring-2 focus:ring-primary focus:border-transparent"
                />
                <button
                  onClick={searchPatients}
                  disabled={loading}
                  className="px-4 py-2 bg-primary hover:bg-primary/90 disabled:bg-muted disabled:text-muted-foreground text-primary-foreground rounded text-xs font-semibold transition-colors"
                >
                  {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Buscar'}
                </button>
              </div>

              {error && (
                <div className="mb-3 p-2 bg-destructive/10 border border-destructive/20 text-destructive-foreground rounded text-xs">
                  {error}
                </div>
              )}

              {loading && (
                <div className="text-center py-8 text-muted-foreground">
                  <Loader2 className="w-6 h-6 mx-auto mb-2 animate-spin text-primary" />
                  <p className="text-xs">Buscando...</p>
                </div>
              )}

              {!loading && patients.length > 0 && (
                <div className="space-y-2">
                  {patients.map((patient) => (
                    <div
                      key={patient.id}
                      onClick={() => {
                        onSelectPatient(patient.id);
                        onClose();
                      }}
                      className="p-3 border border-border rounded hover:bg-primary/10 hover:border-primary/30 cursor-pointer transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-semibold text-xs text-foreground">
                            {patient.first_name || ''} {patient.last_name || ''}
                          </p>
                          <p className="text-[10px] text-muted-foreground">RUT: {patient.rut}</p>
                          {patient.birth_date && (
                            <p className="text-[10px] text-muted-foreground">
                              Fecha de nacimiento: {new Date(patient.birth_date).toLocaleDateString()}
                            </p>
                          )}
                        </div>
                        <User className="w-4 h-4 text-primary" />
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {!loading && searchTerm && patients.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <p className="text-xs">No se encontraron pacientes</p>
                </div>
              )}
            </div>
          ) : (
            <form onSubmit={handleCreatePatient} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-foreground mb-1">
                  RUT *
                </label>
                <input
                  type="text"
                  value={formData.rut}
                  onChange={(e) => setFormData({ ...formData, rut: e.target.value })}
                  required
                  className="w-full px-3 py-2 bg-background border border-input rounded text-xs text-foreground focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder="12345678-9"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-foreground mb-1">
                    Nombre
                  </label>
                  <input
                    type="text"
                    value={formData.first_name}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                    className="w-full px-3 py-2 bg-background border border-input rounded text-xs text-foreground focus:ring-2 focus:ring-primary focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-foreground mb-1">
                    Apellido
                  </label>
                  <input
                    type="text"
                    value={formData.last_name}
                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                    className="w-full px-3 py-2 bg-background border border-input rounded text-xs text-foreground focus:ring-2 focus:ring-primary focus:border-transparent"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-foreground mb-1">
                    Fecha de Nacimiento
                  </label>
                  <input
                    type="date"
                    value={formData.birth_date}
                    onChange={(e) => setFormData({ ...formData, birth_date: e.target.value })}
                    className="w-full px-3 py-2 bg-background border border-input rounded text-xs text-foreground focus:ring-2 focus:ring-primary focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-foreground mb-1">
                    Sexo
                  </label>
                  <select
                    value={formData.sex}
                    onChange={(e) => setFormData({ ...formData, sex: e.target.value })}
                    className="w-full px-3 py-2 bg-background border border-input rounded text-xs text-foreground focus:ring-2 focus:ring-primary focus:border-transparent"
                  >
                    <option value="">Seleccionar...</option>
                    <option value="M">Masculino</option>
                    <option value="F">Femenino</option>
                    <option value="O">Otro</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-foreground mb-1">
                  Historial Médico / Notas
                </label>
                <textarea
                  value={formData.medical_history}
                  onChange={(e) => setFormData({ ...formData, medical_history: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 bg-background border border-input rounded text-xs text-foreground focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder="Notas adicionales sobre el paciente..."
                />
              </div>

              {error && (
                <div className="p-2 bg-destructive/10 border border-destructive/20 text-destructive-foreground rounded text-xs">
                  {error}
                </div>
              )}

              <div className="flex space-x-2 pt-2">
                <button
                  type="button"
                  onClick={onClose}
                  className="flex-1 px-3 py-2 border border-border text-foreground rounded text-xs font-medium hover:bg-secondary transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={loading || !formData.rut.trim()}
                  className="flex-1 px-3 py-2 bg-primary hover:bg-primary/90 disabled:bg-muted disabled:text-muted-foreground text-primary-foreground rounded text-xs font-semibold transition-colors"
                >
                  {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin mx-auto" /> : 'Crear Paciente'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
