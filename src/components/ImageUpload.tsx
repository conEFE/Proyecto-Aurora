import { useState } from 'react';
import { Upload, Image as ImageIcon, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import { apiClient } from '../services/api';
import PatientModal from './PatientModal';

interface DetectionBox {
  x: number;
  y: number;
  width: number;
  height: number;
  confidence: number;
  class_name: string;
}

interface InferenceResult {
  image_id: number;
  detected: boolean;
  confidence: number;
  detections: DetectionBox[];
  processing_time_ms: number;
  model_version: string;
  message: string;
}

export default function ImageUpload() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [patientCode, setPatientCode] = useState('');
  const [currentCaseId, setCurrentCaseId] = useState<number | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<InferenceResult | null>(null);
  const [showPatientModal, setShowPatientModal] = useState(false);
  const [selectedPatientId, setSelectedPatientId] = useState<number | null>(null);
  const [selectedPatient, setSelectedPatient] = useState<{ id: number; rut: string; name?: string } | null>(null);
  const [processingProgress, setProcessingProgress] = useState(0); // 0-100
  const [processingMessage, setProcessingMessage] = useState('');

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setResult(null);
      setError(null);
      
      const reader = new FileReader();
      reader.onload = (e) => {
        setSelectedImage(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleCreateCase = async () => {
    if (!patientCode.trim()) {
      setError('Por favor ingresa un código de paciente');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const response = await apiClient.createCase(
        patientCode.trim(),
        selectedPatientId || undefined
      );
      
      console.log('Respuesta de createCase:', response); // Debug
      
      if (response.data && response.data.id) {
        setCurrentCaseId(response.data.id);
        setError(null);
        console.log('Caso creado con ID:', response.data.id); // Debug
      } else {
        const errorMsg = response.error || 'Error al crear caso';
        setError(errorMsg);
        console.error('Error al crear caso:', errorMsg, response); // Debug
        setCurrentCaseId(null);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error al crear caso';
      setError(errorMsg);
      console.error('Excepción al crear caso:', err); // Debug
      setCurrentCaseId(null); 
    } finally {
      setIsUploading(false);
    }
  };

  const handleProcess = async () => {
    if (!selectedFile) {
      setError('Por favor selecciona una imagen');
      return;
    }

    if (!currentCaseId) {
      setError('Por favor crea un caso primero');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setResult(null);
    setProcessingProgress(0);
    setProcessingMessage('Iniciando análisis...');

    try {
      // Simular progreso mientras se sube la imagen
      setProcessingMessage('Subiendo imagen al servidor...');
      setProcessingProgress(10);

      const uploadResponse = await apiClient.uploadImage(currentCaseId, selectedFile);
      
      if (!uploadResponse.data) {
        setError(uploadResponse.error || 'Error al subir imagen');
        setIsProcessing(false);
        return;
      }

      const imageId = uploadResponse.data.id;
      setProcessingProgress(30);
      setProcessingMessage('Imagen recibida. Iniciando análisis con modelo YOLO...');

      // Simulacion
      const progressInterval = setInterval(() => {
        setProcessingProgress((prev) => {
          if (prev < 90) {
            const newProgress = prev + Math.random() * 15;
            if (newProgress < 60) {
              setProcessingMessage('Analizando patrones en la imagen...');
            } else if (newProgress < 80) {
              setProcessingMessage('Detectando posibles lesiones...');
            } else {
              setProcessingMessage('Finalizando análisis...');
            }
            return Math.min(newProgress, 90);
          }
          return prev;
        });
      }, 300);

      const resultsResponse = await apiClient.getImageResults(imageId);
      
      clearInterval(progressInterval);
      setProcessingProgress(100);
      setProcessingMessage('Análisis completado');

      const resultData = resultsResponse.data;
      if (resultData) {
        setTimeout(() => {
          setResult(resultData);
          setIsProcessing(false);
          setProcessingProgress(0);
          setProcessingMessage('');
        }, 500);
      } else {
        setError(resultsResponse.error || 'Error al procesar imagen');
        setIsProcessing(false);
        setProcessingProgress(0);
        setProcessingMessage('');
      }
    } catch {
      setError('Error al procesar imagen');
      setIsProcessing(false);
      setProcessingProgress(0);
      setProcessingMessage('');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      <div className="mb-4">
        <h2 className="text-lg font-bold text-foreground">Análisis de Imágenes Médicas</h2>
        <p className="mt-1 text-xs text-muted-foreground">
          Sube una imagen médica (mamografía) para procesarla con el modelo YOLO
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        <div className="space-y-4">
          {/* Sección de caso */}
          <div className="bg-card border border-border rounded-lg p-4">
            <h4 className="text-xs font-semibold text-foreground mb-2">Caso Clínico</h4>
            
            {selectedPatient && (
              <div className="mb-2 p-2 bg-primary/10 border border-primary/20 rounded">
                <p className="text-[10px] text-muted-foreground mb-0.5">Paciente asignado:</p>
                <p className="text-xs font-semibold text-foreground">
                  {selectedPatient.name || 'Sin nombre'} - RUT: {selectedPatient.rut}
                </p>
                <button
                  onClick={() => {
                    setSelectedPatient(null);
                    setSelectedPatientId(null);
                  }}
                  className="mt-1 text-[10px] text-primary hover:text-primary/80"
                >
                  Cambiar paciente
                </button>
              </div>
            )}

            <div className="flex gap-2">
              <input
                type="text"
                value={patientCode}
                onChange={(e) => setPatientCode(e.target.value)}
                placeholder="Código de paciente"
                className="flex-1 px-3 py-1.5 bg-background border border-input rounded text-xs text-foreground focus:ring-2 focus:ring-primary focus:border-transparent"
                disabled={isUploading || isProcessing}
              />
              <button
                onClick={() => setShowPatientModal(true)}
                className="px-3 py-1.5 bg-secondary hover:bg-secondary/80 text-secondary-foreground font-semibold rounded text-xs transition-colors"
                title="Asignar paciente existente o crear nuevo"
              >
                Paciente
              </button>
              <button
                onClick={handleCreateCase}
                disabled={isUploading || isProcessing || !patientCode.trim()}
                className="px-3 py-1.5 bg-primary hover:bg-primary/90 disabled:bg-muted disabled:text-muted-foreground text-primary-foreground font-semibold rounded text-xs transition-colors"
              >
                {isUploading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Crear Caso'}
              </button>
            </div>
            {currentCaseId && (
              <p className="mt-1.5 text-[10px] text-green-400">Caso #{currentCaseId} creado</p>
            )}
          </div>

          {/* Sección de carga de imagen */}
          <div className="bg-card border-2 border-dashed border-border rounded-lg p-4">
            <div className="text-center">
              <div className="mx-auto w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-2">
                <Upload className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-sm font-semibold text-foreground mb-1">Cargar Imagen</h3>
              <p className="text-[10px] text-muted-foreground mb-3">
                Formatos soportados: JPEG, PNG (máx. 10MB)
              </p>
              <label className="inline-flex items-center px-4 py-2 bg-primary hover:bg-primary/90 text-primary-foreground font-semibold rounded cursor-pointer transition-colors text-xs">
                <ImageIcon className="w-3.5 h-3.5 mr-1.5" />
                Seleccionar Imagen
                <input
                  type="file"
                  accept="image/jpeg,image/png"
                  onChange={handleImageUpload}
                  className="hidden"
                  disabled={isProcessing}
                />
              </label>
            </div>
          </div>

          {selectedImage && (
            <div className="bg-card border border-border rounded-lg p-4">
              <h4 className="text-xs font-semibold text-foreground mb-2">Vista Previa</h4>
              <div className="relative aspect-video bg-background border border-border rounded overflow-hidden">
                <img
                  src={selectedImage}
                  alt="Preview"
                  className="w-full h-full object-contain"
                />
              </div>
              <button
                onClick={handleProcess}
                disabled={isProcessing || !currentCaseId}
                className="w-full mt-3 flex items-center justify-center space-x-1.5 bg-primary hover:bg-primary/90 disabled:bg-muted disabled:text-muted-foreground text-primary-foreground px-4 py-2 rounded text-xs font-semibold transition-colors"
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Procesando...</span>
                  </>
                ) : (
                  <span>Procesar Imagen</span>
                )}
              </button>
              
              {!currentCaseId && (
                <p className="mt-1.5 text-[10px] text-orange-400 text-center">
                  ⚠️ Debes crear un caso clínico antes de procesar la imagen
                </p>
              )}
            </div>
          )}

          {error && (
            <div className="bg-destructive/10 border border-destructive/20 text-destructive-foreground px-3 py-2 rounded text-xs">
              {error}
            </div>
          )}
        </div>

        <div className="space-y-4">
          <div className="bg-card border border-border rounded-lg p-4">
            <h4 className="text-sm font-semibold text-foreground mb-3">Resultado del Análisis</h4>

            {!result && !isProcessing && (
              <div className="text-center py-8 text-muted-foreground">
                <AlertCircle className="w-8 h-8 mx-auto mb-2" />
                <p className="text-xs">Sube y procesa una imagen para ver los resultados</p>
              </div>
            )}

            {isProcessing && (
              <div className="space-y-3">
                <div className="text-center py-6">
                  <Loader2 className="w-12 h-12 mx-auto mb-2 text-primary animate-spin" />
                  <p className="text-xs font-semibold text-foreground mb-1">
                    {processingMessage || 'Estamos procesando tu imagen...'}
                  </p>
                  <p className="text-[10px] text-muted-foreground mb-3">
                    Por favor espera, esto puede tomar unos segundos
                  </p>
                  
                  {/* Barra de progreso */}
                  <div className="w-full bg-secondary rounded-full h-2 mb-2">
                    <div 
                      className="bg-primary h-2 rounded-full transition-all duration-300 ease-out"
                      style={{ width: `${processingProgress}%` }}
                    ></div>
                  </div>
                  <p className="text-[10px] text-muted-foreground">{Math.round(processingProgress)}% completado</p>
                </div>

                {/* Resultado simulado mientras procesa */}
                <div className="bg-secondary/50 border border-border rounded p-3">
                  <div className="flex items-start space-x-2">
                    <Loader2 className="w-4 h-4 text-muted-foreground animate-spin flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <p className="text-xs font-medium text-foreground mb-1.5">Análisis en progreso...</p>
                      <div className="space-y-1.5">
                        <div>
                          <div className="flex justify-between text-[10px] mb-0.5">
                            <span className="text-muted-foreground">Nivel de Confianza</span>
                            <span className="font-semibold text-foreground">0.0%</span>
                          </div>
                          <div className="w-full bg-secondary rounded-full h-1.5">
                            <div className="bg-muted h-1.5 rounded-full" style={{ width: '0%' }}></div>
                          </div>
                        </div>
                        <p className="text-[10px] text-muted-foreground italic">
                          El modelo está analizando la imagen. Los resultados aparecerán aquí cuando termine.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {result && !isProcessing && (
              <div className="space-y-3">
                <div
                  className={`p-3 rounded border-2 ${
                    result.detected
                      ? 'bg-orange-500/10 border-orange-500/20'
                      : 'bg-green-500/10 border-green-500/20'
                  }`}
                >
                  <div className="flex items-start space-x-2">
                    {result.detected ? (
                      <AlertCircle className="w-5 h-5 text-orange-400 flex-shrink-0 mt-0.5" />
                    ) : (
                      <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                    )}
                    <div>
                      <p
                        className={`text-xs font-semibold ${
                          result.detected ? 'text-orange-400' : 'text-green-400'
                        }`}
                      >
                        {result.message}
                      </p>
                      {result.detected && (
                        <p className="text-[10px] text-orange-400/80 mt-0.5">
                          Se recomienda revisión por especialista
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <div>
                    <div className="flex justify-between text-[10px] mb-1">
                      <span className="text-muted-foreground">Nivel de Confianza</span>
                      <span className="font-semibold text-foreground">{result.confidence.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-1.5">
                      <div 
                        className="bg-primary h-1.5 rounded-full" 
                        style={{ width: `${result.confidence}%` }}
                      ></div>
                    </div>
                  </div>

                  {result.detections && result.detections.length > 0 && (
                    <div>
                      <p className="text-[10px] font-semibold text-foreground mb-1">
                        Detecciones: {result.detections.length}
                      </p>
                      <div className="space-y-1">
                        {result.detections.map((detection, idx) => (
                          <div key={idx} className="text-[10px] text-muted-foreground">
                            • {detection.class_name}: {(detection.confidence * 100).toFixed(1)}%
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="pt-2 border-t border-border">
                    <div className="grid grid-cols-2 gap-2 text-[10px]">
                      <div>
                        <span className="text-muted-foreground">Tiempo:</span>
                        <span className="ml-1 text-foreground">{(result.processing_time_ms / 1000).toFixed(2)}s</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Modelo:</span>
                        <span className="ml-1 text-foreground">{result.model_version}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Nota importante */}
          <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3">
            <div className="flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 text-blue-400 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="text-xs font-semibold text-foreground mb-1">Nota Importante</h4>
                <p className="text-[10px] text-muted-foreground">
                  Este sistema es una herramienta de apoyo diagnóstico. Los resultados deben ser validados por un profesional médico cualificado.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <PatientModal
        isOpen={showPatientModal}
        onClose={() => setShowPatientModal(false)}
        onSelectPatient={(patient) => {
          setSelectedPatientId(patient.id);
          setSelectedPatient({
            id: patient.id,
            rut: patient.rut,
            name: `${patient.first_name} ${patient.last_name}`.trim(),
          });
        }}
      />
    </div>
  );
}
