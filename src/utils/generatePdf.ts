import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { apiClient } from '../services/api';

interface CaseData {
  id: number;
  code: string;
  created_at: string;
  medico_id: number;
  patient_id?: number;
  patient?: {
    id: number;
    rut: string;
    first_name?: string;
    last_name?: string;
    birth_date?: string;
    sex?: string;
  };
}

interface ImageData {
  id: number;
  filename: string;
  uploaded_at: string;
}

interface InferenceResult {
  image_id: number;
  detected: boolean;
  confidence: number;
  detections: Array<{
    x: number;
    y: number;
    width: number;
    height: number;
    confidence: number;
    class_name: string;
  }>;
  processing_time_ms: number;
  model_version: string;
  message: string;
}

export async function generateCaseReport(
  caseData: CaseData,
  images: ImageData[],
  result: InferenceResult | null
) {
  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 20;
  let yPosition = margin;

  // Colores
  const primaryColor: [number, number, number] = [231, 30, 99]; // Pink
  const successColor: [number, number, number] = [34, 197, 94]; // Green
  const warningColor: [number, number, number] = [249, 115, 22]; // Orange

  // Header
  doc.setFillColor(...primaryColor);
  doc.rect(0, 0, pageWidth, 40, 'F');
  
  doc.setTextColor(255, 255, 255);
  doc.setFontSize(20);
  doc.setFont('helvetica', 'bold');
  doc.text('Reporte de Análisis Médico', pageWidth / 2, 25, { align: 'center' });
  
  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  doc.text('Sistema de Detección de Cáncer de Mama - Modelo YOLO', pageWidth / 2, 35, { align: 'center' });
  
  yPosition = 50;
  doc.setTextColor(0, 0, 0);

  // Información del Caso
  doc.setFontSize(14);
  doc.setFont('helvetica', 'bold');
  doc.text('Información del Caso', margin, yPosition);
  yPosition += 10;

  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  
  const caseInfo = [
    ['ID del Caso', `#${caseData.id}`],
    ['Código', caseData.code],
    ['Fecha de Creación', new Date(caseData.created_at).toLocaleDateString('es-CL')],
  ];

  autoTable(doc, {
    startY: yPosition,
    head: [['Campo', 'Valor']],
    body: caseInfo,
    theme: 'striped',
    headStyles: { fillColor: primaryColor, textColor: [255, 255, 255] },
    margin: { left: margin, right: margin },
    styles: { fontSize: 9 },
  });

  yPosition = (doc as unknown as { lastAutoTable: { finalY: number } }).lastAutoTable.finalY + 15;

  // Información del Paciente (si existe)
  if (caseData.patient) {
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('Información del Paciente', margin, yPosition);
    yPosition += 10;

    const patientInfo = [
      ['RUT', caseData.patient.rut],
      ['Nombre', `${caseData.patient.first_name || 'N/A'} ${caseData.patient.last_name || ''}`.trim() || 'N/A'],
      ['Fecha de Nacimiento', caseData.patient.birth_date ? new Date(caseData.patient.birth_date).toLocaleDateString('es-CL') : 'N/A'],
      ['Sexo', caseData.patient.sex === 'M' ? 'Masculino' : caseData.patient.sex === 'F' ? 'Femenino' : 'N/A'],
    ];

    autoTable(doc, {
      startY: yPosition,
      head: [['Campo', 'Valor']],
      body: patientInfo,
      theme: 'striped',
      headStyles: { fillColor: primaryColor, textColor: [255, 255, 255] },
      margin: { left: margin, right: margin },
      styles: { fontSize: 9 },
    });

    yPosition = (doc as unknown as { lastAutoTable: { finalY: number } }).lastAutoTable.finalY + 15;
  }

  // Resultados del Análisis
  if (result) {
    // Nueva página si es necesario
    if (yPosition > pageHeight - 80) {
      doc.addPage();
      yPosition = margin;
    }

    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('Resultados del Análisis', margin, yPosition);
    yPosition += 10;

    const statusColor = result.detected ? warningColor : successColor;
    const statusText = result.detected ? 'POSITIVO - Lesión Detectada' : 'NEGATIVO - Sin Lesiones';

    doc.setFillColor(...statusColor);
    doc.roundedRect(margin, yPosition, pageWidth - 2 * margin, 15, 3, 3, 'F');
    
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.text(statusText, pageWidth / 2, yPosition + 10, { align: 'center' });
    
    yPosition += 20;
    doc.setTextColor(0, 0, 0);

    const resultInfo = [
      ['Nivel de Confianza', `${result.confidence.toFixed(2)}%`],
      ['Modelo Utilizado', result.model_version],
      ['Tiempo de Procesamiento', `${(result.processing_time_ms / 1000).toFixed(2)} segundos`],
      ['Mensaje', result.message],
    ];

    autoTable(doc, {
      startY: yPosition,
      head: [['Campo', 'Valor']],
      body: resultInfo,
      theme: 'striped',
      headStyles: { fillColor: primaryColor, textColor: [255, 255, 255] },
      margin: { left: margin, right: margin },
      styles: { fontSize: 9 },
    });

    yPosition = (doc as unknown as { lastAutoTable: { finalY: number } }).lastAutoTable.finalY + 15;

    // Detecciones (si existen)
    if (result.detections && result.detections.length > 0) {
      if (yPosition > pageHeight - 100) {
        doc.addPage();
        yPosition = margin;
      }

      doc.setFontSize(12);
      doc.setFont('helvetica', 'bold');
      doc.text('Detecciones Encontradas', margin, yPosition);
      yPosition += 10;

      const detectionsData = result.detections.map((det, idx) => [
        `Detección ${idx + 1}`,
        `${(det.confidence * 100).toFixed(1)}%`,
        `${(det.width * 100).toFixed(1)}% x ${(det.height * 100).toFixed(1)}%`,
        det.class_name,
      ]);

      autoTable(doc, {
        startY: yPosition,
        head: [['Detección', 'Confianza', 'Tamaño', 'Tipo']],
        body: detectionsData,
        theme: 'striped',
        headStyles: { fillColor: primaryColor, textColor: [255, 255, 255] },
        margin: { left: margin, right: margin },
        styles: { fontSize: 8 },
      });

      yPosition = (doc as unknown as { lastAutoTable: { finalY: number } }).lastAutoTable.finalY + 15;
    }
  }

  // Imágenes (si existen)
  if (images && images.length > 0) {
    for (let i = 0; i < images.length; i++) {
      const image = images[i];
      
      // Nueva página para cada imagen
      if (i > 0 || yPosition > pageHeight - 120) {
        doc.addPage();
        yPosition = margin;
      }

      doc.setFontSize(12);
      doc.setFont('helvetica', 'bold');
      doc.text(`Imagen ${i + 1}: ${image.filename}`, margin, yPosition);
      yPosition += 10;

      try {
        // Obtener URL de la imagen
        const imageUrl = apiClient.getImageUrl(caseData.id, image.id);
        
        // Cargar imagen
        const img = await loadImageFromUrl(imageUrl);
        
        // Calcular dimensiones para que quepa en la página
        const maxWidth = pageWidth - 2 * margin;
        const maxHeight = pageHeight - yPosition - 30;
        let imgWidth = img.width;
        let imgHeight = img.height;
        
        const ratio = Math.min(maxWidth / imgWidth, maxHeight / imgHeight);
        imgWidth = imgWidth * ratio;
        imgHeight = imgHeight * ratio;
        
        const xPosition = (pageWidth - imgWidth) / 2;
        
        doc.addImage(img, 'JPEG', xPosition, yPosition, imgWidth, imgHeight);
        yPosition += imgHeight + 10;
        
        doc.setFontSize(8);
        doc.setFont('helvetica', 'italic');
        doc.setTextColor(128, 128, 128);
        doc.text(
          `Subida el ${new Date(image.uploaded_at).toLocaleDateString('es-CL')} a las ${new Date(image.uploaded_at).toLocaleTimeString('es-CL')}`,
          pageWidth / 2,
          yPosition,
          { align: 'center' }
        );
        doc.setTextColor(0, 0, 0);
        yPosition += 10;
      } catch {
        doc.setFontSize(10);
        doc.setTextColor(255, 0, 0);
        doc.text('Error al cargar la imagen', margin, yPosition);
        doc.setTextColor(0, 0, 0);
        yPosition += 10;
      }
    }
  }

  // Footer en cada página
  const totalPages = doc.getNumberOfPages();
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);
    doc.setFontSize(8);
    doc.setTextColor(128, 128, 128);
    doc.text(
      `Página ${i} de ${totalPages}`,
      pageWidth / 2,
      pageHeight - 10,
      { align: 'center' }
    );
    doc.text(
      `Generado el ${new Date().toLocaleDateString('es-CL')} a las ${new Date().toLocaleTimeString('es-CL')}`,
      pageWidth / 2,
      pageHeight - 5,
      { align: 'center' }
    );
  }

  // Generar nombre del archivo
  const fileName = `Reporte_Caso_${caseData.id}_${new Date().toISOString().split('T')[0]}.pdf`;
  
  // Guardar PDF
  doc.save(fileName);
}

// Función auxiliar para cargar imagen desde URL
function loadImageFromUrl(url: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = url;
  });
}
