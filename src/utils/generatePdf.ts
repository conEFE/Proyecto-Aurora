import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { apiClient } from '../services/api';
import type { CaseImage, ClinicalCase, ClinicalReview, DicomMetadata, ReportRecord, TriageResult } from '../types';
import { AI_VERDICT_LABELS, EXAM_TYPE_LABELS, RECOMMENDATION_LABELS, TRIAGE_ASSESSMENT_LABELS } from '../types';

type RGB = [number, number, number];
const PRIMARY: RGB = [124, 58, 237];
const AMBER: RGB = [217, 119, 6];
const LEVEL_COLOR: Record<string, RGB> = { ALTA: [220, 38, 38], MEDIA: [217, 119, 6], BAJA: [22, 163, 74] };

const FACTOR_LABELS: Record<string, string> = {
  ai: 'IA (máx. confianza con hallazgo)',
  age: 'Edad',
  family_history: 'Antecedente familiar 1er grado',
  previous_cancer: 'Cáncer de mama previo',
  wait_time: 'Tiempo de espera',
};

export async function sha256Hex(data: ArrayBuffer): Promise<string> {
  const digest = await crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

function ageFrom(birthDate: string): number {
  const b = new Date(birthDate);
  const now = new Date();
  let age = now.getFullYear() - b.getFullYear();
  if (now.getMonth() < b.getMonth() || (now.getMonth() === b.getMonth() && now.getDate() < b.getDate())) age--;
  return age;
}

function lastY(doc: jsPDF): number {
  return (doc as unknown as { lastAutoTable: { finalY: number } }).lastAutoTable.finalY;
}

interface ReportInput {
  caseData: ClinicalCase;
  triage: TriageResult | null;
  review: ClinicalReview;
  metadata: DicomMetadata;
  medicoName: string;
  images?: CaseImage[];
}

/** Construye el PDF. Identifica el caso solo por su código anónimo (sin nombre ni RUT). */
export function buildCaseReport({ caseData, triage, review, metadata, medicoName, images = [] }: ReportInput): jsPDF {
  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 18;
  const generatedAt = new Date();
  const simulated = metadata.AIIsSimulated === true;

  // Metadatos tipo DICOM (SC-02) incrustados en las propiedades del documento
  doc.setProperties({
    title: `Reporte ${caseData.code}`,
    subject: 'Proyecto Aurora - apoyo a la priorización',
    author: medicoName,
    keywords: JSON.stringify(metadata),
    creator: 'Proyecto Aurora',
  });

  doc.setFillColor(...PRIMARY);
  doc.rect(0, 0, pageWidth, 32, 'F');
  doc.setTextColor(255, 255, 255);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(16);
  doc.text('Reporte de caso — Proyecto Aurora', margin, 15);
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(9);
  doc.text('Plataforma de apoyo a la detección temprana y priorización. No reemplaza el criterio médico.', margin, 23);
  doc.setTextColor(0, 0, 0);

  let y = 40;
  if (simulated) {
    doc.setFillColor(...AMBER);
    doc.roundedRect(margin, y, pageWidth - 2 * margin, 12, 2, 2, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(9);
    doc.text('IA SIMULADA: los resultados de análisis de imagen son ficticios y no tienen valor clínico.', pageWidth / 2, y + 7.5, {
      align: 'center',
    });
    doc.setTextColor(0, 0, 0);
    y += 18;
  }

  const section = (title: string) => {
    if (y > pageHeight - 50) {
      doc.addPage();
      y = margin;
    }
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(12);
    doc.text(title, margin, y);
    y += 4;
  };
  const table = (head: string[], body: Array<Array<string>>) => {
    autoTable(doc, {
      startY: y,
      head: [head],
      body,
      theme: 'striped',
      headStyles: { fillColor: PRIMARY, textColor: [255, 255, 255] },
      margin: { left: margin, right: margin },
      styles: { fontSize: 8.5 },
    });
    y = lastY(doc) + 10;
  };

  section('Caso');
  table(
    ['Campo', 'Valor'],
    [
      ['Código anónimo', caseData.code],
      ['Edad de la paciente', caseData.patient ? `${ageFrom(caseData.patient.birth_date)} años` : '—'],
      ['Fecha de creación', new Date(caseData.created_at).toLocaleString('es-CL')],
      ['Fecha de cierre', caseData.closed_at ? new Date(caseData.closed_at).toLocaleString('es-CL') : '—'],
      ['Síntomas', [
        caseData.palpable_mass && 'masa palpable',
        caseData.nipple_discharge && 'secreción por el pezón',
        caseData.skin_or_nipple_changes && 'cambios en piel/pezón',
      ].filter(Boolean).join(', ') || 'ninguno'],
      ['BI-RADS informado', caseData.birads_reported === null ? 'sin informe' : String(caseData.birads_reported)],
    ]
  );

  if (triage) {
    section('Triage');
    const color = LEVEL_COLOR[triage.final_level];
    doc.setFillColor(...color);
    doc.roundedRect(margin, y, 60, 9, 2, 2, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(9);
    doc.text(`Nivel ${triage.final_level}`, margin + 30, y + 6, { align: 'center' });
    doc.setTextColor(0, 0, 0);
    doc.setFont('helvetica', 'normal');
    doc.text(
      `Puntaje ${triage.score.toFixed(2)} / 100 · configuración v${triage.config_version}` +
        (triage.escalation_rule ? ` · regla ${triage.escalation_rule}` : ''),
      margin + 65,
      y + 6
    );
    y += 14;
    if (triage.override_by !== null) {
      doc.setFontSize(8.5);
      doc.text(`Nivel ajustado por médico (calculado: ${triage.computed_level}). Motivo: ${triage.override_reason ?? ''}`, margin, y, {
        maxWidth: pageWidth - 2 * margin,
      });
      y += 8;
    }
    if (triage.breakdown) {
      const b = triage.breakdown as unknown as Record<string, { value: number | boolean; weight: number; points: number }>;
      table(
        ['Factor', 'Valor', 'Peso', 'Aporte'],
        Object.keys(FACTOR_LABELS).map((k) => [
          FACTOR_LABELS[k] + (k === 'ai' && simulated ? ' [IA SIMULADA]' : ''),
          typeof b[k].value === 'boolean' ? (b[k].value ? 'Sí' : 'No') : String(b[k].value),
          String(b[k].weight),
          b[k].points.toFixed(2),
        ])
      );
    }
  }

  section('Revisión médica');
  table(
    ['Campo', 'Valor'],
    [
      ['BI-RADS final', String(review.birads_final)],
      ['Hallazgos', review.findings],
      ['Recomendación', RECOMMENDATION_LABELS[review.recommendation]],
      ['Médico', medicoName],
      ['Fecha', review.created_at ? new Date(review.created_at).toLocaleString('es-CL') : '—'],
    ]
  );

  section('Validación médica de la IA y del triage');
  const validated = images.filter((img) => img.inference);
  table(
    ['Elemento', 'Resultado IA', 'Validación del médico'],
    [
      ...validated.map((img) => [
        `${EXAM_TYPE_LABELS[img.exam_type]}${img.laterality ? ` (${img.laterality === 'L' ? 'izq.' : 'der.'})` : ''}`,
        `${img.inference!.detected ? 'Hallazgo' : 'Sin hallazgos'} ${img.inference!.confidence.toFixed(1)}%` +
          (img.inference!.is_simulated ? ' [IA SIMULADA]' : ''),
        img.validation
          ? AI_VERDICT_LABELS[img.validation.verdict] + (img.validation.comment ? ` — ${img.validation.comment}` : '')
          : 'Sin validar',
      ]),
      [
        'Triage',
        review.triage_level_at_review
          ? `Nivel ${review.triage_level_at_review} (configuración v${review.triage_config_version_at_review})`
          : '—',
        review.triage_assessment
          ? TRIAGE_ASSESSMENT_LABELS[review.triage_assessment] + (review.triage_comment ? ` — ${review.triage_comment}` : '')
          : 'No registrada',
      ],
    ]
  );

  section('Metadatos tipo DICOM (SC-02)');
  table(
    ['Atributo', 'Valor'],
    Object.entries(metadata).map(([k, v]) => [k, Array.isArray(v) ? v.join(', ') : v === null ? '—' : String(v)])
  );

  const pages = doc.getNumberOfPages();
  for (let i = 1; i <= pages; i++) {
    doc.setPage(i);
    doc.setFontSize(7.5);
    doc.setTextColor(120, 120, 120);
    doc.text(
      `${caseData.code} · Generado el ${generatedAt.toLocaleString('es-CL')} por ${medicoName} · Página ${i} de ${pages}`,
      pageWidth / 2,
      pageHeight - 8,
      { align: 'center' }
    );
  }
  return doc;
}

/** Genera el PDF, calcula su SHA-256, lo registra en el backend y descarga exactamente esos bytes. */
export async function generateAndRegisterReport(
  caseData: ClinicalCase,
  review: ClinicalReview,
  medicoName: string
): Promise<{ report?: ReportRecord; error?: string }> {
  const meta = await apiClient.getReportMetadata(caseData.id);
  if (!meta.data) return { error: meta.error || 'No se pudieron obtener los metadatos del reporte' };
  const [triage, images] = await Promise.all([apiClient.getTriage(caseData.id), apiClient.listImages(caseData.id)]);

  const doc = buildCaseReport({
    caseData,
    triage: triage.data ?? null,
    review,
    metadata: meta.data,
    medicoName,
    images: images.data ?? [],
  });
  const bytes = doc.output('arraybuffer');
  const hash = await sha256Hex(bytes);
  const registered = await apiClient.registerReport(caseData.id, hash);
  if (!registered.data) return { error: registered.error || 'No se pudo registrar el reporte' };

  const url = URL.createObjectURL(new Blob([bytes], { type: 'application/pdf' }));
  const a = document.createElement('a');
  a.href = url;
  a.download = `Reporte_${caseData.code}_${new Date().toISOString().slice(0, 10)}.pdf`;
  a.click();
  URL.revokeObjectURL(url);
  return { report: registered.data };
}
