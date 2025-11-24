import { useState, useEffect } from 'react';
import { Eye, Calendar, AlertCircle, CheckCircle2, Clock, Loader2 } from 'lucide-react';
import { apiClient } from '../services/api';
import { generateCaseReport } from '../utils/generatePdf';

interface Case {
  id: number;
  code: string;
  created_at: string;
  medico_id: number;
  descripcion?: string;
}

interface Image {
  id: number;
  filename: string;
  filepath: string;
  mime_type: string;
  width?: number;
  height?: number;
  uploaded_at: string;
  case_id: number;
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
  message: string;
}

interface CaseWithResults extends Case {
  images?: Image[];
  latestResult?: InferenceResult;
  status?: 'positive' | 'negative' | 'review';
}

export default function CaseManagement() {
  const [cases, setCases] = useState<CaseWithResults[]>([]);
  const [selectedCase, setSelectedCase] = useState<CaseWithResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalCases, setTotalCases] = useState(0);
  const pageSize = 10;

  useEffect(() => {
    loadCases();
  }, [page]);

  const loadCases = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.getCases(page, pageSize);
      if (response.data) {
        setCases(response.data);
        setTotalCases(response.data.length); 
      } else {
        setError(response.error || 'Error al cargar casos');
      }
    } catch (err) {
      setError('Error al cargar casos');
    } finally {
      setLoading(false);
    }
  };

  const loadCaseDetails = async (caseId: number) => {
    setLoadingDetails(true);
    try {
      // Cargar caso completo
      const caseResponse = await apiClient.getCase(caseId);
      if (!caseResponse.data) {
        setError(caseResponse.error || 'Error al cargar caso');
        return;
      }

      // Cargar imágenes del caso
      const imagesResponse = await apiClient.getCaseImages(caseId);
      const images = imagesResponse.data || [];

      // Cargar resultados de la última imagen (si existe)
      let latestResult: InferenceResult | undefined;
      if (images.length > 0) {
        const lastImage = images[0];
        const resultsResponse = await apiClient.getImageResults(lastImage.id);
        if (resultsResponse.data) {
          latestResult = resultsResponse.data;
        }
      }

      // Determinar status basado en el resultado
      let status: 'positive' | 'negative' | 'review' = 'review';
      if (latestResult) {
        if (latestResult.detected) {
          status = 'positive';
        } else if (latestResult.confidence >= 90) {
          status = 'negative';
        } else {
          status = 'review';
        }
      }

      const caseWithDetails: CaseWithResults = {
        ...caseResponse.data,
        images,
        latestResult,
        status,
      };

      setSelectedCase(caseWithDetails);
    } catch (err) {
      setError('Error al cargar detalles del caso');
    } finally {
      setLoadingDetails(false);
    }
  };

  const getStatusBadge = (status?: string) => {
    if (!status) return null;
    
    const styles = {
      positive: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      negative: 'bg-green-500/10 text-green-400 border-green-500/20',
      review: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
    };

    const labels = {
      positive: 'Positivo',
      negative: 'Negativo',
      review: 'En Revisión',
    };

    return (
      <span className={`px-2 py-0.5 text-[10px] font-semibold rounded border ${styles[status as keyof typeof styles]}`}>
        {labels[status as keyof typeof labels]}
      </span>
    );
  };

  const getStatusIcon = (status?: string) => {
    if (!status) return null;
    switch (status) {
      case 'positive':
        return <AlertCircle className="w-4 h-4 text-orange-400" />;
      case 'negative':
        return <CheckCircle2 className="w-4 h-4 text-green-400" />;
      case 'review':
        return <Clock className="w-4 h-4 text-yellow-400" />;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-CL', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
  };

  // Calcular estadísticas
  const stats = {
    total: cases.length,
    positive: cases.filter((c) => c.status === 'positive').length,
    review: cases.filter((c) => c.status === 'review').length,
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      <div className="mb-4">
        <h2 className="text-lg font-bold text-foreground">Gestión de Casos</h2>
        <p className="mt-0.5 text-xs text-muted-foreground">
          Historial de análisis realizados y seguimiento de casos
        </p>
      </div>

      {error && (
        <div className="mb-3 bg-destructive/10 border border-destructive/20 text-destructive-foreground px-3 py-2 rounded text-xs">
          {error}
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-3 mb-4">
        <div className="bg-card border border-border rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[10px] text-muted-foreground">Total de Casos</p>
              <p className="text-xl font-bold text-foreground mt-0.5">{stats.total}</p>
            </div>
            <div className="w-8 h-8 bg-blue-500/10 rounded flex items-center justify-center">
              <Calendar className="w-4 h-4 text-blue-400" />
            </div>
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[10px] text-muted-foreground">Casos Positivos</p>
              <p className="text-xl font-bold text-orange-400 mt-0.5">{stats.positive}</p>
            </div>
            <div className="w-8 h-8 bg-orange-500/10 rounded flex items-center justify-center">
              <AlertCircle className="w-4 h-4 text-orange-400" />
            </div>
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[10px] text-muted-foreground">En Revisión</p>
              <p className="text-xl font-bold text-yellow-400 mt-0.5">{stats.review}</p>
            </div>
            <div className="w-8 h-8 bg-yellow-500/10 rounded flex items-center justify-center">
              <Clock className="w-4 h-4 text-yellow-400" />
            </div>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <div className="bg-card border border-border rounded-lg overflow-hidden">
            {loading ? (
              <div className="text-center py-8">
                <Loader2 className="w-6 h-6 mx-auto mb-2 text-primary animate-spin" />
                <p className="text-xs text-muted-foreground">Cargando casos...</p>
              </div>
            ) : cases.length === 0 ? (
              <div className="text-center py-8">
                <Calendar className="w-12 h-12 mx-auto mb-2 text-muted-foreground" />
                <p className="text-xs text-muted-foreground">No hay casos registrados</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-secondary/50 border-b border-border">
                    <tr>
                      <th className="px-3 py-2 text-left text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">ID CASO</th>
                      <th className="px-3 py-2 text-left text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">PACIENTE</th>
                      <th className="px-3 py-2 text-left text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">FECHA</th>
                      <th className="px-3 py-2 text-left text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">RESULTADO</th>
                      <th className="px-3 py-2 text-left text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">CONFIANZA</th>
                      <th className="px-3 py-2 text-left text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">ACCIÓN</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {cases.map((caseItem) => (
                      <tr key={caseItem.id} className="hover:bg-secondary/30 transition-colors">
                        <td className="px-3 py-2 whitespace-nowrap text-xs text-foreground font-medium">
                          #{caseItem.id}
                        </td>
                        <td className="px-3 py-2 whitespace-nowrap text-xs text-muted-foreground">
                          {caseItem.code}
                        </td>
                        <td className="px-3 py-2 whitespace-nowrap text-xs text-muted-foreground">
                          {formatDate(caseItem.created_at)}
                        </td>
                        <td className="px-3 py-2 whitespace-nowrap">
                          {getStatusBadge(caseItem.status)}
                        </td>
                        <td className="px-3 py-2 whitespace-nowrap text-xs text-foreground">
                          {caseItem.latestResult ? `${caseItem.latestResult.confidence.toFixed(1)}%` : '-'}
                        </td>
                        <td className="px-3 py-2 whitespace-nowrap">
                          <button
                            onClick={() => loadCaseDetails(caseItem.id)}
                            disabled={loadingDetails}
                            className="flex items-center space-x-1 text-primary hover:text-primary/80 font-medium text-xs disabled:opacity-50"
                          >
                            <Eye className="w-3.5 h-3.5" />
                            <span>Ver Detalle</span>
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            
            {/* Paginación */}
            <div className="px-3 py-2 border-t border-border flex items-center justify-between">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-2 py-1 text-xs text-muted-foreground hover:text-foreground disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Anterior
              </button>
              <span className="text-xs text-muted-foreground">Página {page}</span>
              <button
                onClick={() => setPage(p => p + 1)}
                disabled={cases.length < pageSize}
                className="px-2 py-1 text-xs text-muted-foreground hover:text-foreground disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Siguiente
              </button>
            </div>
          </div>
        </div>

        <div className="lg:col-span-1">
          {selectedCase ? (
            <div className="bg-card border border-border rounded-lg p-4 space-y-3">
              <h3 className="text-sm font-semibold text-foreground mb-3">Detalle del Caso</h3>
              
              <div className="flex items-center justify-between pb-2 border-b border-border">
                <span className="text-xs text-muted-foreground">Estado</span>
                {getStatusBadge(selectedCase.status)}
              </div>

              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-xs text-muted-foreground">ID del Caso:</span>
                  <span className="text-xs font-semibold text-foreground">#{selectedCase.id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-xs text-muted-foreground">Paciente:</span>
                  <span className="text-xs font-semibold text-foreground">
                    {selectedCase.code}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-xs text-muted-foreground">Fecha:</span>
                  <span className="text-xs font-semibold text-foreground">
                    {formatDate(selectedCase.created_at)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-xs text-muted-foreground">Confianza:</span>
                  <span className="text-xs font-semibold text-foreground">
                    {selectedCase.latestResult ? `${selectedCase.latestResult.confidence.toFixed(1)}%` : '-'}
                  </span>
                </div>
                {selectedCase.images && selectedCase.images.length > 0 && (
                  <div className="flex justify-between">
                    <span className="text-xs text-muted-foreground">Imágenes:</span>
                    <span className="text-xs font-semibold text-foreground">
                      {selectedCase.images.length}
                    </span>
                  </div>
                )}
              </div>

              {selectedCase.images && selectedCase.images.length > 0 && (
                <div className="pt-2">
                  <div className="aspect-video bg-background border border-border rounded relative overflow-hidden">
                    <img
                      src={apiClient.getImageUrl(selectedCase.id, selectedCase.images[0].id)}
                      alt={selectedCase.images[0].filename}
                      className="w-full h-full object-contain"
                      onError={(e) => {
                        e.currentTarget.style.display = 'none';
                      }}
                    />
                    {selectedCase.latestResult?.detected && selectedCase.latestResult.detections.length > 0 && (
                      selectedCase.latestResult.detections.map((detection, idx) => (
                        <div
                          key={idx}
                          className="absolute border-2 border-orange-400 rounded"
                          style={{
                            left: `${detection.x * 100}%`,
                            top: `${detection.y * 100}%`,
                            width: `${detection.width * 100}%`,
                            height: `${detection.height * 100}%`,
                          }}
                        >
                          <div className="absolute -top-6 left-0 bg-orange-400 text-white px-1.5 py-0.5 text-[10px] font-bold rounded">
                            {(detection.confidence * 100).toFixed(0)}%
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}

              {selectedCase.latestResult && (
                <div
                  className={`p-2 rounded border ${
                    selectedCase.status === 'positive'
                      ? 'bg-orange-500/10 border-orange-500/20'
                      : selectedCase.status === 'negative'
                      ? 'bg-green-500/10 border-green-500/20'
                      : 'bg-yellow-500/10 border-yellow-500/20'
                  }`}
                >
                  <div className="flex items-start space-x-2">
                    {getStatusIcon(selectedCase.status)}
                    <p className="text-[10px] text-foreground">
                      {selectedCase.latestResult.message}
                    </p>
                  </div>
                </div>
              )}

              <button
                onClick={async () => {
                  if (selectedCase) {
                    try {
                      if (selectedCase.images && selectedCase.images.length > 0 && selectedCase.latestResult) {
                        await generateCaseReport(
                          selectedCase,
                          selectedCase.images,
                          selectedCase.latestResult
                        );
                      } else {
                        alert('El caso no tiene imágenes o resultados de análisis para generar el reporte');
                      }
                    } catch (error) {
                      console.error('Error al generar reporte:', error);
                      alert('Error al generar el reporte PDF');
                    }
                  }
                }}
                disabled={!selectedCase || !selectedCase.images || selectedCase.images.length === 0 || !selectedCase.latestResult}
                className="w-full mt-2 bg-primary hover:bg-primary/90 disabled:bg-muted disabled:text-muted-foreground disabled:cursor-not-allowed text-primary-foreground px-3 py-2 rounded text-xs font-semibold transition-colors"
              >
                Generar Reporte PDF
              </button>
            </div>
          ) : (
            <div className="bg-card border border-border rounded-lg p-4">
              <div className="text-center py-8">
                <Eye className="w-12 h-12 mx-auto mb-2 text-muted-foreground" />
                <p className="text-xs text-muted-foreground">Selecciona un caso para ver sus detalles</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
