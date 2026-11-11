import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import type { AIVerdict, CaseStatus, DashboardMetrics, ModelPerformanceReport, TriageAssessment } from '../types';
import { AI_VERDICT_LABELS, CASE_STATUS_LABELS, TRIAGE_ASSESSMENT_LABELS } from '../types';
import {
  C,
  MARGIN,
  type RGB,
  applyAssets,
  drawBrandHeader,
  drawFooter,
  drawLevelStamp,
  drawNotice,
  lastY,
  loadPdfAssets,
  rule,
  sectionTitle,
  tableStyle,
  text,
} from './pdfTheme';

const LEVELS = ['ALTA', 'MEDIA', 'BAJA'] as const;
type Level = (typeof LEVELS)[number];
type Tone = 'ok' | 'warn' | 'alert' | 'info';

const TONE: Record<Tone, { color: RGB; label: string }> = {
  ok: { color: C.level.BAJA, label: 'BIEN' },
  warn: { color: C.level.MEDIA, label: 'ATENCIÓN' },
  alert: { color: C.level.ALTA, label: 'ALERTA' },
  info: { color: [32, 80, 182], label: 'NOTA' },
};

const dec = (n: number, d = 1) => n.toFixed(d).replace('.', ',');
const pct = (v: number | null, d = 1) => (v === null ? '—' : `${dec(v * 100, d)} %`);
const int = (n: number) => n.toLocaleString('es-CL');
const okText = (ok: boolean | null) => (ok === null ? '—' : ok ? 'Cumple' : 'No cumple');

function seconds(s: number | null): string {
  if (s === null) return '—';
  if (s < 60) return `${s.toFixed(0)} s`;
  if (s < 3600) return `${dec(s / 60)} min`;
  return `${dec(s / 3600)} h`;
}

function hours(h: number | null): string {
  if (h === null) return '—';
  return h < 48 ? `${dec(h)} h` : `${dec(h / 24)} días`;
}

function day(iso: string | null): string {
  return iso ? new Date(iso).toLocaleDateString('es-CL') : '';
}

// --- Lectura de los datos: el relato se arma con reglas simples y transparentes -------------------

interface Finding {
  tone: Tone;
  title: string;
  text: string;
}

interface Story {
  summary: string;
  findings: Finding[];
  recommendations: string[];
  volume: string;
  priority: string;
  quality: string;
  model: string;
  platform: string;
}

function tell(data: DashboardMetrics, model: ModelPerformanceReport | null): Story {
  const total = data.total_cases;
  const closed = data.cases_by_status.CERRADO ?? 0;
  const pending = total - closed;
  const lv = (l: Level) => data.cases_by_level[l] ?? 0;
  const share = (l: Level) => (total ? lv(l) / total : 0);
  const rt = data.avg_triage_to_review_hours_by_level;
  const findings: Finding[] = [];
  const recs: string[] = [];

  // Volumen y tendencia (la última semana puede estar en curso: se compara sin ella)
  const weeks = data.cases_per_week;
  const full = weeks.slice(0, -1);
  let trend = '';
  if (full.length >= 6) {
    const recent = full.slice(-3).reduce((a, w) => a + w.cases, 0) / 3;
    const before = full.slice(-6, -3).reduce((a, w) => a + w.cases, 0) / 3;
    if (before > 0) {
      const change = (recent - before) / before;
      trend =
        Math.abs(change) < 0.1
          ? 'La demanda se mantuvo estable en las últimas semanas.'
          : change > 0
            ? `La demanda viene en alza: las últimas tres semanas completas promedian ${dec(recent)} casos, ${pct(change, 0)} más que las tres anteriores.`
            : `La demanda bajó: las últimas tres semanas completas promedian ${dec(recent)} casos, ${pct(-change, 0)} menos que las tres anteriores.`;
    }
  }
  const peak = weeks.reduce((m, w) => (w.cases > (m?.cases ?? -1) ? w : m), null as (typeof weeks)[number] | null);
  const volume =
    total === 0
      ? 'No se registraron casos en el período.'
      : `Se registraron ${int(total)} casos en ${weeks.length} semanas` +
        (peak ? `, con un máximo de ${peak.cases} en la semana del ${day(peak.week_start).slice(0, 5)}. ` : '. ') +
        trend;

  // Priorización: ¿los ALTA se revisan antes que los MEDIA y estos antes que los BAJA?
  const ordered = rt.ALTA !== null && rt.MEDIA !== null && rt.BAJA !== null && rt.ALTA < rt.MEDIA && rt.MEDIA < rt.BAJA;
  const faster = rt.ALTA && rt.BAJA ? rt.BAJA / rt.ALTA : null;
  let priority = `${pct(share('ALTA'), 0)} de los casos quedó en ALTA, ${pct(share('MEDIA'), 0)} en MEDIA y ${pct(share('BAJA'), 0)} en BAJA. `;
  if (ordered && faster)
    priority += `La cola funciona como se espera: los casos ALTA llegaron a revisión en ${hours(rt.ALTA)} en promedio, ${dec(faster)} veces más rápido que los BAJA (${hours(rt.BAJA)}).`;
  else if (rt.ALTA !== null)
    priority += `Los tiempos de revisión no siguen el orden de urgencia (ALTA ${hours(rt.ALTA)}, MEDIA ${hours(rt.MEDIA)}, BAJA ${hours(rt.BAJA)}): conviene revisar cómo se está usando la cola.`;
  else priority += 'Aún no hay revisiones médicas para medir los tiempos por nivel.';

  if (ordered && faster)
    findings.push({
      tone: 'ok',
      title: 'La priorización acorta la espera de los casos urgentes',
      text: `ALTA se revisa en ${hours(rt.ALTA)}; BAJA, en ${hours(rt.BAJA)}.`,
    });
  else if (rt.ALTA !== null)
    findings.push({ tone: 'warn', title: 'Los tiempos no respetan el nivel', text: 'Revisar el uso de la cola de triage.' });

  if (data.alta_pending_over_hours > 0) {
    findings.push({
      tone: 'alert',
      title: `${data.alta_pending_over_hours} ${data.alta_pending_over_hours === 1 ? 'caso ALTA espera' : 'casos ALTA esperan'} más de ${data.alta_pending_threshold_hours} h`,
      text: 'Son los casos que más riesgo corren por la demora.',
    });
    recs.push(
      `Revisar hoy los ${data.alta_pending_over_hours} casos ALTA con más de ${data.alta_pending_threshold_hours} h de espera y, si se repite, asignar un médico responsable de la cola ALTA por turno.`,
    );
  } else if (lv('ALTA') > 0) {
    findings.push({
      tone: 'ok',
      title: `Ningún caso ALTA espera más de ${data.alta_pending_threshold_hours} h`,
      text: 'La meta de cero casos ALTA atrasados se cumple.',
    });
  }

  if (data.avg_creation_to_triage_seconds !== null) {
    const ok = data.avg_creation_to_triage_seconds <= data.kpi_creation_to_triage_target_seconds;
    findings.push({
      tone: ok ? 'ok' : 'warn',
      title: `El triage se calcula en ${seconds(data.avg_creation_to_triage_seconds)}`,
      text: ok ? 'Muy por debajo de la meta de 5 minutos desde la creación del caso.' : 'Supera la meta de 5 minutos.',
    });
    if (!ok) recs.push('Revisar la carga de imágenes y la disponibilidad del modelo: el triage tarda más de 5 minutos.');
  }

  // Calidad: ajustes, concordancia IA–médico y aprobación del triage
  const fn = data.ai_validations_by_verdict.FALSO_NEGATIVO ?? 0;
  const fp = data.ai_validations_by_verdict.FALSO_POSITIVO ?? 0;
  const under = data.triage_assessments_by_value.SUBESTIMADO ?? 0;
  const over = data.triage_assessments_by_value.SOBREESTIMADO ?? 0;
  let quality = '';
  if (data.override_ratio !== null)
    quality += `Los médicos ajustaron el nivel en ${pct(data.override_ratio)} de los cálculos (${data.triage_overrides} de ${data.triage_total}). `;
  if (data.triage_agreement_rate !== null)
    quality += `Al cerrar, aprobaron el triage en ${pct(data.triage_agreement_rate, 0)} de las revisiones; ${under} ${under === 1 ? 'caso se consideró subestimado' : 'casos se consideraron subestimados'} y ${over} sobreestimados. `;
  if (data.ai_agreement_rate !== null)
    quality += `La IA coincidió con el médico en ${pct(data.ai_agreement_rate, 0)} de ${data.ai_validations_total} imágenes evaluadas, con ${fp} falsos positivos y ${fn} falsos negativos.`;
  if (!quality) quality = 'Aún no hay revisiones médicas registradas en el período.';

  if (data.override_ratio !== null) {
    const r = data.override_ratio;
    findings.push({
      tone: r <= 0.1 ? 'ok' : r <= 0.2 ? 'warn' : 'alert',
      title: `Los médicos ajustan ${pct(r, 0)} de los niveles`,
      text: r <= 0.1 ? 'Los parámetros del triage calzan con el criterio clínico.' : 'Una proporción alta sugiere revisar los parámetros.',
    });
    if (r > 0.1) recs.push('Revisar con el equipo médico los parámetros del triage: la proporción de ajustes supera el 10 %.');
  }
  if (under > 0 && data.triage_assessments_total > 0 && under / data.triage_assessments_total > 0.05)
    recs.push(
      `Analizar los ${under} casos marcados como subestimados: son los que el triage dejó con menos prioridad de la necesaria.`,
    );
  if (fn > 0)
    findings.push({
      tone: 'warn',
      title: `${fn} ${fn === 1 ? 'falso negativo' : 'falsos negativos'} de la IA`,
      text: 'Hallazgos que el médico vio y la IA no: el error más importante a vigilar.',
    });

  // Modelo
  const sim = model?.versions.some((v) => v.is_simulated) || data.ai_validations_simulated > 0;
  const real = model?.versions.filter((v) => !v.is_simulated) ?? [];
  let modelText = '';
  if (real.length > 0) {
    const v = real[real.length - 1];
    modelText = `El modelo ${v.model_version} tiene ${v.evaluable} imágenes evaluables, con exactitud ${pct(v.accuracy, 0)}, sensibilidad ${pct(v.sensitivity, 0)} y especificidad ${pct(v.specificity, 0)}. `;
    modelText +=
      v.meets_k5 === null
        ? `Aún no alcanza la muestra mínima de ${model!.min_sample} para evaluar la meta K5.`
        : v.meets_k5
          ? 'Cumple la meta K5.'
          : 'No cumple la meta K5.';
  }
  if (sim) {
    modelText +=
      (modelText ? ' ' : '') +
      'Los resultados de IA de este período son SIMULADOS: sirven para probar el flujo y el cálculo de las métricas, pero no miden un modelo real ni tienen valor clínico.';
    findings.push({
      tone: 'info',
      title: 'Las métricas de IA provienen de la IA simulada',
      text: 'Miden el flujo, no el desempeño clínico de un modelo.',
    });
    recs.push('Conectar el modelo real y acumular validaciones médicas antes de evaluar la meta K5 de exactitud.');
  }
  if (!modelText) modelText = 'No hay validaciones del modelo en el período.';

  // Plataforma
  const p95 = data.api_p95_ms;
  const platform =
    p95 === null
      ? 'No hay mediciones de rendimiento de la plataforma en el período.'
      : `El 95 % de las solicitudes respondió en menos de ${int(Math.round(p95))} ms (meta: menos de 3 s), sobre ${int(data.api_requests)} solicitudes medidas, con ${data.server_errors} errores del servidor.`;
  if (p95 !== null && p95 >= data.kpi_api_p95_target_ms)
    recs.push('Revisar el rendimiento del servidor: el tiempo de respuesta p95 supera los 3 segundos.');

  // Resumen ejecutivo
  const summary =
    total === 0
      ? 'En el período no se registraron casos, por lo que no hay indicadores que informar.'
      : `En el período se registraron ${int(total)} casos: ${lv('ALTA')} ALTA, ${lv('MEDIA')} MEDIA y ${lv('BAJA')} BAJA. ` +
        `${int(closed)} ya tienen revisión médica y ${int(pending)} siguen pendientes. ` +
        (ordered && faster
          ? `La priorización cumple su propósito: los casos urgentes se revisaron ${dec(faster)} veces más rápido que los de baja prioridad`
          : 'Los tiempos de revisión todavía no muestran el efecto de la priorización') +
        (data.alta_pending_over_hours > 0
          ? `, aunque ${data.alta_pending_over_hours} ${data.alta_pending_over_hours === 1 ? 'caso ALTA sigue' : 'casos ALTA siguen'} esperando más de ${data.alta_pending_threshold_hours} h. `
          : '. ') +
        (data.triage_agreement_rate !== null
          ? `Los médicos aprobaron el nivel asignado en ${pct(data.triage_agreement_rate, 0)} de las revisiones.`
          : '');

  if (recs.length === 0) recs.push('Mantener el monitoreo semanal: todos los indicadores están dentro de sus metas.');
  return { summary, findings, recommendations: recs, volume, priority, quality, model: modelText, platform };
}

// --- Dibujo ---------------------------------------------------------------------------------------

function paragraph(doc: jsPDF, y: number, body: string, width: number, size = 9.5, color: RGB = C.ink): number {
  text(doc, color, size);
  const lines = doc.splitTextToSize(body, width) as string[];
  const lh = size * 0.3528 * 1.45;
  doc.text(lines, MARGIN, y, { lineHeightFactor: 1.45 });
  return y + lines.length * lh;
}

function statTile(doc: jsPDF, x: number, y: number, w: number, value: string, label: string, caption: string) {
  doc.setDrawColor(...C.rule);
  doc.setLineWidth(0.3);
  doc.roundedRect(x, y, w, 26, 2, 2, 'S');
  text(doc, C.muted, 7.5, 'bold');
  doc.text(label, x + 4, y + 6);
  text(doc, C.ink, 18, 'extrabold');
  doc.text(value, x + 4, y + 15.5);
  text(doc, C.muted, 7);
  doc.text(doc.splitTextToSize(caption, w - 8) as string[], x + 4, y + 20.5);
}

/** Columnas de una sola serie: un tono, extremos redondeados, eje recesivo y rótulos selectivos. */
function columnChart(doc: jsPDF, y: number, points: Array<{ label: string; value: number }>, height = 46): number {
  const width = doc.internal.pageSize.getWidth() - 2 * MARGIN;
  const plotX = MARGIN + 8;
  const plotW = width - 8;
  const max = Math.max(1, ...points.map((p) => p.value));
  const niceMax = Math.ceil(max / 5) * 5;
  const base = y + height;
  // Grilla recesiva: base y dos referencias
  text(doc, C.muted, 6.5);
  for (const t of [0, niceMax / 2, niceMax]) {
    const gy = base - (t / niceMax) * height;
    doc.setDrawColor(...(t === 0 ? C.muted : C.rule));
    doc.setLineWidth(t === 0 ? 0.3 : 0.15);
    doc.line(plotX, gy, plotX + plotW, gy);
    doc.text(String(Math.round(t)), plotX - 2, gy + 1, { align: 'right' });
  }
  const slot = plotW / points.length;
  const barW = Math.min(9, slot * 0.6);
  const peakIndex = points.reduce((m, p, i) => (p.value > points[m].value ? i : m), 0);
  points.forEach((p, i) => {
    const h = (p.value / niceMax) * height;
    const x = plotX + i * slot + (slot - barW) / 2;
    if (h > 0) {
      doc.setFillColor(...C.rose);
      doc.roundedRect(x, base - h, barW, h, 0.8, 0.8, 'F');
      doc.rect(x, base - Math.min(h, 0.8), barW, Math.min(h, 0.8), 'F'); // base recta
    }
    text(doc, C.muted, 6.5);
    doc.text(p.label, x + barW / 2, base + 4, { align: 'center' });
    // Rótulos selectivos: máximo y última semana
    if (i === peakIndex || i === points.length - 1) {
      text(doc, C.ink, 7.5, 'bold');
      doc.text(String(p.value), x + barW / 2, base - h - 1.5, { align: 'center' });
    }
  });
  return base + 8;
}

/** Barras horizontales por nivel, rotuladas con el timbre del nivel (el color nunca va solo). */
function levelBars(
  doc: jsPDF,
  x: number,
  y: number,
  w: number,
  title: string,
  values: Record<Level, number | null>,
  format: (v: number | null) => string,
): number {
  text(doc, C.ink, 8.5, 'bold');
  doc.text(title, x, y);
  let yy = y + 8;
  const max = Math.max(1, ...LEVELS.map((l) => values[l] ?? 0));
  const labelW = 22;
  const valueW = 18;
  const barMax = w - labelW - valueW;
  for (const l of LEVELS) {
    drawLevelStamp(doc, x, yy, l);
    const v = values[l];
    doc.setFillColor(...C.blush);
    doc.roundedRect(x + labelW, yy - 3, barMax, 3.6, 0.8, 0.8, 'F');
    if (v !== null && v > 0) {
      doc.setFillColor(...C.rose);
      doc.roundedRect(x + labelW, yy - 3, Math.max(1.6, (v / max) * barMax), 3.6, 0.8, 0.8, 'F');
    }
    text(doc, C.ink, 8.5, 'bold');
    doc.text(format(v), x + w, yy, { align: 'right' });
    yy += 8;
  }
  return yy;
}

interface ManagementReportInput {
  data: DashboardMetrics;
  model: ModelPerformanceReport | null;
  generatedBy: string;
  assets: Awaited<ReturnType<typeof loadPdfAssets>>;
}

/** Informe de gestión con relato: resumen, hallazgos, gráficos, lectura por sección y recomendaciones. */
export function buildManagementReport({ data, model, generatedBy, assets }: ManagementReportInput): jsPDF {
  const doc = new jsPDF();
  applyAssets(doc, assets);
  const pageW = doc.internal.pageSize.getWidth();
  const pageH = doc.internal.pageSize.getHeight();
  const contentW = pageW - 2 * MARGIN;
  const table = tableStyle(0);
  const generatedAt = new Date();
  const story = tell(data, model);
  const period =
    data.date_from || data.date_to
      ? `${day(data.date_from) || 'inicio'} – ${day(data.date_to) || 'hoy'}`
      : 'todos los registros';

  let y = drawBrandHeader(doc, assets, 'Informe de gestión', `Generado el ${generatedAt.toLocaleString('es-CL')}`);
  const ensure = (needed: number) => {
    if (y + needed > pageH - 22) {
      doc.addPage();
      y = 40;
    }
  };
  const section = (n: number, title: string, lead: string) => {
    ensure(40);
    y = sectionTitle(doc, y, `${n}. ${title}`) + 3;
    y = paragraph(doc, y, lead, contentW, 9, C.muted) + 3;
  };

  // Portada: titular, período y resumen
  text(doc, C.ink, 24, 'extrabold');
  doc.text('Informe de gestión', MARGIN, y + 7);
  text(doc, C.muted, 9);
  doc.text(`Período: ${period}  ·  Métricas agregadas, sin datos identificables de pacientes`, MARGIN, y + 13.5);
  y += 21;
  if (data.ai_validations_simulated > 0 || model?.versions.some((v) => v.is_simulated))
    y = drawNotice(doc, y, 'IA SIMULADA', 'Incluye resultados de IA simulada: no son resultados clínicos.', C.sim, C.simBg);

  y = sectionTitle(doc, y + 1, 'Resumen ejecutivo') + 3;
  y = paragraph(doc, y, story.summary, contentW, 10) + 5;

  // Cifras principales
  const tileW = (contentW - 3 * 4) / 4;
  const rt = data.avg_triage_to_review_hours_by_level;
  statTile(doc, MARGIN, y, tileW, int(data.total_cases), 'CASOS', `${int(data.cases_by_status.CERRADO ?? 0)} con revisión médica`);
  statTile(
    doc,
    MARGIN + (tileW + 4),
    y,
    tileW,
    int(data.cases_by_level.ALTA ?? 0),
    'CASOS ALTA',
    `${pct(data.total_cases ? (data.cases_by_level.ALTA ?? 0) / data.total_cases : 0, 0)} del total`,
  );
  statTile(doc, MARGIN + 2 * (tileW + 4), y, tileW, hours(rt.ALTA), 'ALTA A REVISIÓN', 'promedio desde el triage');
  statTile(
    doc,
    MARGIN + 3 * (tileW + 4),
    y,
    tileW,
    pct(data.triage_agreement_rate, 0),
    'TRIAGE APROBADO',
    'por el médico al cerrar el caso',
  );
  y += 34;

  // Hallazgos clave: etiqueta de estado (texto + color), nunca solo color
  y = sectionTitle(doc, y, 'Hallazgos clave') + 4;
  for (const f of story.findings) {
    ensure(12);
    const tone = TONE[f.tone];
    text(doc, tone.color, 7, 'extrabold');
    doc.setDrawColor(...tone.color);
    doc.setLineWidth(0.3);
    const tagW = doc.getTextWidth(tone.label) + 4;
    doc.roundedRect(MARGIN, y - 3.4, tagW, 4.8, 1, 1, 'S');
    doc.text(tone.label, MARGIN + 2, y);
    text(doc, C.ink, 9.5, 'bold');
    doc.text(f.title, MARGIN + 24, y);
    y += 4.2;
    text(doc, C.muted, 8.5);
    doc.text(f.text, MARGIN + 24, y);
    y += 7;
  }

  // 1. Volumen
  doc.addPage();
  y = 40;
  section(1, 'Volumen de casos', story.volume);
  text(doc, C.ink, 8.5, 'bold');
  doc.text('Casos creados por semana', MARGIN, y + 2);
  text(doc, C.muted, 7);
  doc.text('(la última columna puede ser una semana en curso)', MARGIN + 41, y + 2);
  y = columnChart(
    doc,
    y + 8,
    data.cases_per_week.slice(-12).map((w) => ({ label: day(w.week_start).slice(0, 5), value: w.cases })),
  );
  y += 4;

  // 2. Priorización
  section(2, 'Priorización y tiempos de revisión', story.priority);
  const half = (contentW - 10) / 2;
  const counts = Object.fromEntries(LEVELS.map((l) => [l, data.cases_by_level[l] ?? 0])) as Record<Level, number>;
  const end1 = levelBars(doc, MARGIN, y + 2, half, 'Casos por nivel vigente', counts, (v) => int(v ?? 0));
  const end2 = levelBars(doc, MARGIN + half + 10, y + 2, half, 'Promedio del triage a la revisión', rt, (v) => hours(v));
  y = Math.max(end1, end2) + 1;
  text(doc, C.muted, 8);
  doc.text(
    'Estado de los casos: ' +
      (Object.keys(data.cases_by_status) as CaseStatus[])
        .map((s) => `${CASE_STATUS_LABELS[s]} ${data.cases_by_status[s]}`)
        .join('  ·  '),
    MARGIN,
    y,
  );
  y += 10;

  // 3. Calidad
  section(3, 'Calidad de las decisiones', story.quality);
  autoTable(doc, {
    ...table,
    startY: y,
    head: [['Indicador', 'Valor', 'Desglose']],
    body: [
      ['Ajustes médicos del nivel', pct(data.override_ratio), `${data.triage_overrides} de ${data.triage_total} cálculos`],
      [
        `Concordancia IA - médico (${data.ai_validations_total})`,
        pct(data.ai_agreement_rate),
        (Object.keys(AI_VERDICT_LABELS) as AIVerdict[])
          .map((v) => `${data.ai_validations_by_verdict[v] ?? 0} ${AI_VERDICT_LABELS[v].toLowerCase()}`)
          .join(' · '),
      ],
      [
        `Aprobación del triage (${data.triage_assessments_total})`,
        pct(data.triage_agreement_rate),
        (Object.keys(TRIAGE_ASSESSMENT_LABELS) as TriageAssessment[])
          .map((v) => `${data.triage_assessments_by_value[v] ?? 0} ${TRIAGE_ASSESSMENT_LABELS[v].toLowerCase()}`)
          .join(' · '),
      ],
    ],
    columnStyles: { 1: { halign: 'right', fontStyle: 'bold' }, 2: { cellWidth: 82, textColor: C.muted } },
  });
  y = lastY(doc) + 10;

  // 4. Modelo
  section(4, 'Desempeño del modelo de IA', story.model);
  if (model && model.versions.length > 0) {
    autoTable(doc, {
      ...table,
      startY: y,
      head: [['Modelo', 'Evaluables', 'Exactitud', 'Sensibilidad', 'Especificidad', `Meta K5 (${pct(model.k5_target, 0)})`]],
      body: model.versions.map((v) => [
        `${v.model_version}${v.is_simulated ? ' · IA SIMULADA' : ''}`,
        String(v.evaluable),
        pct(v.accuracy),
        pct(v.sensitivity),
        pct(v.specificity),
        v.is_simulated ? 'No aplica' : okText(v.meets_k5),
      ]),
    });
    y = lastY(doc) + 10;
  }

  // 5. Plataforma
  section(5, 'Rendimiento de la plataforma', story.platform);
  autoTable(doc, {
    ...table,
    startY: y,
    head: [['Indicador', 'Valor', 'Meta', 'Estado']],
    body: [
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
        `Respuesta de la API, p95 (${int(data.api_requests)} solicitudes)`,
        data.api_p95_ms === null ? '—' : `${data.api_p95_ms.toFixed(0)} ms`,
        'menos de 3 s',
        okText(data.api_p95_ms === null ? null : data.api_p95_ms < data.kpi_api_p95_target_ms),
      ],
      [
        `Casos ALTA pendientes más de ${data.alta_pending_threshold_hours} h`,
        String(data.alta_pending_over_hours),
        '0',
        okText(data.alta_pending_over_hours === 0),
      ],
      ['Errores del servidor (5xx)', `${data.server_errors} (${pct(data.server_error_rate)})`, '—', '—'],
    ],
    columnStyles: { 1: { halign: 'right', fontStyle: 'bold' }, 2: { textColor: C.muted } },
    didParseCell: (cell) => {
      if (cell.section === 'body' && cell.column.index === 3) {
        const raw = String(cell.cell.raw);
        if (raw === 'Cumple') cell.cell.styles.textColor = C.level.BAJA;
        if (raw === 'No cumple') cell.cell.styles.textColor = C.level.ALTA;
      }
    },
  });
  y = lastY(doc) + 10;

  // Recomendaciones
  ensure(20 + story.recommendations.length * 9);
  y = sectionTitle(doc, y, 'Recomendaciones') + 4;
  story.recommendations.forEach((r, i) => {
    ensure(10);
    text(doc, C.rose, 9.5, 'extrabold');
    doc.text(`${i + 1}`, MARGIN, y);
    text(doc, C.ink, 9.5);
    const lines = doc.splitTextToSize(r, contentW - 8) as string[];
    doc.text(lines, MARGIN + 7, y, { lineHeightFactor: 1.4 });
    y += lines.length * 4.7 + 2.5;
  });

  // Notas metodológicas
  ensure(30);
  y += 4;
  rule(doc, y);
  y += 5;
  text(doc, C.ink, 8, 'bold');
  doc.text('Cómo leer este informe', MARGIN, y);
  y += 4;
  paragraph(
    doc,
    y,
    'El nivel vigente es el del último cálculo, incluidos los ajustes médicos. Los tiempos de revisión se miden desde el ' +
      'primer triage hasta el registro de la revisión. La concordancia IA - médico usa la validación médica de cada imagen ' +
      'como referencia; las imágenes no evaluables no cuentan. El relato y las recomendaciones se generan con reglas fijas ' +
      'a partir de estas cifras y no reemplazan el análisis del equipo.',
    contentW,
    7.5,
    C.muted,
  );

  drawFooter(doc, `Informe de gestión · ${period} · Generado el ${generatedAt.toLocaleString('es-CL')} por ${generatedBy}`, {
    assets,
    kind: 'Informe de gestión',
    detail: `Período: ${period}`,
  });
  return doc;
}
