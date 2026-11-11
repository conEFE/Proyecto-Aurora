import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import type { AIVerdict, CaseStatus, DashboardMetrics, ModelPerformanceReport, TriageAssessment } from '../types';
import { AI_VERDICT_LABELS, CASE_STATUS_LABELS, TRIAGE_ASSESSMENT_LABELS } from '../types';

type RGB = [number, number, number];
const PRIMARY: RGB = [124, 58, 237];
const LEVELS = ['ALTA', 'MEDIA', 'BAJA'] as const;

const dec = (n: number, d = 1) => n.toFixed(d).replace('.', ',');
const pct = (v: number | null) => (v === null ? '—' : `${dec(v * 100)} %`);
const okText = (ok: boolean | null) => (ok === null ? '—' : ok ? 'Cumple' : 'No cumple');

function seconds(s: number | null): string {
  if (s === null) return '—';
  if (s < 60) return `${s.toFixed(0)} s`;
  if (s < 3600) return `${dec(s / 60)} min`;
  return `${dec(s / 3600)} h`;
}

function day(iso: string | null): string {
  return iso ? new Date(iso).toLocaleDateString('es-CL') : '';
}

function lastY(doc: jsPDF): number {
  return (doc as unknown as { lastAutoTable: { finalY: number } }).lastAutoTable.finalY;
}

interface ManagementReportInput {
  data: DashboardMetrics;
  model: ModelPerformanceReport | null;
  generatedBy: string;
}

/** Informe de gestión breve (1–2 páginas) con las métricas agregadas del Dashboard. Sin datos de pacientes. */
export function buildManagementReport({ data, model, generatedBy }: ManagementReportInput): jsPDF {
  const doc = new jsPDF();
  const width = doc.internal.pageSize.getWidth();
  const head = { fillColor: PRIMARY, textColor: 255 as const, fontStyle: 'bold' as const };
  const table = { theme: 'grid' as const, headStyles: head, styles: { fontSize: 9, cellPadding: 2 }, margin: { left: 14, right: 14 } };

  doc.setFillColor(...PRIMARY);
  doc.rect(0, 0, width, 26, 'F');
  doc.setTextColor(255);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(16);
  doc.text('Proyecto Aurora · Informe de gestión', 14, 12);
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(9);
  const period =
    data.date_from || data.date_to
      ? `Período: ${day(data.date_from) || 'inicio'} – ${day(data.date_to) || 'hoy'}`
      : 'Período: todos los registros';
  doc.text(`${period} · Generado el ${new Date().toLocaleString('es-CL')} por ${generatedBy}`, 14, 20);
  doc.setTextColor(0);

  autoTable(doc, {
    ...table,
    startY: 32,
    head: [['Indicador', 'Valor', 'Meta', 'Estado']],
    body: [
      ['Casos en el período', data.total_cases.toLocaleString('es-CL'), '—', '—'],
      [
        'Creación a triage (promedio)',
        seconds(data.avg_creation_to_triage_seconds),
        'máx. 5 min',
        okText(
          data.avg_creation_to_triage_seconds === null
            ? null
            : data.avg_creation_to_triage_seconds <= data.kpi_creation_to_triage_target_seconds,
        ),
      ],
      [
        `Casos ALTA pendientes más de ${data.alta_pending_threshold_hours} h`,
        String(data.alta_pending_over_hours),
        '0',
        okText(data.alta_pending_over_hours === 0),
      ],
      [
        `Respuesta de la API, p95 (${data.api_requests} solicitudes)`,
        data.api_p95_ms === null ? '—' : `${data.api_p95_ms.toFixed(0)} ms`,
        '< 3 s',
        okText(data.api_p95_ms === null ? null : data.api_p95_ms < data.kpi_api_p95_target_ms),
      ],
      ['Errores del servidor (5xx)', `${data.server_errors} (${pct(data.server_error_rate)})`, '—', '—'],
    ],
  });

  const half = (width - 28 - 6) / 2;
  const y = lastY(doc) + 8;
  autoTable(doc, {
    ...table,
    startY: y,
    margin: { left: 14, right: width - 14 - half },
    head: [['Nivel de triage', 'Casos', 'Triage a revisión']],
    body: LEVELS.map((l) => {
      const h = data.avg_triage_to_review_hours_by_level[l];
      return [l, String(data.cases_by_level[l] ?? 0), h === null ? '—' : `${dec(h)} h`];
    }),
  });
  const leftEnd = lastY(doc);
  autoTable(doc, {
    ...table,
    startY: y,
    margin: { left: 14 + half + 6, right: 14 },
    head: [['Estado del caso', 'Casos']],
    body: (Object.keys(data.cases_by_status) as CaseStatus[]).map((s) => [
      CASE_STATUS_LABELS[s],
      String(data.cases_by_status[s]),
    ]),
  });
  const weeks = data.cases_per_week.slice(-12);
  autoTable(doc, {
    ...table,
    startY: Math.max(leftEnd, lastY(doc)) + 8,
    head: [['Semana del', ...weeks.map((w) => day(w.week_start).slice(0, 5))]],
    body: [['Casos', ...weeks.map((w) => String(w.cases))]],
    styles: { fontSize: 8, cellPadding: 1.5, halign: 'center' },
  });

  autoTable(doc, {
    ...table,
    startY: lastY(doc) + 8,
    head: [['Calidad de las decisiones', 'Valor', 'Desglose']],
    body: [
      [
        'Ajustes médicos del nivel',
        pct(data.override_ratio),
        `${data.triage_overrides} de ${data.triage_total} cálculos ajustados`,
      ],
      [
        `Concordancia IA – médico (${data.ai_validations_total} validaciones)`,
        pct(data.ai_agreement_rate),
        (Object.keys(AI_VERDICT_LABELS) as AIVerdict[])
          .map((v) => `${data.ai_validations_by_verdict[v] ?? 0} ${AI_VERDICT_LABELS[v].toLowerCase()}`)
          .join(' · '),
      ],
      [
        `Aprobación del triage (${data.triage_assessments_total} evaluaciones)`,
        pct(data.triage_agreement_rate),
        (Object.keys(TRIAGE_ASSESSMENT_LABELS) as TriageAssessment[])
          .map((v) => `${data.triage_assessments_by_value[v] ?? 0} ${TRIAGE_ASSESSMENT_LABELS[v].toLowerCase()}`)
          .join(' · '),
      ],
    ],
    columnStyles: { 2: { cellWidth: 80 } },
  });

  if (model && model.versions.length > 0) {
    autoTable(doc, {
      ...table,
      startY: lastY(doc) + 8,
      head: [['Modelo', 'Evaluables', 'Exactitud', 'Sensibilidad', 'Especificidad', `Meta K5 (${pct(model.k5_target)})`]],
      body: model.versions.map((v) => [
        `${v.model_version}${v.is_simulated ? ' (IA SIMULADA)' : ''}`,
        String(v.evaluable),
        pct(v.accuracy),
        pct(v.sensitivity),
        pct(v.specificity),
        okText(v.meets_k5),
      ]),
    });
  }

  const pages = doc.getNumberOfPages();
  for (let i = 1; i <= pages; i++) {
    doc.setPage(i);
    doc.setFontSize(7.5);
    doc.setTextColor(110);
    const note =
      data.ai_validations_simulated > 0 || model?.versions.some((v) => v.is_simulated)
        ? 'Incluye resultados de IA SIMULADA: no son resultados clínicos. '
        : '';
    const footer = doc.splitTextToSize(
      `${note}Métricas agregadas, sin datos identificables de pacientes. La plataforma apoya, no reemplaza, el criterio médico.`,
      width - 28 - 14,
    );
    doc.text(footer, 14, doc.internal.pageSize.getHeight() - 12);
    doc.text(`${i}/${pages}`, width - 14, doc.internal.pageSize.getHeight() - 12, { align: 'right' });
  }
  return doc;
}
