import type jsPDF from 'jspdf';
import type { UserOptions } from 'jspdf-autotable';
import regularUrl from '../assets/fonts/AtkinsonHyperlegibleNext-Regular.ttf?url';
import boldUrl from '../assets/fonts/AtkinsonHyperlegibleNext-Bold.ttf?url';
import extraBoldUrl from '../assets/fonts/AtkinsonHyperlegibleNext-ExtraBold.ttf?url';
import logoUrl from '../assets/aurora-simbolo-claro.png';

/** Paleta del tema claro de la interfaz (DESIGN.md), en RGB para jsPDF. */
export type RGB = [number, number, number];
export const C = {
  ink: [40, 21, 32] as RGB, // Tinta Ciruela (foreground)
  muted: [107, 76, 95] as RGB, // Ciruela Tenue (muted-foreground)
  rose: [191, 24, 99] as RGB, // Rosa Clínico (primary)
  blush: [253, 242, 247] as RGB, // Rubor (muted)
  rule: [244, 210, 224] as RGB, // Regla Rubor (border)
  sim: [140, 62, 13] as RGB, // Ocre Simulado (texto)
  simBg: [254, 243, 200] as RGB, // Ocre Simulado (fondo)
  proto: [134, 25, 143] as RGB, // Modelo prototipo
  protoBg: [250, 232, 255] as RGB,
  level: { ALTA: [204, 42, 30], MEDIA: [170, 79, 9], BAJA: [19, 118, 56] } as Record<string, RGB>,
};

export const FONT = 'Atkinson';
export const MARGIN = 18;

interface PdfAssets {
  fonts: Array<{ file: string; style: string; data: string }>;
  logo: string;
}

let assetsPromise: Promise<PdfAssets> | null = null;

async function toBase64(url: string): Promise<string> {
  const buf = await (await fetch(url)).arrayBuffer();
  let binary = '';
  const bytes = new Uint8Array(buf);
  for (let i = 0; i < bytes.length; i += 0x8000) binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(binary);
}

/** Carga (una vez) la tipografía de la interfaz y el símbolo de la marca. */
export function loadPdfAssets(): Promise<PdfAssets> {
  assetsPromise ??= (async () => {
    const [regular, bold, extra, logo] = await Promise.all([
      toBase64(regularUrl),
      toBase64(boldUrl),
      toBase64(extraBoldUrl),
      toBase64(logoUrl),
    ]);
    return {
      fonts: [
        { file: 'Atkinson-Regular.ttf', style: 'normal', data: regular },
        { file: 'Atkinson-Bold.ttf', style: 'bold', data: bold },
        { file: 'Atkinson-ExtraBold.ttf', style: 'extrabold', data: extra },
      ],
      logo: `data:image/png;base64,${logo}`,
    };
  })().catch((e) => {
    assetsPromise = null;
    throw e;
  });
  return assetsPromise;
}

export function applyAssets(doc: jsPDF, assets: PdfAssets): void {
  for (const f of assets.fonts) {
    doc.addFileToVFS(f.file, f.data);
    doc.addFont(f.file, FONT, f.style);
  }
  doc.setFont(FONT, 'normal');
}

export function text(doc: jsPDF, color: RGB, size: number, style: 'normal' | 'bold' | 'extrabold' = 'normal'): void {
  doc.setFont(FONT, style);
  doc.setFontSize(size);
  doc.setTextColor(...color);
}

export function rule(doc: jsPDF, y: number, color: RGB = C.rule, width = 0.3): void {
  const w = doc.internal.pageSize.getWidth();
  doc.setDrawColor(...color);
  doc.setLineWidth(width);
  doc.line(MARGIN, y, w - MARGIN, y);
}

/** Encabezado como la barra de la interfaz: símbolo + «Aurora Care», tipo de documento y regla fina. */
export function drawBrandHeader(doc: jsPDF, assets: PdfAssets, kind: string, detail?: string): number {
  const w = doc.internal.pageSize.getWidth();
  doc.addImage(assets.logo, 'PNG', MARGIN, 11, 14, 10.5);
  text(doc, C.ink, 12, 'extrabold');
  doc.text('Aurora Care', MARGIN + 17, 16.5);
  text(doc, C.muted, 8);
  doc.text('Triage de cáncer de mama', MARGIN + 17, 20.5);
  text(doc, C.rose, 9, 'bold');
  doc.text(kind.toUpperCase(), w - MARGIN, 16.5, { align: 'right', charSpace: 0.3 });
  if (detail) {
    text(doc, C.muted, 8);
    doc.text(detail, w - MARGIN, 20.5, { align: 'right' });
  }
  rule(doc, 26);
  return 34;
}

/** Aviso tipo badge (IA SIMULADA / PROTOTIPO): fondo suave, borde y texto del color semántico. */
export function drawNotice(doc: jsPDF, y: number, label: string, message: string, fg: RGB, bg: RGB): number {
  const w = doc.internal.pageSize.getWidth();
  doc.setFillColor(...bg);
  doc.setDrawColor(...fg);
  doc.setLineWidth(0.3);
  doc.roundedRect(MARGIN, y, w - 2 * MARGIN, 10, 1.5, 1.5, 'FD');
  text(doc, fg, 8, 'extrabold');
  doc.text(label, MARGIN + 4, y + 6.4, { charSpace: 0.25 });
  const lw = doc.getTextWidth(label) + label.length * 0.25;
  text(doc, fg, 8);
  doc.text(message, MARGIN + 4 + lw + 3, y + 6.4);
  return y + 15;
}

/** Timbre de nivel: anillo cuyo grosor sube con la urgencia, más el nombre del nivel (como en la interfaz). */
export function drawLevelStamp(doc: jsPDF, x: number, y: number, level: string, size: 'md' | 'lg' = 'md'): number {
  const color = C.level[level] ?? C.muted;
  const r = size === 'lg' ? 2.6 : 1.9;
  const width = { ALTA: 0.9, MEDIA: 0.65, BAJA: 0.4 }[level] ?? 0.4;
  doc.setDrawColor(...color);
  doc.setLineWidth(width);
  doc.circle(x + r, y - r * 0.75, r, 'S');
  text(doc, color, size === 'lg' ? 13 : 9, 'extrabold');
  doc.text(level, x + 2 * r + 2, y, { charSpace: 0.25 });
  return x + 2 * r + 2 + doc.getTextWidth(level) + level.length * 0.25;
}

export function sectionTitle(doc: jsPDF, y: number, title: string): number {
  text(doc, C.ink, 11, 'bold');
  doc.text(title, MARGIN, y);
  return y + 3;
}

/** Tablas como en la interfaz: encabezado sobre rubor en texto tenue, filas separadas por reglas finas. */
export function tableStyle(startY: number): Partial<UserOptions> {
  return {
    startY,
    theme: 'plain',
    // Deja libre el encabezado (34 mm) y el pie (22 mm) en las páginas que agrega la tabla
    margin: { left: MARGIN, right: MARGIN, top: 34, bottom: 22 },
    styles: {
      font: FONT,
      fontSize: 8.5,
      textColor: C.ink,
      cellPadding: { top: 2.2, bottom: 2.2, left: 2.5, right: 2.5 },
      lineColor: C.rule,
      lineWidth: { bottom: 0.25 },
    },
    headStyles: { fillColor: C.blush, textColor: C.muted, fontStyle: 'bold', fontSize: 7.5 },
  };
}

/** Lista clave-valor (como los <dl> de la interfaz): rótulo tenue y valor en tinta. */
export function kvStyle(startY: number, labelWidth = 48): Partial<UserOptions> {
  return {
    ...tableStyle(startY),
    columnStyles: { 0: { cellWidth: labelWidth, textColor: C.muted } },
  };
}

/** Pie en todas las páginas y, desde la segunda, el encabezado de la marca. */
export function drawFooter(doc: jsPDF, left: string, header?: { assets: PdfAssets; kind: string; detail: string }): void {
  const w = doc.internal.pageSize.getWidth();
  const h = doc.internal.pageSize.getHeight();
  const pages = doc.getNumberOfPages();
  for (let i = 1; i <= pages; i++) {
    doc.setPage(i);
    if (header && i > 1) drawBrandHeader(doc, header.assets, header.kind, header.detail);
    rule(doc, h - 15);
    text(doc, C.muted, 7.5);
    doc.text(left, MARGIN, h - 10, { maxWidth: w - 2 * MARGIN - 20 });
    doc.text(`${i} / ${pages}`, w - MARGIN, h - 10, { align: 'right' });
    text(doc, C.muted, 7);
    doc.text('Aurora Care · La plataforma apoya, no reemplaza, el criterio médico.', MARGIN, h - 6);
  }
}

export function lastY(doc: jsPDF): number {
  return (doc as unknown as { lastAutoTable: { finalY: number } }).lastAutoTable.finalY;
}
