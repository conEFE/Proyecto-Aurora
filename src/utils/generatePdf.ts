import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { apiClient } from '../services/api';
import type {
  CaseImage,
  ClinicalCase,
  ClinicalReview,
  DicomMetadata,
  MedicalSignatureBlock,
  ReportRecord,
  TriageResult,
} from '../types';
import { AI_VERDICT_LABELS, EXAM_TYPE_LABELS, RECOMMENDATION_LABELS, TRIAGE_ASSESSMENT_LABELS } from '../types';
import { RULE_LABELS } from '../constants';
import {
  C,
  MARGIN,
  applyAssets,
  drawBrandHeader,
  drawFooter,
  drawLevelStamp,
  drawNotice,
  kvStyle,
  lastY,
  loadPdfAssets,
  rule,
  sectionTitle,
  tableStyle,
  text,
} from './pdfTheme';

const FACTOR_LABELS: Record<string, string> = {
  ai: 'IA (máx. probabilidad de malignidad sobre el umbral)',
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

interface ReportInput {
  caseData: ClinicalCase;
  triage: TriageResult | null;
  review: ClinicalReview;
  metadata: DicomMetadata;
  medicoName: string;
  images?: CaseImage[];
  /** Miniaturas JPEG de las imágenes, por id (las que no se pudieron cargar se omiten). */
  thumbnails?: Record<number, Thumbnail>;
  assets: Awaited<ReturnType<typeof loadPdfAssets>>;
}

export interface Thumbnail {
  data: string;
  width: number;
  height: number;
}

const VIEWER: [number, number, number] = [16, 10, 20]; // Negatoscopio
const BOX: [number, number, number] = [245, 166, 35]; // marca del hallazgo, como en el visor

/** Reduce una imagen a JPEG (lado mayor 900 px) para incluirla en el PDF sin inflarlo. */
export async function makeThumbnail(blob: Blob, maxSide = 900): Promise<Thumbnail | null> {
  try {
    const bitmap = await createImageBitmap(blob);
    const scale = Math.min(1, maxSide / Math.max(bitmap.width, bitmap.height));
    const canvas = document.createElement('canvas');
    canvas.width = Math.round(bitmap.width * scale);
    canvas.height = Math.round(bitmap.height * scale);
    const ctx = canvas.getContext('2d');
    if (!ctx) return null;
    ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
    bitmap.close();
    return { data: canvas.toDataURL('image/jpeg', 0.82), width: canvas.width, height: canvas.height };
  } catch {
    return null;
  }
}

const sideName = (l?: string | null) => (l === 'L' ? 'Izquierda' : l === 'R' ? 'Derecha' : 'Sin lado');

const STATUS_LABEL: Record<string, string> = {
  ABIERTO: 'Abierto',
  PRIORIZADO: 'Priorizado',
  EN_REVISION: 'En revisión',
  CERRADO: 'Cerrado',
};

/** Construye el PDF con el sistema visual de la interfaz. Identifica el caso solo por su código anónimo. */
export function buildCaseReport({ caseData, triage, review, metadata, medicoName, images = [], thumbnails = {}, assets }: ReportInput): jsPDF {
  const doc = new jsPDF();
  applyAssets(doc, assets);
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const contentWidth = pageWidth - 2 * MARGIN;
  const generatedAt = new Date();
  const simulated = metadata.AIIsSimulated === true;
  const prototype = metadata.AIIsPrototype === true;
  const fmt = (v?: string | null) => (v ? new Date(v).toLocaleString('es-CL') : '—');

  // Metadatos tipo DICOM incrustados en las propiedades del documento
  doc.setProperties({
    title: `Reporte ${caseData.code}`,
    subject: 'Aurora Care - apoyo a la priorización',
    author: medicoName,
    keywords: JSON.stringify(metadata),
    creator: 'Aurora Care',
  });

  let y = drawBrandHeader(doc, assets, 'Reporte de caso', `Generado el ${generatedAt.toLocaleString('es-CL')}`);

  // Titular: código del caso (Display) con su timbre de nivel y estado, como en el detalle del caso
  text(doc, C.ink, 24, 'extrabold');
  doc.text(caseData.code, MARGIN, y + 6);
  text(doc, C.muted, 8.5);
  doc.text(`Creado el ${fmt(caseData.created_at)}  ·  Cerrado el ${fmt(caseData.closed_at)}`, MARGIN, y + 12);
  if (triage) {
    const level = triage.final_level;
    text(doc, C.ink, 13, 'extrabold');
    const stampWidth = 2 * 2.6 + 2 + doc.getTextWidth(level) + level.length * 0.25;
    drawLevelStamp(doc, pageWidth - MARGIN - stampWidth, y + 4, level, 'lg');
  }
  text(doc, C.muted, 8.5);
  doc.text(STATUS_LABEL[caseData.status] ?? caseData.status, pageWidth - MARGIN, y + 12, { align: 'right' });
  y += 18;

  // Paciente (anónimo) en tres columnas, entre reglas finas
  rule(doc, y);
  const col = contentWidth / 3;
  const symptoms =
    [
      caseData.palpable_mass && 'masa palpable',
      caseData.nipple_discharge && 'secreción por el pezón',
      caseData.skin_or_nipple_changes && 'cambios en piel o pezón',
    ]
      .filter(Boolean)
      .join(', ') || 'ninguno';
  const cells: Array<[string, string, string]> = [
    ['Edad de la paciente', caseData.patient ? `${ageFrom(caseData.patient.birth_date)} años` : '—', ''],
    ['Síntomas', symptoms, ''],
    ['BI-RADS informado', caseData.birads_reported === null ? 'Sin informe' : String(caseData.birads_reported), ''],
  ];
  cells.forEach(([label, value], i) => {
    text(doc, C.muted, 7.5);
    doc.text(label, MARGIN + i * col, y + 6);
    text(doc, C.ink, 9.5, 'bold');
    doc.text(value, MARGIN + i * col, y + 11.5, { maxWidth: col - 4 });
  });
  y += 17;
  rule(doc, y);
  y += 7;

  if (simulated)
    y = drawNotice(doc, y, 'IA SIMULADA', 'Los resultados de análisis de imagen son ficticios y no tienen valor clínico.', C.sim, C.simBg);
  if (prototype)
    y = drawNotice(doc, y, 'MODELO PROTOTIPO — NO VALIDADO', 'El resultado de IA no tiene validación clínica.', C.proto, C.protoBg);

  const ensureSpace = (needed: number) => {
    if (y > pageHeight - 22 - needed) {
      doc.addPage();
      y = 34;
    }
  };
  const section = (title: string) => {
    ensureSpace(30);
    y = sectionTitle(doc, y + 2, title);
  };

  if (triage) {
    section('Triage');
    y += 3;
    text(doc, C.muted, 8.5);
    let line = `Puntaje ${triage.score.toFixed(1).replace('.', ',')} / 100 · parámetros v${triage.config_version}`;
    if (triage.escalation_rule) line += ` · ALTA por escalamiento: ${RULE_LABELS[triage.escalation_rule] ?? 'regla clínica'}`;
    doc.text(line, MARGIN, y + 2);
    // Barra de puntaje: pista rubor y relleno del color del nivel
    const barY = y + 5;
    doc.setFillColor(...C.blush);
    doc.roundedRect(MARGIN, barY, contentWidth, 2.4, 1.2, 1.2, 'F');
    doc.setFillColor(...(C.level[triage.final_level] ?? C.rose));
    doc.roundedRect(MARGIN, barY, Math.max(2.4, (contentWidth * Math.min(100, triage.score)) / 100), 2.4, 1.2, 1.2, 'F');
    y = barY + 7;
    if (triage.override_by !== null) {
      text(doc, C.ink, 8.5);
      const msg = `Nivel ajustado por el médico (calculado: ${triage.computed_level}). Motivo: ${triage.override_reason ?? ''}`;
      const lines = doc.splitTextToSize(msg, contentWidth);
      doc.text(lines, MARGIN, y + 1);
      y += lines.length * 4 + 3;
    }
    if (triage.breakdown) {
      const b = triage.breakdown as unknown as Record<string, { value: number | boolean; weight: number; points: number }>;
      autoTable(doc, {
        ...tableStyle(y),
        head: [['Factor', 'Valor', 'Peso', 'Aporte']],
        body: Object.keys(FACTOR_LABELS).map((k) => [
          FACTOR_LABELS[k] + (k === 'ai' && simulated ? ' · IA SIMULADA' : k === 'ai' && prototype ? ' · PROTOTIPO' : ''),
          typeof b[k].value === 'boolean' ? (b[k].value ? 'Sí' : 'No') : String(b[k].value),
          String(b[k].weight),
          b[k].points.toFixed(2).replace('.', ','),
        ]),
        columnStyles: { 1: { halign: 'right' }, 2: { halign: 'right' }, 3: { halign: 'right', fontStyle: 'bold' } },
      });
      y = lastY(doc) + 8;
    }
  }

  section('Revisión médica');
  autoTable(doc, {
    ...kvStyle(y + 1),
    body: [
      ['BI-RADS final', String(review.birads_final)],
      ['Hallazgos', review.findings],
      ['Recomendación', RECOMMENDATION_LABELS[review.recommendation]],
      ['Médico', medicoName],
      ['Fecha', fmt(review.created_at)],
    ],
  });
  y = lastY(doc) + 8;

  section('Validación médica de la IA y del triage');
  const validated = images.filter((img) => img.inference);
  autoTable(doc, {
    ...tableStyle(y + 1),
    head: [['Elemento', 'Resultado', 'Validación del médico']],
    body: [
      ...validated.map((img) => [
        `${EXAM_TYPE_LABELS[img.exam_type]}${img.laterality ? ` · ${img.laterality === 'L' ? 'Izquierda' : 'Derecha'}` : ''}`,
        `${img.inference!.detected ? 'Sospecha' : 'Baja probabilidad'} · ${img.inference!.confidence.toFixed(1).replace('.', ',')} %` +
          (img.inference!.is_simulated ? ' · IA SIMULADA' : img.inference!.clinically_validated ? '' : ' · PROTOTIPO'),
        img.validation
          ? AI_VERDICT_LABELS[img.validation.verdict] + (img.validation.comment ? ` — ${img.validation.comment}` : '')
          : 'Sin validar',
      ]),
      [
        'Triage',
        review.triage_level_at_review
          ? `Nivel ${review.triage_level_at_review} · parámetros v${review.triage_config_version_at_review}`
          : '—',
        review.triage_assessment
          ? TRIAGE_ASSESSMENT_LABELS[review.triage_assessment] + (review.triage_comment ? ` — ${review.triage_comment}` : '')
          : 'No registrada',
      ],
    ],
  });
  y = lastY(doc) + 8;

  // Lámina del examen: Derecha a la izquierda e Izquierda a la derecha, como en la orden y en la interfaz
  const withThumb = images.filter((img) => thumbnails[img.id]);
  if (withThumb.length > 0) {
    const cellW = (contentWidth - 8) / 2;
    const imgH = 62;
    const sides: Array<[string, CaseImage[]]> = [
      ['Derecha', withThumb.filter((i) => i.laterality === 'R')],
      ['Izquierda', withThumb.filter((i) => i.laterality === 'L')],
    ];
    const other = withThumb.filter((i) => i.laterality !== 'R' && i.laterality !== 'L');
    if (other.length) sides.push(['Sin lado', other]);
    const rows = Math.max(...sides.map(([, list]) => list.length));
    ensureSpace(imgH + 30);
    y = sectionTitle(doc, y + 2, 'Imágenes del examen') + 3;
    sides.slice(0, 2).forEach(([name], i) => {
      text(doc, C.ink, 9, 'bold');
      doc.text(name, MARGIN + i * (cellW + 8), y + 2);
    });
    y += 5;
    const drawCell = (img: CaseImage, x: number, top: number) => {
      const t = thumbnails[img.id];
      doc.setFillColor(...VIEWER);
      doc.roundedRect(x, top, cellW, imgH, 1.5, 1.5, 'F');
      const scale = Math.min((cellW - 4) / t.width, (imgH - 4) / t.height);
      const w = t.width * scale;
      const h = t.height * scale;
      const ix = x + (cellW - w) / 2;
      const iy = top + (imgH - h) / 2;
      doc.addImage(t.data, 'JPEG', ix, iy, w, h);
      for (const d of img.inference?.detections ?? []) {
        doc.setDrawColor(...BOX);
        doc.setLineWidth(0.5);
        doc.rect(ix + d.x * w, iy + d.y * h, d.width * w, d.height * h, 'S');
      }
      const inf = img.inference;
      text(doc, C.ink, 8, 'bold');
      doc.text(`${EXAM_TYPE_LABELS[img.exam_type]} · ${sideName(img.laterality)}`, x, top + imgH + 4.5);
      text(doc, C.muted, 7.5);
      doc.text(
        inf
          ? `${inf.detected ? 'Sospecha' : 'Baja probabilidad'} · ${inf.confidence.toFixed(1).replace('.', ',')} %` +
              (inf.detections?.length ? ` · ${inf.detections.length} ${inf.detections.length === 1 ? 'marca' : 'marcas'}` : '') +
              (inf.is_simulated ? ' · IA SIMULADA' : inf.clinically_validated ? '' : ' · PROTOTIPO')
          : 'Sin resultado de IA',
        x,
        top + imgH + 8.5,
        { maxWidth: cellW },
      );
    };
    for (let r = 0; r < rows; r++) {
      ensureSpace(imgH + 14);
      sides.slice(0, 2).forEach(([, list], i) => {
        if (list[r]) drawCell(list[r], MARGIN + i * (cellW + 8), y);
      });
      y += imgH + 14;
    }
    if (other.length) {
      for (let r = 0; r < other.length; r += 2) {
        ensureSpace(imgH + 14);
        other.slice(r, r + 2).forEach((img, i) => drawCell(img, MARGIN + i * (cellW + 8), y));
        y += imgH + 14;
      }
    }
    if (withThumb.some((i) => i.inference?.detections?.length)) {
      text(doc, C.muted, 7);
      doc.text('Los recuadros marcan las zonas señaladas por la IA. El médico revisó cada imagen.', MARGIN, y + 1);
      y += 6;
    }
  }

  const signature = metadata.MedicalSignature as MedicalSignatureBlock | undefined;
  if (signature) {
    ensureSpace(52);
    y = sectionTitle(doc, y + 2, 'Firma del médico');
    // Bloque de firma: borde rosa, como la acción principal del caso
    const boxY = y + 2;
    doc.setDrawColor(...C.rose);
    doc.setLineWidth(0.4);
    doc.roundedRect(MARGIN, boxY, contentWidth, 34, 2, 2, 'S');
    text(doc, C.ink, 8.5);
    doc.text(
      doc.splitTextToSize(
        'El médico declara su conformidad con el contenido de este reporte, incluida la validación del resultado de IA.',
        contentWidth - 10,
      ),
      MARGIN + 5,
      boxY + 7,
    );
    text(doc, C.ink, 12, 'extrabold');
    doc.text(signature.SignedBy, MARGIN + 5, boxY + 17);
    text(doc, C.muted, 8);
    doc.text(`Firmado el ${fmt(signature.SignedAt)}`, MARGIN + 5, boxY + 22);
    text(doc, C.muted, 7.5);
    doc.text('Código de verificación', pageWidth - MARGIN - 5, boxY + 13, { align: 'right' });
    text(doc, C.rose, 12, 'extrabold');
    doc.text(signature.VerificationCode, pageWidth - MARGIN - 5, boxY + 19, { align: 'right' });
    text(doc, C.muted, 6.5);
    doc.text(`SHA-256 del contenido firmado: ${signature.ContentSHA256}`, MARGIN + 5, boxY + 30);
    y = boxY + 34 + 8;
  }

  section('Metadatos del estudio');
  autoTable(doc, {
    ...kvStyle(y + 1, 62),
    styles: { ...kvStyle(y + 1).styles, fontSize: 7.5, cellPadding: { top: 1.5, bottom: 1.5, left: 2.5, right: 2.5 } },
    head: [['Atributo', 'Valor']],
    body: Object.entries(metadata)
      .filter(([k]) => k !== 'MedicalSignature')
      .map(([k, v]) => [k, Array.isArray(v) ? v.join(', ') : v === null ? '—' : String(v)]),
  });

  drawFooter(doc, `${caseData.code} · Generado el ${generatedAt.toLocaleString('es-CL')} por ${medicoName}`, {
    assets,
    kind: 'Reporte de caso',
    detail: caseData.code,
  });
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

  const assets = await loadPdfAssets();
  // Miniaturas de las imágenes (se descifran en el servidor y se reducen aquí); si una falla, se omite
  const list = images.data ?? [];
  const thumbs = await Promise.all(
    list.map(async (img) => {
      const blob = await apiClient.fetchImageBlob(caseData.id, img.id);
      return [img.id, blob ? await makeThumbnail(blob) : null] as const;
    }),
  );
  const thumbnails: Record<number, Thumbnail> = {};
  for (const [id, t] of thumbs) if (t) thumbnails[id] = t;
  const doc = buildCaseReport({
    thumbnails,
    assets,
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
