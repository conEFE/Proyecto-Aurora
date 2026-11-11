import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import type { AIVerdict, CaseStatus, DashboardMetrics, ModelPerformanceReport, TriageAssessment } from '../types';
import { AI_VERDICT_LABELS, CASE_STATUS_LABELS, TRIAGE_ASSESSMENT_LABELS } from '../types';

import {
  C,
  MARGIN,
  applyAssets,
  drawBrandHeader,
  drawFooter,
  drawNotice,
  lastY,
  loadPdfAssets,
  sectionTitle,
  tableStyle,
  text,
} from './pdfTheme';

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

interface ManagementReportInput {
  data: DashboardMetrics;
  model: ModelPerformanceReport | null;
  generatedBy: string;
  assets: Awaited<ReturnType<typeof loadPdfAssets>>;
}

/** Informe de gestión breve (1–2 páginas) con las métricas agregadas del Dashboard. Sin datos de pacientes. */
export function buildManagementReport({ data, model, generatedBy, assets }: ManagementReportInput): jsPDF {
  const doc = new jsPDF();
  applyAssets(doc, assets);
  const width = doc.internal.pageSize.getWidth();
  const table = tableStyle(0);
  const generatedAt = new Date();

  let y = drawBrandHeader(doc, assets, 'Informe de gestión', `Generado el ${generatedAt.toLocaleString('es-CL')}`);
  text(doc, C.ink, 22, 'extrabold');
  doc.text('Informe de gestión', MARGIN, y + 6);
  text(doc, C.muted, 9);
  const period =
    data.date_from || data.date_to
      ? `Período: ${day(data.date_from) || 'inicio'} – ${day(data.date_to) || 'hoy'}`
      : 'Período: todos los registros';
  doc.text(`${period} · Métricas agregadas, sin datos identificables de pacientes`, MARGIN, y + 12);
  y += 19;
  if (data.ai_validations_simulated > 0 || model?.versions.some((v) => v.is_simulated))
    y = drawNotice(doc, y, 'IA SIMULADA', 'Incluye resultados de IA simulada: no son resultados clínicos.', C.sim, C.simBg);
  y = sectionTitle(doc, y + 2, 'Indicadores y metas');

  autoTable(doc, {
    ...table,
    startY: y + 1,
    head: [['Indicador', 'Valor', 'Meta', 'Estado']],
    columnStyles: { 1: { halign: 'right', fontStyle: 'bold' }, 2: { textColor: C.muted } },
    didParseCell: (cell) => {
      if (cell.section === 'body' && cell.column.index === 3) {
        const raw = String(cell.cell.raw);
        if (raw === 'Cumple') cell.cell.styles.textColor = C.level.BAJA;
        if (raw === 'No cumple') cell.cell.styles.textColor = C.level.ALTA;
      }
    },
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

  const half = (width - 2 * MARGIN - 8) / 2;
  y = sectionTitle(doc, lastY(doc) + 10, 'Casos por nivel y estado');
  const top = y + 1;
  autoTable(doc, {
    ...table,
    startY: top,
    margin: { left: MARGIN, right: width - MARGIN - half },
    head: [['Nivel de triage', 'Casos', 'Triage a revisión']],
    body: LEVELS.map((l) => {
      const h = data.avg_triage_to_review_hours_by_level[l];
      return [l, String(data.cases_by_level[l] ?? 0), h === null ? '—' : `${dec(h)} h`];
    }),
    columnStyles: { 1: { halign: 'right' }, 2: { halign: 'right' } },
    didParseCell: (cell) => {
      if (cell.section === 'body' && cell.column.index === 0) {
        cell.cell.styles.textColor = C.level[String(cell.cell.raw)] ?? C.ink;
        cell.cell.styles.fontStyle = 'bold';
      }
    },
  });
  const leftEnd = lastY(doc);
  autoTable(doc, {
    ...table,
    startY: top,
    margin: { left: MARGIN + half + 8, right: MARGIN },
    head: [['Estado del caso', 'Casos']],
    body: (Object.keys(data.cases_by_status) as CaseStatus[]).map((s) => [
      CASE_STATUS_LABELS[s],
      String(data.cases_by_status[s]),
    ]),
    columnStyles: { 1: { halign: 'right' } },
  });

  const weeks = data.cases_per_week.slice(-12);
  y = sectionTitle(doc, Math.max(leftEnd, lastY(doc)) + 10, 'Casos creados por semana');
  autoTable(doc, {
    ...table,
    startY: y + 1,
    head: [['Semana del', ...weeks.map((w) => day(w.week_start).slice(0, 5))]],
    body: [['Casos', ...weeks.map((w) => String(w.cases))]],
    styles: { ...table.styles, fontSize: 8, cellPadding: 1.8, halign: 'center' },
  });

  y = sectionTitle(doc, lastY(doc) + 10, 'Calidad de las decisiones');
  autoTable(doc, {
    ...table,
    startY: y + 1,
    head: [['Indicador', 'Valor', 'Desglose']],
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
    columnStyles: { 1: { halign: 'right', fontStyle: 'bold' }, 2: { cellWidth: 78, textColor: C.muted } },
  });

  if (model && model.versions.length > 0) {
    // El título no queda solo al pie: si no cabe el bloque, pasa a la página siguiente
    y = lastY(doc) + 10;
    if (y + 12 + model.versions.length * 9 > doc.internal.pageSize.getHeight() - 22) {
      doc.addPage();
      y = 40;
    }
    y = sectionTitle(doc, y, 'Desempeño del modelo por versión');
    autoTable(doc, {
      ...table,
      startY: y + 1,
      head: [['Modelo', 'Evaluables', 'Exactitud', 'Sensibilidad', 'Especificidad', `Meta K5 (${pct(model.k5_target)})`]],
      body: model.versions.map((v) => [
        `${v.model_version}${v.is_simulated ? ' · IA SIMULADA' : ''}`,
        String(v.evaluable),
        pct(v.accuracy),
        pct(v.sensitivity),
        pct(v.specificity),
        okText(v.meets_k5),
      ]),
    });
  }

  drawFooter(doc, `Informe de gestión · Generado el ${generatedAt.toLocaleString('es-CL')} por ${generatedBy}`, {
    assets,
    kind: 'Informe de gestión',
    detail: period.replace('Período: ', ''),
  });
  return doc;
}
