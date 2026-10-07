import { useEffect, useState } from 'react';
import { Loader2, Save, User } from 'lucide-react';
import { apiClient } from '../services/api';
import type { CaseSymptoms, ClinicalCase, Me } from '../types';
import { StatusBadge } from './Badges';
import CaseImages from './CaseImages';
import SymptomsForm from './SymptomsForm';
import { cardClass, errorBox, formatDate, formatDateTime, primaryButton } from './ui';

interface CaseDetailProps {
  caseId: number;
  me: Me;
  onChanged: () => void;
}

function ageFrom(birthDate: string): number {
  const b = new Date(birthDate);
  const now = new Date();
  let age = now.getFullYear() - b.getFullYear();
  const m = now.getMonth() - b.getMonth();
  if (m < 0 || (m === 0 && now.getDate() < b.getDate())) age--;
  return age;
}

function symptomsOf(c: ClinicalCase): CaseSymptoms {
  return {
    palpable_mass: c.palpable_mass,
    nipple_discharge: c.nipple_discharge,
    skin_or_nipple_changes: c.skin_or_nipple_changes,
    birads_reported: c.birads_reported,
  };
}

export default function CaseDetail({ caseId, me, onChanged }: CaseDetailProps) {
  const [data, setData] = useState<ClinicalCase | null>(null);
  const [symptoms, setSymptoms] = useState<CaseSymptoms | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let cancelled = false;
    apiClient.getCase(caseId).then((r) => {
      if (cancelled) return;
      if (r.data) {
        setData(r.data);
        setSymptoms(symptomsOf(r.data));
        setError(null);
      } else setError(r.error || 'Error al cargar el caso');
    });
    return () => {
      cancelled = true;
    };
  }, [caseId]);

  if (error && !data) return <div className={errorBox}>{error}</div>;
  if (!data || !symptoms) {
    return (
      <div className={`${cardClass} p-8 flex justify-center`}>
        <Loader2 className="w-6 h-6 animate-spin text-primary" />
      </div>
    );
  }

  const closed = data.status === 'CERRADO';
  const dirty = JSON.stringify(symptoms) !== JSON.stringify(symptomsOf(data));

  const save = async () => {
    setSaving(true);
    const r = await apiClient.updateCase(data.id, symptoms);
    setSaving(false);
    if (r.data) {
      setData(r.data);
      setSymptoms(symptomsOf(r.data));
      setError(null);
      onChanged();
    } else setError(r.error || 'No se pudo guardar');
  };

  return (
    <div className="space-y-3">
      <div className={`${cardClass} p-4 space-y-3`}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-foreground">{data.code}</h3>
            <p className="text-[10px] text-muted-foreground">Creado el {formatDateTime(data.created_at)}</p>
          </div>
          <StatusBadge status={data.status} />
        </div>

        {data.patient && (
          <div className="p-2 bg-secondary/40 rounded flex items-start gap-2">
            <User className="w-4 h-4 text-primary mt-0.5" />
            <div className="text-xs">
              <p className="font-semibold text-foreground">
                {data.patient.first_name} {data.patient.last_name}
              </p>
              <p className="text-[10px] text-muted-foreground">
                RUT {data.patient.rut} · {ageFrom(data.patient.birth_date)} años (nac. {formatDate(data.patient.birth_date)})
              </p>
              <p className="text-[10px] text-muted-foreground">
                Antecedente familiar 1er grado: {data.patient.family_history_first_degree ? 'Sí' : 'No'} · Cáncer de
                mama previo: {data.patient.previous_breast_cancer ? 'Sí' : 'No'}
              </p>
            </div>
          </div>
        )}

        {error && <div className={errorBox}>{error}</div>}

        <SymptomsForm value={symptoms} onChange={setSymptoms} disabled={closed} />
        {closed ? (
          <p className="text-[10px] text-muted-foreground">Caso cerrado el {formatDateTime(data.closed_at)}: solo lectura.</p>
        ) : (
          <button className={primaryButton} disabled={!dirty || saving} onClick={save}>
            {saving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
            Guardar antecedentes
          </button>
        )}

      </div>

      <div className={`${cardClass} p-4`}>
        <h4 className="text-xs font-semibold text-foreground mb-2">Imágenes ({data.image_count})</h4>
        <CaseImages caseId={data.id} me={me} />
      </div>
    </div>
  );
}
