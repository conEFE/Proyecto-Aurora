import { useCallback, useEffect, useState } from 'react';
import { ChevronLeft, FolderPlus, Loader2, Save, Search, Trash2, UserPlus, Users } from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '../services/api';
import type { ClinicalCase, Patient, PatientInput, Sex } from '../types';
import { cn } from '../lib/cn';
import { LevelBadge, StatusBadge } from './Badges';
import { EmptyState, ErrorMessage, Loading } from './Feedback';
import PatientModal from './PatientModal';
import PatientTimeline from './PatientTimeline';
import {
  cardClass,
  dangerButton,
  formatDate,
  ghostButton,
  inputClass,
  labelClass,
  pageClass,
  pageTitle,
  primaryButton,
  secondaryButton,
  sectionTitle,
  tdClass,
  textareaClass,
  thClass,
} from './ui';

type EditableFields = Pick<
  PatientInput,
  | 'first_name'
  | 'last_name'
  | 'birth_date'
  | 'sex'
  | 'medical_history'
  | 'family_history_first_degree'
  | 'previous_breast_cancer'
>;

function editableOf(p: Patient): EditableFields {
  return {
    first_name: p.first_name,
    last_name: p.last_name,
    birth_date: p.birth_date,
    sex: p.sex ?? null,
    medical_history: p.medical_history ?? '',
    family_history_first_degree: p.family_history_first_degree,
    previous_breast_cancer: p.previous_breast_cancer,
  };
}

function ageFrom(birthDate: string): number {
  const b = new Date(birthDate);
  const now = new Date();
  let age = now.getFullYear() - b.getFullYear();
  const m = now.getMonth() - b.getMonth();
  if (m < 0 || (m === 0 && now.getDate() < b.getDate())) age--;
  return age;
}

function PatientState({ p }: { p: Patient }) {
  if (p.blocked_at) return <span className="text-sm font-semibold text-alta">Datos bloqueados</span>;
  if (!p.consent_given) return <span className="text-sm font-semibold text-media">Sin consentimiento</span>;
  return <span className="text-sm text-baja">Activo</span>;
}

interface PatientDetailProps {
  patient: Patient;
  onUpdated: (p: Patient) => void;
  onDeleted: (id: number) => void;
  onOpenCase: (caseId: number) => void;
  onNewCase: (p: Patient) => void;
}

function PatientDetail({ patient, onUpdated, onDeleted, onOpenCase, onNewCase }: PatientDetailProps) {
  const [form, setForm] = useState<EditableFields>(editableOf(patient));
  const [cases, setCases] = useState<ClinicalCase[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const blocked = !!patient.blocked_at;
  const dirty = JSON.stringify(form) !== JSON.stringify(editableOf(patient));

  useEffect(() => {
    apiClient.getCases({ patient_id: patient.id, size: 100 }).then((r) => {
      if (r.data) setCases(r.data.items);
      else setError(r.error || 'No se pudieron cargar los casos.');
    });
  }, [patient.id]);

  const save = async () => {
    setSaving(true);
    setError(null);
    const r = await apiClient.updatePatient(patient.id, {
      ...form,
      first_name: form.first_name.trim(),
      last_name: form.last_name.trim(),
      medical_history: form.medical_history?.trim() || null,
    });
    setSaving(false);
    if (r.data) {
      toast.success('Datos guardados. Si tiene casos abiertos, su triage se recalculó.');
      onUpdated(r.data);
    } else setError(r.error || 'No se pudieron guardar los cambios.');
  };

  const remove = async () => {
    setSaving(true);
    const r = await apiClient.deletePatient(patient.id);
    setSaving(false);
    if (r.error) {
      setError(r.error);
      setConfirmDelete(false);
    } else {
      toast.success('Paciente eliminado.');
      onDeleted(patient.id);
    }
  };

  const canEdit = !blocked && !saving;
  const hasCases = (cases?.length ?? 0) > 0;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4 pb-6 border-b border-border">
        <div>
          <div className="flex flex-wrap items-center gap-x-5 gap-y-2">
            <h2 id="pd-title" className="text-4xl font-extrabold tracking-tight">
              {patient.first_name} {patient.last_name}
            </h2>
            <PatientState p={patient} />
          </div>
          <p className="mt-2 text-muted-foreground tabular-nums">
            RUT {patient.rut} · {ageFrom(patient.birth_date)} años · registrada el {formatDate(patient.created_at)}
          </p>
        </div>
        <button className={primaryButton} disabled={blocked || !patient.consent_given} onClick={() => onNewCase(patient)}
          title={!patient.consent_given ? 'Registre el consentimiento en Privacidad para crear casos' : undefined}>
          <FolderPlus aria-hidden className="w-4 h-4" /> Nuevo caso
        </button>
      </div>

      <div className="grid xl:grid-cols-[minmax(0,7fr)_minmax(0,5fr)] gap-6 items-start">
      <div className="space-y-6 min-w-0">
      <section className={cn(cardClass, 'p-6 space-y-5')} aria-labelledby="pd-data">
        <h3 id="pd-data" className={sectionTitle}>Datos</h3>
        {blocked && (
          <p className="text-sm text-muted-foreground">
            Datos bloqueados desde el {formatDate(patient.blocked_at)}. No se pueden editar ni crear casos.
          </p>
        )}
        <ErrorMessage>{error}</ErrorMessage>

        <div className="grid sm:grid-cols-2 gap-4">
          <div>
            <label className={labelClass} htmlFor="pd-first">Nombres</label>
            <input id="pd-first" className={inputClass} value={form.first_name} disabled={!canEdit}
              onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
          </div>
          <div>
            <label className={labelClass} htmlFor="pd-last">Apellidos</label>
            <input id="pd-last" className={inputClass} value={form.last_name} disabled={!canEdit}
              onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
          </div>
          <div>
            <label className={labelClass} htmlFor="pd-birth">Fecha de nacimiento</label>
            <input id="pd-birth" type="date" className={inputClass} value={form.birth_date} disabled={!canEdit}
              max={new Date().toISOString().slice(0, 10)}
              onChange={(e) => setForm({ ...form, birth_date: e.target.value })} />
          </div>
          <div>
            <label className={labelClass} htmlFor="pd-sex">Sexo</label>
            <select id="pd-sex" className={inputClass} value={form.sex ?? ''} disabled={!canEdit}
              onChange={(e) => setForm({ ...form, sex: (e.target.value || null) as Sex | null })}>
              <option value="F">Femenino</option>
              <option value="M">Masculino</option>
              <option value="O">Otro</option>
            </select>
          </div>
        </div>
        <fieldset className="px-4 pb-4 pt-2 rounded-lg border border-border" disabled={!canEdit}>
          <legend className="px-1 text-sm font-bold">Antecedentes</legend>
          <div className="grid sm:grid-cols-2 gap-3">
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={form.family_history_first_degree}
                onChange={(e) => setForm({ ...form, family_history_first_degree: e.target.checked })} />
              Antecedente familiar de primer grado
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={form.previous_breast_cancer}
                onChange={(e) => setForm({ ...form, previous_breast_cancer: e.target.checked })} />
              Cáncer de mama previo
            </label>
          </div>
        </fieldset>
        <div>
          <label className={labelClass} htmlFor="pd-history">Historial médico y notas</label>
          <textarea id="pd-history" rows={3} className={textareaClass} value={form.medical_history ?? ''} disabled={!canEdit}
            onChange={(e) => setForm({ ...form, medical_history: e.target.value })} />
        </div>
        {!blocked && (
          <button className={primaryButton} disabled={!dirty || saving || !form.first_name.trim() || !form.last_name.trim() || !form.birth_date}
            onClick={save}>
            {saving ? <Loader2 aria-hidden className="w-4 h-4 animate-spin" /> : <Save aria-hidden className="w-4 h-4" />}
            Guardar cambios
          </button>
        )}
      </section>

      <section className={cn(cardClass, 'overflow-hidden')} aria-labelledby="pd-cases">
        <div className="px-6 pt-5 pb-3 flex flex-wrap items-center justify-between gap-3">
          <h3 id="pd-cases" className={sectionTitle}>Casos{cases ? ` (${cases.length})` : ''}</h3>
        </div>
        {cases === null ? (
          <Loading label="Cargando casos…" />
        ) : cases.length === 0 ? (
          <p className="px-6 pb-5 text-sm text-muted-foreground">Sin casos. Cree uno con «Nuevo caso».</p>
        ) : (
          <table className="w-full">
            <caption className="sr-only">Casos del paciente</caption>
            <thead className="bg-muted/60">
              <tr>
                <th scope="col" className={thClass}>Código</th>
                <th scope="col" className={thClass}>Fecha</th>
                <th scope="col" className={thClass}>Estado</th>
                <th scope="col" className={thClass}>Triage</th>
                <th scope="col" className={cn(thClass, 'text-right')}>Imág.</th>
              </tr>
            </thead>
            <tbody>
              {cases.map((c) => (
                <tr key={c.id} className="hover:bg-accent/60">
                  <td className={tdClass}>
                    <button className="font-bold tabular-nums hover:text-brand hover:underline" onClick={() => onOpenCase(c.id)}>
                      {c.code}
                    </button>
                  </td>
                  <td className={cn(tdClass, 'text-muted-foreground tabular-nums')}>{formatDate(c.created_at)}</td>
                  <td className={tdClass}><StatusBadge status={c.status} /></td>
                  <td className={tdClass}><LevelBadge level={c.triage_level} /></td>
                  <td className={cn(tdClass, 'text-right tabular-nums text-muted-foreground')}>{c.image_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
      </div>

      <div className="space-y-6 min-w-0">
      <PatientTimeline
        patientId={patient.id}
        refreshKey={`${cases?.length ?? ''}-${patient.consent_given}-${patient.blocked_at ?? ''}`}
        onOpenCase={onOpenCase}
      />

      {!blocked && cases !== null && (
        <section className={cn(cardClass, 'p-6 space-y-3')} aria-labelledby="pd-delete">
          <h3 id="pd-delete" className={sectionTitle}>Eliminar paciente</h3>
          {hasCases ? (
            <p className="text-sm text-muted-foreground">
              Tiene casos clínicos, así que no se puede eliminar. Para suprimir sus datos, use «Bloquear datos» en Privacidad.
            </p>
          ) : confirmDelete ? (
            <div className="space-y-3">
              <p className="text-sm">
                Se eliminará a {patient.first_name} {patient.last_name} y su historial de consentimiento. Queda registrado
                en la auditoría y no se puede deshacer.
              </p>
              <div className="flex gap-2">
                <button className={dangerButton} disabled={saving} onClick={remove}>
                  {saving && <Loader2 aria-hidden className="w-4 h-4 animate-spin" />} Eliminar definitivamente
                </button>
                <button className={secondaryButton} onClick={() => setConfirmDelete(false)}>Cancelar</button>
              </div>
            </div>
          ) : (
            <>
              <p className="text-sm text-muted-foreground">
                Sin casos asociados.
              </p>
              <button className={secondaryButton} onClick={() => setConfirmDelete(true)}>
                <Trash2 aria-hidden className="w-4 h-4" /> Eliminar paciente
              </button>
            </>
          )}
        </section>
      )}
      </div>
      </div>
    </div>
  );
}

interface PatientsPanelProps {
  onOpenCase: (caseId: number) => void;
  onNewCase: (patient: Patient) => void;
}

/** Pacientes: buscar, registrar, editar, ver sus casos y eliminar (solo sin casos). */
export default function PatientsPanel({ onOpenCase, onNewCase }: PatientsPanelProps) {
  const [term, setTerm] = useState('');
  const [patients, setPatients] = useState<Patient[] | null>(null);
  const [selected, setSelected] = useState<Patient | null>(null);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (search?: string) => {
    const r = await apiClient.searchPatients(search?.trim() || undefined, true);
    if (r.data) {
      setPatients(r.data);
      setError(null);
    } else setError(r.error || 'No se pudieron cargar los pacientes.');
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const modal = (
    <PatientModal
      isOpen={creating}
      createOnly
      onClose={() => setCreating(false)}
      onSelectPatient={(p) => {
        setSelected(p);
        load(term);
      }}
    />
  );

  if (selected) {
    return (
      <div className={pageClass}>
        <button className={cn(ghostButton, '-ml-3 mb-4')} onClick={() => setSelected(null)}>
          <ChevronLeft aria-hidden className="w-4 h-4" /> Pacientes
        </button>
        <PatientDetail
          key={selected.id}
          patient={selected}
          onOpenCase={onOpenCase}
          onNewCase={onNewCase}
          onUpdated={(p) => {
            setSelected(p);
            setPatients((prev) => prev?.map((x) => (x.id === p.id ? p : x)) ?? null);
          }}
          onDeleted={(id) => {
            setSelected(null);
            setPatients((prev) => prev?.filter((x) => x.id !== id) ?? null);
          }}
        />
        {modal}
      </div>
    );
  }

  return (
    <div className={pageClass}>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <h1 className={pageTitle}>Pacientes</h1>
        <button className={primaryButton} onClick={() => setCreating(true)}>
          <UserPlus aria-hidden className="w-4 h-4" /> Nuevo paciente
        </button>
      </div>

      <ErrorMessage className="mt-4">{error}</ErrorMessage>

      <form
        className="mt-6 flex gap-2 max-w-xl"
        onSubmit={(e) => {
          e.preventDefault();
          load(term);
        }}
      >
        <label htmlFor="pp-search" className="sr-only">Buscar por RUT o nombre</label>
        <input id="pp-search" type="search" className={inputClass} placeholder="Buscar por RUT o nombre" value={term}
          onChange={(e) => setTerm(e.target.value)} />
        <button type="submit" className={secondaryButton}><Search aria-hidden className="w-4 h-4" /> Buscar</button>
      </form>

      <div className={cn(cardClass, 'mt-4 overflow-hidden')}>
        {patients === null ? (
          <Loading label="Cargando pacientes…" />
        ) : patients.length === 0 ? (
          <EmptyState title="Sin pacientes" icon={<Users aria-hidden className="w-8 h-8" />}>
            {term ? 'No hay coincidencias.' : 'Registre la primera con «Nuevo paciente».'}
          </EmptyState>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <caption className="sr-only">Lista de pacientes</caption>
              <thead className="bg-muted/60">
                <tr>
                  <th scope="col" className={cn(thClass, 'pl-5')}>Paciente</th>
                  <th scope="col" className={thClass}>RUT</th>
                  <th scope="col" className={cn(thClass, 'text-right')}>Edad</th>
                  <th scope="col" className={thClass}>Estado</th>
                  <th scope="col" className={cn(thClass, 'pr-5')}>Registrada</th>
                </tr>
              </thead>
              <tbody>
                {patients.map((p) => (
                  <tr key={p.id} onClick={() => setSelected(p)} className="cursor-pointer hover:bg-accent/60 transition-colors">
                    <td className={cn(tdClass, 'pl-5')}>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelected(p);
                        }}
                        className="font-semibold hover:text-brand hover:underline text-left"
                      >
                        {p.first_name} {p.last_name}
                      </button>
                    </td>
                    <td className={cn(tdClass, 'text-muted-foreground tabular-nums')}>{p.rut}</td>
                    <td className={cn(tdClass, 'text-right tabular-nums')}>{ageFrom(p.birth_date)}</td>
                    <td className={tdClass}><PatientState p={p} /></td>
                    <td className={cn(tdClass, 'pr-5 text-muted-foreground tabular-nums')}>{formatDate(p.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {patients && patients.length >= 50 && (
          <p className="px-5 py-3 border-t border-border text-sm text-muted-foreground">
            Se muestran las 50 más recientes. Use la búsqueda para encontrar otras.
          </p>
        )}
      </div>
      {modal}
    </div>
  );
}
