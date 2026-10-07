import { useState } from 'react';
import { X, Search, UserPlus, User, Loader2, ShieldCheck } from 'lucide-react';
import { apiClient } from '../services/api';
import type { Patient, PatientInput, Sex } from '../types';
import { isValidRut, normalizeRut } from '../utils/rut';
import { errorBox, inputClass, labelClass, primaryButton, secondaryButton, formatDate } from './ui';

interface PatientModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectPatient: (patient: Patient) => void;
}

const EMPTY_FORM: PatientInput = {
  rut: '',
  first_name: '',
  last_name: '',
  birth_date: '',
  sex: 'F',
  medical_history: '',
  family_history_first_degree: false,
  previous_breast_cancer: false,
  consent_given: false,
};

export default function PatientModal({ isOpen, onClose, onSelectPatient }: PatientModalProps) {
  const [mode, setMode] = useState<'select' | 'create'>('select');
  const [searchTerm, setSearchTerm] = useState('');
  const [searched, setSearched] = useState(false);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<PatientInput>(EMPTY_FORM);

  const rutError = form.rut.trim() !== '' && !isValidRut(form.rut) ? 'RUT inválido: revise el dígito verificador' : null;
  const canSubmit =
    !loading &&
    form.rut.trim() !== '' &&
    !rutError &&
    form.first_name.trim() !== '' &&
    form.last_name.trim() !== '' &&
    form.birth_date !== '' &&
    form.consent_given;

  const searchPatients = async () => {
    setLoading(true);
    setError(null);
    const response = await apiClient.searchPatients(searchTerm.trim() || undefined);
    if (response.data) setPatients(response.data);
    else setError(response.error || 'Error al buscar pacientes');
    setSearched(true);
    setLoading(false);
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;
    setLoading(true);
    setError(null);
    const response = await apiClient.createPatient({
      ...form,
      rut: normalizeRut(form.rut),
      first_name: form.first_name.trim(),
      last_name: form.last_name.trim(),
      medical_history: form.medical_history?.trim() || null,
    });
    setLoading(false);
    if (response.data) {
      onSelectPatient(response.data);
      setForm(EMPTY_FORM);
      onClose();
    } else {
      setError(response.error || 'Error al registrar paciente');
    }
  };

  if (!isOpen) return null;

  const tabClass = (active: boolean) =>
    `flex items-center space-x-1.5 px-3 py-1.5 rounded text-xs font-medium transition-colors ${
      active
        ? 'bg-primary/20 text-primary border border-primary/30'
        : 'bg-secondary text-muted-foreground hover:text-foreground hover:bg-secondary/80'
    }`;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-card border border-border rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-card border-b border-border px-4 py-3 flex items-center justify-between">
          <h2 className="text-sm font-bold text-foreground">
            {mode === 'select' ? 'Buscar paciente' : 'Registrar paciente'}
          </h2>
          <button onClick={onClose} className="text-muted-foreground hover:text-foreground" aria-label="Cerrar">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4">
          <div className="flex space-x-2 mb-4">
            <button onClick={() => setMode('select')} className={tabClass(mode === 'select')}>
              <Search className="w-3.5 h-3.5" />
              <span>Buscar existente</span>
            </button>
            <button onClick={() => setMode('create')} className={tabClass(mode === 'create')}>
              <UserPlus className="w-3.5 h-3.5" />
              <span>Registrar nuevo</span>
            </button>
          </div>

          {error && <div className={`${errorBox} mb-3`}>{error}</div>}

          {mode === 'select' ? (
            <div>
              <div className="flex space-x-2 mb-3">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && searchPatients()}
                  placeholder="Buscar por RUT o nombre..."
                  className={inputClass}
                />
                <button onClick={searchPatients} disabled={loading} className={primaryButton}>
                  {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Buscar'}
                </button>
              </div>

              <div className="space-y-2">
                {patients.map((patient) => (
                  <button
                    key={patient.id}
                    onClick={() => {
                      onSelectPatient(patient);
                      onClose();
                    }}
                    className="w-full text-left p-3 border border-border rounded hover:bg-primary/10 hover:border-primary/30 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-semibold text-xs text-foreground">
                          {patient.first_name} {patient.last_name}
                        </p>
                        <p className="text-[10px] text-muted-foreground">
                          RUT {patient.rut} · Nac. {formatDate(patient.birth_date)}
                        </p>
                      </div>
                      {patient.consent_given ? (
                        <span className="text-[10px] text-green-400 flex items-center gap-1">
                          <ShieldCheck className="w-3 h-3" /> Consentimiento
                        </span>
                      ) : (
                        <span className="text-[10px] text-orange-400">Sin consentimiento</span>
                      )}
                      <User className="w-4 h-4 text-primary" />
                    </div>
                  </button>
                ))}
              </div>

              {!loading && searched && patients.length === 0 && (
                <p className="text-center py-8 text-xs text-muted-foreground">No se encontraron pacientes</p>
              )}
            </div>
          ) : (
            <form onSubmit={handleCreate} className="space-y-3">
              <div>
                <label className={labelClass} htmlFor="p-rut">RUT *</label>
                <input
                  id="p-rut"
                  type="text"
                  value={form.rut}
                  onChange={(e) => setForm({ ...form, rut: e.target.value })}
                  onBlur={() => form.rut && setForm({ ...form, rut: normalizeRut(form.rut) })}
                  required
                  className={inputClass}
                  placeholder="12345678-5"
                />
                {rutError && <p className="mt-1 text-[10px] text-red-400">{rutError}</p>}
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className={labelClass} htmlFor="p-first">Nombres *</label>
                  <input
                    id="p-first"
                    value={form.first_name}
                    onChange={(e) => setForm({ ...form, first_name: e.target.value })}
                    required
                    className={inputClass}
                  />
                </div>
                <div>
                  <label className={labelClass} htmlFor="p-last">Apellidos *</label>
                  <input
                    id="p-last"
                    value={form.last_name}
                    onChange={(e) => setForm({ ...form, last_name: e.target.value })}
                    required
                    className={inputClass}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className={labelClass} htmlFor="p-birth">Fecha de nacimiento *</label>
                  <input
                    id="p-birth"
                    type="date"
                    value={form.birth_date}
                    max={new Date().toISOString().slice(0, 10)}
                    onChange={(e) => setForm({ ...form, birth_date: e.target.value })}
                    required
                    className={inputClass}
                  />
                </div>
                <div>
                  <label className={labelClass} htmlFor="p-sex">Sexo</label>
                  <select
                    id="p-sex"
                    value={form.sex ?? ''}
                    onChange={(e) => setForm({ ...form, sex: (e.target.value || null) as Sex | null })}
                    className={inputClass}
                  >
                    <option value="F">Femenino</option>
                    <option value="M">Masculino</option>
                    <option value="O">Otro</option>
                  </select>
                </div>
              </div>

              <fieldset className="grid sm:grid-cols-2 gap-2 p-3 border border-border rounded">
                <legend className="px-1 text-[10px] font-semibold text-muted-foreground uppercase">
                  Antecedentes
                </legend>
                <label className="flex items-center gap-2 text-xs text-foreground">
                  <input
                    type="checkbox"
                    checked={form.family_history_first_degree}
                    onChange={(e) => setForm({ ...form, family_history_first_degree: e.target.checked })}
                  />
                  Antecedente familiar de primer grado
                </label>
                <label className="flex items-center gap-2 text-xs text-foreground">
                  <input
                    type="checkbox"
                    checked={form.previous_breast_cancer}
                    onChange={(e) => setForm({ ...form, previous_breast_cancer: e.target.checked })}
                  />
                  Cáncer de mama previo
                </label>
              </fieldset>

              <div>
                <label className={labelClass} htmlFor="p-history">Historial médico / notas</label>
                <textarea
                  id="p-history"
                  value={form.medical_history ?? ''}
                  onChange={(e) => setForm({ ...form, medical_history: e.target.value })}
                  rows={3}
                  className={inputClass}
                />
              </div>

              <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded">
                <label className="flex items-start gap-2 text-xs text-foreground">
                  <input
                    type="checkbox"
                    className="mt-0.5"
                    checked={form.consent_given}
                    onChange={(e) => setForm({ ...form, consent_given: e.target.checked })}
                  />
                  <span>
                    <strong>Consentimiento informado (obligatorio).</strong> Declaro que el paciente fue informado
                    de que sus datos e imágenes se usarán en una plataforma de apoyo a la priorización de casos,
                    que no reemplaza el criterio médico, y que autorizó su tratamiento conforme a la Ley 19.628.
                    Se registrará la fecha y el usuario que confirma.
                  </span>
                </label>
              </div>

              <div className="flex gap-2 pt-2">
                <button type="button" onClick={onClose} className={`${secondaryButton} flex-1`}>
                  Cancelar
                </button>
                <button type="submit" disabled={!canSubmit} className={`${primaryButton} flex-1`}>
                  {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Registrar paciente'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
