import { useEffect, useState } from 'react';
import { ArrowRight, FileDown, Loader2, PenLine, ShieldAlert, ShieldCheck } from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '../services/api';
import type {
  ClinicalCase,
  ClinicalReview,
  Me,
  Recommendation,
  ReportRecord,
  ReportSignature,
  ReviewInput,
  TriageAssessment,
  TriageResult,
} from '../types';
import { RECOMMENDATION_LABELS, TRIAGE_ASSESSMENT_LABELS } from '../types';
import { BIRADS_LABELS } from '../constants';
import { cn } from '../lib/cn';
import { LevelBadge } from './Badges';
import { ErrorMessage, SuccessMessage } from './Feedback';
import {
  cardClass,
  formatDateTime,
  inputClass,
  labelClass,
  primaryButton,
  secondaryButton,
  sectionTitle,
  textareaClass,
} from './ui';

interface ReviewPanelProps {
  caseData: ClinicalCase;
  me: Me;
  validationKey?: number;
  onChanged: () => void;
  onNextCase?: () => void;
  embedded?: boolean;
}

const ASSESSMENTS: TriageAssessment[] = ['APROPIADO', 'SOBREESTIMADO', 'SUBESTIMADO'];

const legendClass = 'px-1 text-sm font-bold text-foreground';

export default function ReviewPanel({ caseData, me, validationKey = 0, onChanged, onNextCase, embedded = false }: ReviewPanelProps) {
  const [review, setReview] = useState<ClinicalReview | null>(null);
  const [reports, setReports] = useState<ReportRecord[]>([]);
  const [signature, setSignature] = useState<ReportSignature | null>(null);
  const [password, setPassword] = useState('');
  const [triage, setTriage] = useState<TriageResult | null>(null);
  const [pendingValidations, setPendingValidations] = useState(0);
  const [form, setForm] = useState<ReviewInput>({
    birads_final: 1,
    findings: '',
    recommendation: 'CONTROL_RUTINA',
    triage_assessment: 'APROPIADO',
    triage_comment: '',
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  useEffect(() => {
    if (caseData.status !== 'CERRADO') return;
    apiClient.getReview(caseData.id).then((r) => r.data && setReview(r.data));
    apiClient.listReports(caseData.id).then((r) => r.data && setReports(r.data));
    // 404 = aún no firmado
    apiClient.getReportSignature(caseData.id).then((r) => setSignature(r.data ?? null));
  }, [caseData.id, caseData.status]);

  useEffect(() => {
    if (caseData.status !== 'EN_REVISION') return;
    apiClient.getTriage(caseData.id).then((r) => {
      if (!r.data) return;
      setTriage(r.data);
      // Si el médico ya ajustó el nivel, se sugiere la evaluación correspondiente
      const rank = { ALTA: 0, MEDIA: 1, BAJA: 2 } as const;
      if (r.data.override_by !== null && r.data.final_level !== r.data.computed_level) {
        const suggestion: TriageAssessment =
          rank[r.data.final_level] < rank[r.data.computed_level] ? 'SUBESTIMADO' : 'SOBREESTIMADO';
        setForm((f) => ({ ...f, triage_assessment: suggestion }));
      }
    });
  }, [caseData.id, caseData.status]);

  useEffect(() => {
    if (caseData.status !== 'EN_REVISION') return;
    apiClient.listImages(caseData.id).then((r) => {
      if (r.data) setPendingValidations(r.data.filter((i) => i.inference && !i.validation).length);
    });
  }, [caseData.id, caseData.status, validationKey]);

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
      if (!r.data) return r.error || 'No se pudo tomar el caso.';
      toast.success(`Caso ${caseData.code} en revisión`);
      onChanged();
      return null;
    });

  const submitReview = () =>
    run(async () => {
      const r = await apiClient.createReview(caseData.id, {
        ...form,
        findings: form.findings.trim(),
        triage_comment: form.triage_comment?.trim() || null,
      });
      if (!r.data) return r.error || 'No se pudo registrar la revisión.';
      setReview(r.data);
      toast.success(`Revisión registrada. Caso ${caseData.code} cerrado.`);
      onChanged();
      return null;
    });

  const sign = () =>
    run(async () => {
      const r = await apiClient.signReport(caseData.id, password);
      setPassword('');
      if (!r.data) return r.error || 'No se pudo firmar el reporte.';
      setSignature(r.data);
      setInfo(`Reporte firmado. Código de verificación ${r.data.verification_code}.`);
      return null;
    });

  const generate = () =>
    run(async () => {
      if (!review) return 'El caso no tiene revisión.';
      const medicoName = review.medico_id === me.id ? me.full_name : `Médico #${review.medico_id}`;
      // jsPDF se carga solo al generar el reporte, no en la carga inicial
      const { generateAndRegisterReport } = await import('../utils/generatePdf');
      const result = await generateAndRegisterReport(caseData, review, medicoName);
      if (result.error) return result.error;
      setInfo(`Reporte registrado (SHA-256 ${result.report!.content_hash.slice(0, 12)}…).`);
      const list = await apiClient.listReports(caseData.id);
      if (list.data) setReports(list.data);
      return null;
    });

  return (
    <section aria-labelledby={`review-${caseData.id}`} className={cn(embedded ? 'space-y-4' : cn(cardClass, 'p-6'), 'space-y-4')}>
      <h3 id={`review-${caseData.id}`} className={sectionTitle}>Revisión médica</h3>
      <ErrorMessage>{error}</ErrorMessage>
      <SuccessMessage>{info}</SuccessMessage>

      {caseData.status === 'ABIERTO' && (
        <p className="text-sm text-muted-foreground">El caso espera su triage antes de poder tomarse.</p>
      )}

      {caseData.status === 'PRIORIZADO' && (
        <div className="flex flex-wrap items-center gap-3">
          <button className={primaryButton} onClick={take} disabled={busy}>
            {busy && <Loader2 aria-hidden className="w-4 h-4 animate-spin" />}
            Tomar caso para revisión
          </button>
          <p className="text-sm text-muted-foreground">Queda asignado a usted y sale de la cola de otros médicos.</p>
        </div>
      )}

      {caseData.status === 'EN_REVISION' && (
        <div className="space-y-4">
          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className={labelClass} htmlFor="rv-birads">BI-RADS final</label>
              <select id="rv-birads" className={inputClass} value={form.birads_final}
                onChange={(e) => setForm({ ...form, birads_final: Number(e.target.value) })}>
                {Object.entries(BIRADS_LABELS).map(([k, label]) => <option key={k} value={k}>{label}</option>)}
              </select>
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
          </div>
          <div>
            <label className={labelClass} htmlFor="rv-findings">Hallazgos</label>
            <textarea id="rv-findings" rows={4} className={textareaClass} value={form.findings}
              aria-describedby="rv-findings-hint"
              onChange={(e) => setForm({ ...form, findings: e.target.value })} />
            <p id="rv-findings-hint" className="mt-1 text-xs text-muted-foreground">Obligatorio (mínimo 5 caracteres).</p>
          </div>
          <fieldset className="px-4 pb-4 pt-2 rounded-lg border border-border space-y-2.5">
            <legend className={legendClass}>Evaluación del triage</legend>
            {triage && (
              <p className="text-sm text-muted-foreground flex flex-wrap items-center gap-2">
                Nivel vigente <LevelBadge level={triage.final_level} /> · puntaje{' '}
                <span className="tabular-nums">{triage.score.toFixed(1).replace('.', ',')}</span> · configuración v{triage.config_version}
              </p>
            )}
            <div className="flex flex-wrap gap-x-6 gap-y-2">
              {ASSESSMENTS.map((a) => (
                <label key={a} className="inline-flex items-center gap-2 text-sm">
                  <input
                    type="radio"
                    name={`triage-assessment-${caseData.id}`}
                    checked={form.triage_assessment === a}
                    onChange={() => setForm({ ...form, triage_assessment: a })}
                  />
                  {TRIAGE_ASSESSMENT_LABELS[a]}
                </label>
              ))}
            </div>
            <label htmlFor="rv-triage-comment" className="sr-only">Comentario sobre el triage</label>
            <input
              id="rv-triage-comment"
              className={inputClass}
              placeholder="Comentario sobre el triage (opcional)"
              value={form.triage_comment ?? ''}
              onChange={(e) => setForm({ ...form, triage_comment: e.target.value })}
            />
          </fieldset>
          {pendingValidations > 0 && (
            <p role="status" className="text-sm font-semibold text-media">
              Falta validar el resultado de IA de {pendingValidations} {pendingValidations === 1 ? 'imagen' : 'imágenes'} antes de
              cerrar. Hágalo en la sección Imágenes.
            </p>
          )}
          <div className="flex flex-wrap items-center gap-3">
            <button
              className={primaryButton}
              onClick={submitReview}
              disabled={busy || form.findings.trim().length < 5 || pendingValidations > 0}
            >
              {busy && <Loader2 aria-hidden className="w-4 h-4 animate-spin" />}
              Registrar revisión y cerrar caso
            </button>
            <p className="text-xs text-muted-foreground">Al cerrar, el caso queda en solo lectura.</p>
          </div>
        </div>
      )}

      {caseData.status === 'CERRADO' && review && (
        <div className="space-y-4 text-sm">
          <dl className="grid grid-cols-[10rem_1fr] gap-x-4 gap-y-2">
            <dt className="text-muted-foreground">BI-RADS final</dt>
            <dd className="font-bold">{BIRADS_LABELS[review.birads_final] ?? review.birads_final}</dd>
            <dt className="text-muted-foreground">Hallazgos</dt>
            <dd>{review.findings}</dd>
            <dt className="text-muted-foreground">Recomendación</dt>
            <dd>{RECOMMENDATION_LABELS[review.recommendation]}</dd>
            <dt className="text-muted-foreground">Evaluación del triage</dt>
            <dd>
              {review.triage_assessment ? TRIAGE_ASSESSMENT_LABELS[review.triage_assessment] : 'No registrada'}
              {review.triage_level_at_review && (
                <span className="text-muted-foreground"> (nivel evaluado {review.triage_level_at_review}, v{review.triage_config_version_at_review})</span>
              )}
              {review.triage_comment && <span className="block text-muted-foreground">{review.triage_comment}</span>}
            </dd>
            <dt className="text-muted-foreground">Registrada</dt>
            <dd className="tabular-nums">{formatDateTime(review.created_at)}</dd>
          </dl>

          <fieldset className="px-4 pb-4 pt-2 rounded-lg border border-border space-y-3">
            <legend className={legendClass}>Firma del médico</legend>
            {signature ? (
              <p className={cn('flex items-start gap-2', signature.valid ? 'text-foreground' : 'text-destructive')}>
                {signature.valid ? (
                  <ShieldCheck aria-hidden className="w-5 h-5 shrink-0 text-baja" />
                ) : (
                  <ShieldAlert aria-hidden className="w-5 h-5 shrink-0" />
                )}
                <span>
                  Firmado por <strong>{signature.medico_name}</strong> el {formatDateTime(signature.signed_at)}. Código{' '}
                  <strong className="tabular-nums">{signature.verification_code}</strong>
                  {signature.valid ? ' · firma verificada.' : ' · el contenido cambió después de la firma.'}
                </span>
              </p>
            ) : review.medico_id === me.id ? (
              <form
                className="space-y-3"
                onSubmit={(e) => {
                  e.preventDefault();
                  sign();
                }}
              >
                <p className="text-muted-foreground">
                  Declaro mi conformidad con el contenido de este reporte, incluida la validación del resultado de IA de
                  cada imagen. Confirme con su contraseña.
                </p>
                <div className="flex flex-wrap gap-2">
                  <label htmlFor={`rv-sign-${caseData.id}`} className="sr-only">Contraseña para firmar</label>
                  <input
                    id={`rv-sign-${caseData.id}`}
                    type="password"
                    autoComplete="current-password"
                    className={cn(inputClass, 'w-64')}
                    placeholder="Contraseña"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                  <button type="submit" className={primaryButton} disabled={busy || !password}>
                    {busy ? <Loader2 aria-hidden className="w-4 h-4 animate-spin" /> : <PenLine aria-hidden className="w-4 h-4" />}
                    Firmar reporte
                  </button>
                </div>
              </form>
            ) : (
              <p className="font-semibold text-media">Pendiente de firma por el médico que registró la revisión.</p>
            )}
          </fieldset>

          <div className="flex flex-wrap items-center gap-3">
            <button className={primaryButton} onClick={generate} disabled={busy || !signature}>
              {busy ? <Loader2 aria-hidden className="w-4 h-4 animate-spin" /> : <FileDown aria-hidden className="w-4 h-4" />}
              Generar reporte PDF
            </button>
            {onNextCase && (
              <button className={secondaryButton} onClick={onNextCase}>
                Siguiente caso de la cola <ArrowRight aria-hidden className="w-4 h-4" />
              </button>
            )}
          </div>
          {!signature && <p className="text-xs text-muted-foreground">El PDF se emite una vez firmado el reporte.</p>}
          {reports.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-muted-foreground">Reportes generados</h4>
              <ul className="mt-1">
                {reports.map((r) => (
                  <li key={r.id} className="text-sm text-muted-foreground tabular-nums">
                    {formatDateTime(r.generated_at)} · SHA-256 {r.content_hash.slice(0, 16)}…
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
