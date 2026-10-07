import { useEffect, useState } from 'react';
import { ClipboardCheck, FileDown, Loader2 } from 'lucide-react';
import { apiClient } from '../services/api';
import type { ClinicalCase, ClinicalReview, Me, Recommendation, ReportRecord, ReviewInput } from '../types';
import { RECOMMENDATION_LABELS } from '../types';
import { BIRADS_LABELS } from '../constants';
import { generateAndRegisterReport } from '../utils/generatePdf';
import { cardClass, errorBox, formatDateTime, inputClass, labelClass, primaryButton } from './ui';

interface ReviewPanelProps {
  caseData: ClinicalCase;
  me: Me;
  onChanged: () => void;
}

export default function ReviewPanel({ caseData, me, onChanged }: ReviewPanelProps) {
  const [review, setReview] = useState<ClinicalReview | null>(null);
  const [reports, setReports] = useState<ReportRecord[]>([]);
  const [form, setForm] = useState<ReviewInput>({ birads_final: 1, findings: '', recommendation: 'CONTROL_RUTINA' });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  useEffect(() => {
    if (caseData.status !== 'CERRADO') return;
    apiClient.getReview(caseData.id).then((r) => r.data && setReview(r.data));
    apiClient.listReports(caseData.id).then((r) => r.data && setReports(r.data));
  }, [caseData.id, caseData.status]);

  const run = async (fn: () => Promise<string | null>) => {
    setBusy(true);
    setError(null);
    setInfo(null);
    const err = await fn();
    setBusy(false);
    if (err) setError(err);
  };

  const take = () =>
    run(async () => {
      const r = await apiClient.takeCase(caseData.id);
      if (!r.data) return r.error || 'No se pudo tomar el caso';
      onChanged();
      return null;
    });

  const submitReview = () =>
    run(async () => {
      const r = await apiClient.createReview(caseData.id, { ...form, findings: form.findings.trim() });
      if (!r.data) return r.error || 'No se pudo registrar la revisión';
      setReview(r.data);
      onChanged();
      return null;
    });

  const generate = () =>
    run(async () => {
      if (!review) return 'El caso no tiene revisión';
      const medicoName = review.medico_id === me.id ? me.full_name : `Médico #${review.medico_id}`;
      const result = await generateAndRegisterReport(caseData, review, medicoName);
      if (result.error) return result.error;
      setInfo(`Reporte registrado (SHA-256 ${result.report!.content_hash.slice(0, 12)}…).`);
      const list = await apiClient.listReports(caseData.id);
      if (list.data) setReports(list.data);
      return null;
    });

  return (
    <div className={`${cardClass} p-4 space-y-3`}>
      <h4 className="text-xs font-semibold text-foreground flex items-center gap-1.5">
        <ClipboardCheck className="w-3.5 h-3.5 text-primary" /> Revisión médica
      </h4>
      {error && <div className={errorBox}>{error}</div>}
      {info && <div className="p-2 bg-green-500/10 border border-green-500/20 text-green-300 rounded text-xs">{info}</div>}

      {caseData.status === 'ABIERTO' && (
        <p className="text-[10px] text-muted-foreground">El caso espera su triage antes de poder tomarse.</p>
      )}

      {caseData.status === 'PRIORIZADO' && (
        <button className={primaryButton} onClick={take} disabled={busy}>
          {busy ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Tomar caso para revisión'}
        </button>
      )}

      {caseData.status === 'EN_REVISION' && (
        <div className="space-y-2">
          <div>
            <label className={labelClass} htmlFor="rv-birads">BI-RADS final</label>
            <select id="rv-birads" className={inputClass} value={form.birads_final}
              onChange={(e) => setForm({ ...form, birads_final: Number(e.target.value) })}>
              {Object.entries(BIRADS_LABELS).map(([k, label]) => <option key={k} value={k}>{label}</option>)}
            </select>
          </div>
          <div>
            <label className={labelClass} htmlFor="rv-findings">Hallazgos</label>
            <textarea id="rv-findings" rows={3} className={inputClass} value={form.findings}
              onChange={(e) => setForm({ ...form, findings: e.target.value })} />
          </div>
          <div>
            <label className={labelClass} htmlFor="rv-rec">Recomendación</label>
            <select id="rv-rec" className={inputClass} value={form.recommendation}
              onChange={(e) => setForm({ ...form, recommendation: e.target.value as Recommendation })}>
              {(Object.keys(RECOMMENDATION_LABELS) as Recommendation[]).map((r) => (
                <option key={r} value={r}>{RECOMMENDATION_LABELS[r]}</option>
              ))}
            </select>
          </div>
          <button className={primaryButton} onClick={submitReview} disabled={busy || form.findings.trim().length < 5}>
            {busy ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Registrar revisión y cerrar caso'}
          </button>
          <p className="text-[10px] text-muted-foreground">Al cerrar, el caso queda en solo lectura.</p>
        </div>
      )}

      {caseData.status === 'CERRADO' && review && (
        <div className="space-y-2 text-xs">
          <p><span className="text-muted-foreground">BI-RADS final:</span> <strong>{review.birads_final}</strong></p>
          <p><span className="text-muted-foreground">Hallazgos:</span> {review.findings}</p>
          <p><span className="text-muted-foreground">Recomendación:</span> {RECOMMENDATION_LABELS[review.recommendation]}</p>
          <p className="text-[10px] text-muted-foreground">Registrada el {formatDateTime(review.created_at)}</p>
          <button className={primaryButton} onClick={generate} disabled={busy}>
            {busy ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <FileDown className="w-3.5 h-3.5" />}
            Generar reporte PDF
          </button>
          {reports.length > 0 && (
            <div className="pt-1">
              <p className="text-[10px] font-semibold text-muted-foreground uppercase">Reportes generados</p>
              {reports.map((r) => (
                <p key={r.id} className="text-[10px] text-muted-foreground font-mono">
                  {formatDateTime(r.generated_at)} · {r.content_hash.slice(0, 16)}…
                </p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
