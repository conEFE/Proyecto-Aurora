import { useEffect, useState } from 'react';
import { Loader2, Search, ShieldCheck, UserPlus } from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '../services/api';
import type { ConsentText, Patient, PatientInput, Sex } from '../types';
import { isValidRut, normalizeRut } from '../utils/rut';
import { cn } from '../lib/cn';
import Dialog from './Dialog';
import { ErrorMessage, Loading } from './Feedback';
import { formatDate, inputClass, labelClass, primaryButton, secondaryButton, textareaClass } from './ui';

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
  const [consentText, setConsentText] = useState<ConsentText | null>(null);

  // El texto de consentimiento vigente se muestra completo y su versión se envía al registrar
  useEffect(() => {
    if (!isOpen || mode !== 'create' || consentText) return;
    apiClient.getConsentText().then((r) => {
      if (r.data) setConsentText(r.data);
      else setError(r.error || 'No se pudo cargar el texto de consentimiento.');
    });
  }, [isOpen, mode, consentText]);

  const rutError = form.rut.trim() !== '' && !isValidRut(form.rut) ? 'RUT inválido: revise el dígito verificador.' : null;
  const canSubmit =
    !loading &&
    form.rut.trim() !== '' &&
    !rutError &&
    form.first_name.trim() !== '' &&
    form.last_name.trim() !== '' &&
    form.birth_date !== '' &&
    form.consent_given &&
    consentText !== null;

  const searchPatients = async () => {
    setLoading(true);
    setError(null);
    const response = await apiClient.searchPatients(searchTerm.trim() || undefined);
    if (response.data) setPatients(response.data);
    else setError(response.error || 'No se pudo buscar. Intente de nuevo.');
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
      consent_text_version: consentText?.version,
    });
    setLoading(false);
    if (response.data) {
      toast.success(`Paciente ${response.data.first_name} ${response.data.last_name} registrada`);
      onSelectPatient(response.data);
      setForm(EMPTY_FORM);
      onClose();
    } else {
      setError(response.error || 'No se pudo registrar el paciente. Revise los datos.');
    }
  };

  const tabClass = (active: boolean) =>
    cn(
      'inline-flex items-center gap-2 h-8 px-3 rounded-md text-sm transition-colors',
      active ? 'bg-card text-foreground font-bold ring-1 ring-border' : 'text-muted-foreground hover:text-foreground',
    );

  return (
    <Dialog
      open={isOpen}
      onOpenChange={(open) => !open && onClose()}
      title={mode === 'select' ? 'Buscar paciente' : 'Registrar paciente'}
      description={mode === 'select' ? 'Busque por RUT o nombre y selecciónela.' : 'Los campos marcados con * son obligatorios.'}
      size="lg"
    >
      <div role="group" aria-label="Modo" className="inline-flex p-1 rounded-lg bg-muted mb-5">
        <button onClick={() => setMode('select')} aria-pressed={mode === 'select'} className={tabClass(mode === 'select')}>
          <Search aria-hidden className="w-4 h-4" /> Buscar existente
        </button>
        <button onClick={() => setMode('create')} aria-pressed={mode === 'create'} className={tabClass(mode === 'create')}>
          <UserPlus aria-hidden className="w-4 h-4" /> Registrar nueva
        </button>
      </div>

      <ErrorMessage className="mb-4">{error}</ErrorMessage>

      {mode === 'select' ? (
        <div>
          <form
            className="flex gap-2 mb-4"
            onSubmit={(e) => {
              e.preventDefault();
              searchPatients();
            }}
          >
            <label htmlFor="p-search" className="sr-only">Buscar por RUT o nombre</label>
            <input
              id="p-search"
              type="search"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="RUT o nombre"
              className={inputClass}
              autoFocus
            />
            <button type="submit" disabled={loading} className={primaryButton}>
              {loading ? <Loader2 aria-hidden className="w-4 h-4 animate-spin" /> : <Search aria-hidden className="w-4 h-4" />}
              Buscar
            </button>
          </form>

          {loading ? (
            <Loading label="Buscando…" className="py-6" />
          ) : (
            <ul className="divide-y divide-border border-y border-border">
              {patients.map((patient) => (
                <li key={patient.id}>
                  <button
                    onClick={() => {
                      onSelectPatient(patient);
                      onClose();
                    }}
                    className="w-full flex items-center justify-between gap-4 px-2 py-3 text-left hover:bg-accent transition-colors rounded-md"
                  >
                    <span>
                      <span className="block font-bold">{patient.first_name} {patient.last_name}</span>
                      <span className="block text-sm text-muted-foreground tabular-nums">
                        RUT {patient.rut} · nac. {formatDate(patient.birth_date)}
                      </span>
                    </span>
                    {patient.consent_given ? (
                      <span className="inline-flex items-center gap-1.5 text-sm text-baja">
                        <ShieldCheck aria-hidden className="w-4 h-4" /> Con consentimiento
                      </span>
                    ) : (
                      <span className="text-sm font-semibold text-media">Sin consentimiento</span>
                    )}
                  </button>
                </li>
              ))}
            </ul>
          )}

          {!loading && searched && patients.length === 0 && (
            <p role="status" className="text-center py-8 text-sm text-muted-foreground">
              No se encontraron pacientes. Puede registrarla en «Registrar nueva».
            </p>
          )}
        </div>
      ) : (
        <form onSubmit={handleCreate} className="space-y-4" noValidate>
          <div>
            <label className={labelClass} htmlFor="p-rut">RUT *</label>
            <input
              id="p-rut"
              type="text"
              value={form.rut}
              onChange={(e) => setForm({ ...form, rut: e.target.value })}
              onBlur={() => form.rut && setForm({ ...form, rut: normalizeRut(form.rut) })}
              required
              className={cn(inputClass, 'w-56')}
              placeholder="12345678-5"
              aria-invalid={rutError ? true : undefined}
              aria-describedby={rutError ? 'p-rut-error' : undefined}
            />
            {rutError && <p id="p-rut-error" className="mt-1 text-sm text-destructive">{rutError}</p>}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelClass} htmlFor="p-first">Nombres *</label>
              <input id="p-first" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} required className={inputClass} />
            </div>
            <div>
              <label className={labelClass} htmlFor="p-last">Apellidos *</label>
              <input id="p-last" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} required className={inputClass} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
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

          <fieldset className="px-4 pb-4 pt-2 rounded-lg border border-border">
            <legend className="px-1 text-sm font-bold">Antecedentes</legend>
            <div className="grid sm:grid-cols-2 gap-3">
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={form.family_history_first_degree}
                  onChange={(e) => setForm({ ...form, family_history_first_degree: e.target.checked })}
                />
                Antecedente familiar de primer grado
              </label>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={form.previous_breast_cancer}
                  onChange={(e) => setForm({ ...form, previous_breast_cancer: e.target.checked })}
                />
                Cáncer de mama previo
              </label>
            </div>
          </fieldset>

          <div>
            <label className={labelClass} htmlFor="p-history">Historial médico y notas</label>
            <textarea
              id="p-history"
              value={form.medical_history ?? ''}
              onChange={(e) => setForm({ ...form, medical_history: e.target.value })}
              rows={3}
              className={textareaClass}
            />
          </div>

          <fieldset className="px-4 pb-4 pt-2 rounded-lg bg-muted border border-border space-y-3">
            <legend className="px-1 text-sm font-bold">
              Consentimiento informado *
              {consentText && <span className="ml-1 font-normal text-muted-foreground">· versión {consentText.version}</span>}
            </legend>
            {consentText ? (
              <div
                className="max-h-48 overflow-y-auto whitespace-pre-line rounded-md border border-border bg-background p-3 text-sm leading-relaxed text-muted-foreground"
                tabIndex={0}
                aria-label="Texto de consentimiento informado"
              >
                {consentText.body}
              </div>
            ) : (
              <p role="status" className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 aria-hidden className="w-4 h-4 animate-spin" /> Cargando el texto de consentimiento…
              </p>
            )}
            <label className="flex items-start gap-3 text-sm">
              <input
                type="checkbox"
                className="mt-0.5 shrink-0"
                checked={form.consent_given}
                disabled={!consentText}
                onChange={(e) => setForm({ ...form, consent_given: e.target.checked })}
              />
              <span>
                Declaro que mostré o leí este texto a la paciente y que autorizó el tratamiento de sus datos. Se registrará
                la versión del texto, la fecha y el usuario que confirma.
              </span>
            </label>
          </fieldset>

          <div className="flex justify-end gap-2 pt-1">
            <button type="button" onClick={onClose} className={secondaryButton}>Cancelar</button>
            <button type="submit" disabled={!canSubmit} className={primaryButton}>
              {loading && <Loader2 aria-hidden className="w-4 h-4 animate-spin" />}
              Registrar paciente
            </button>
          </div>
        </form>
      )}
    </Dialog>
  );
}
