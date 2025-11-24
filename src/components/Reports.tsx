import { useState, useEffect } from 'react';
import { Download, TrendingUp, Users, Target, Calendar, Loader2 } from 'lucide-react';
import { apiClient } from '../services/api';

export default function Reports() {
  const [statistics, setStatistics] = useState({
    total_cases: 0,
    positive_cases: 0,
    negative_cases: 0,
    average_confidence: 0,
    average_processing_time_ms: 0,
    total_detections: 0,
  });
  const [monthlyData, setMonthlyData] = useState<Array<{
    month: string;
    cases: number;
    positive: number;
    negative: number;
  }>>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsResponse, monthlyResponse] = await Promise.all([
        apiClient.getStatistics(),
        apiClient.getMonthlyData(),
      ]);

      if (statsResponse.data) {
        setStatistics(statsResponse.data);
      } else {
        setError(statsResponse.error || 'Error al cargar estadísticas');
      }

      if (monthlyResponse.data) {
        setMonthlyData(monthlyResponse.data);
      }
    } catch (err) {
      setError('Error al cargar datos de reportes');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const displayStats = [
    { 
      label: 'Casos Procesados', 
      value: statistics.total_cases.toLocaleString(), 
      icon: Users, 
      color: 'blue' 
    },
    { 
      label: 'Precisión Promedio', 
      value: `${statistics.average_confidence.toFixed(1)}%`, 
      icon: Target, 
      color: 'pink' 
    },
    { 
      label: 'Detecciones Positivas', 
      value: statistics.positive_cases.toLocaleString(), 
      icon: TrendingUp, 
      color: 'orange' 
    },
    { 
      label: 'Tiempo Promedio', 
      value: `${(statistics.average_processing_time_ms / 1000).toFixed(1)}s`, 
      icon: Calendar, 
      color: 'green' 
    },
  ];

  const maxCases = Math.max(...monthlyData.map((d) => d.cases), 1);
  const totalCases = statistics.total_cases;
  const positivePercentage = totalCases > 0 ? (statistics.positive_cases / totalCases) * 100 : 0;
  const negativePercentage = totalCases > 0 ? (statistics.negative_cases / totalCases) * 100 : 0;

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      <div className="mb-4 flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-bold text-foreground">Reportes y Estadísticas</h2>
          <p className="mt-0.5 text-xs text-muted-foreground">
            Análisis del rendimiento del sistema y métricas de diagnóstico
          </p>
        </div>
        <button className="mt-3 sm:mt-0 flex items-center space-x-1.5 bg-primary hover:bg-primary/90 text-primary-foreground px-4 py-2 rounded text-xs font-semibold transition-colors">
          <Download className="w-3.5 h-3.5" />
          <span>Exportar PDF</span>
        </button>
      </div>

      {error && (
        <div className="mb-3 bg-destructive/10 border border-destructive/20 text-destructive-foreground px-3 py-2 rounded text-xs">
          {error}
        </div>
      )}

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
        {displayStats.map((stat, index) => {
          const Icon = stat.icon;
          const colorClasses = {
            blue: 'bg-blue-500/10 text-blue-400',
            pink: 'bg-primary/10 text-primary',
            orange: 'bg-orange-500/10 text-orange-400',
            green: 'bg-green-500/10 text-green-400',
          };

          return (
            <div
              key={index}
              className="bg-card border border-border rounded-lg p-3"
            >
              <div className="flex items-center justify-between mb-2">
                <div className={`w-8 h-8 rounded flex items-center justify-center ${colorClasses[stat.color as keyof typeof colorClasses]}`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <p className="text-xl font-bold text-foreground">{stat.value}</p>
              <p className="text-[10px] text-muted-foreground mt-0.5">{stat.label}</p>
            </div>
          );
        })}
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 bg-card border border-border rounded-lg p-4">
          <h3 className="text-sm font-semibold text-foreground mb-4">
            Análisis Mensual de Casos (2025)
          </h3>

          <div className="space-y-3">
            {monthlyData.length > 0 ? (
              monthlyData.map((data, index) => (
                <div key={index} className="space-y-1.5">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-medium text-foreground w-20">{data.month}</span>
                    <span className="text-muted-foreground">{data.cases} casos</span>
                  </div>
                  <div className="flex space-x-1 h-6">
                    {data.positive > 0 && (
                      <div
                        className="bg-orange-400 rounded-l flex items-center justify-center text-[10px] text-white font-semibold"
                        style={{ width: `${(data.positive / maxCases) * 100}%` }}
                      >
                        {data.positive > 5 && data.positive}
                      </div>
                    )}
                    {data.negative > 0 && (
                      <div
                        className="bg-green-400 rounded-r flex items-center justify-center text-[10px] text-white font-semibold"
                        style={{ width: `${(data.negative / maxCases) * 100}%` }}
                      >
                        {data.negative > 15 && data.negative}
                      </div>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <p className="text-xs">No hay datos mensuales disponibles</p>
              </div>
            )}
          </div>

          <div className="flex items-center justify-center space-x-4 mt-4 pt-4 border-t border-border">
            <div className="flex items-center space-x-1.5">
              <div className="w-3 h-3 bg-orange-400 rounded"></div>
              <span className="text-[10px] text-muted-foreground">Positivos</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <div className="w-3 h-3 bg-green-400 rounded"></div>
              <span className="text-[10px] text-muted-foreground">Negativos</span>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="text-sm font-semibold text-foreground mb-3">
              Distribución de Resultados
            </h3>

            <div className="space-y-3">
              <div>
                <div className="flex justify-between items-center mb-1.5">
                  <span className="text-xs text-muted-foreground">Negativos</span>
                  <span className="text-xs font-semibold text-foreground">{negativePercentage.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div className="bg-green-400 h-2 rounded-full" style={{ width: `${negativePercentage}%` }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between items-center mb-1.5">
                  <span className="text-xs text-muted-foreground">Positivos</span>
                  <span className="text-xs font-semibold text-foreground">{positivePercentage.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div className="bg-orange-400 h-2 rounded-full" style={{ width: `${positivePercentage}%` }}></div>
                </div>
              </div>

              <div className="pt-3 border-t border-border">
                <div className="text-center">
                  <p className="text-2xl font-bold text-primary">{statistics.positive_cases}</p>
                  <p className="text-[10px] text-muted-foreground mt-0.5">Detecciones Tempranas</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-primary to-primary/80 rounded-lg p-4 text-primary-foreground">
            <h3 className="text-sm font-semibold mb-1">Modelo YOLO v8</h3>
            <p className="text-[10px] text-primary-foreground/80 mb-3">
              Entrenado con 50,000+ imágenes médicas validadas
            </p>
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-white/10 rounded p-2 backdrop-blur">
                <p className="text-lg font-bold">96.2%</p>
                <p className="text-[10px] text-primary-foreground/80">Sensibilidad</p>
              </div>
              <div className="bg-white/10 rounded p-2 backdrop-blur">
                <p className="text-lg font-bold">94.8%</p>
                <p className="text-[10px] text-primary-foreground/80">Especificidad</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-4 bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
        <div className="flex items-start space-x-2">
          <div className="w-8 h-8 bg-blue-500/20 rounded flex items-center justify-center flex-shrink-0">
            <Download className="w-4 h-4 text-blue-400" />
          </div>
          <div>
            <h4 className="font-semibold text-xs text-foreground mb-1">Generación de Reportes</h4>
            <p className="text-[10px] text-muted-foreground mb-2">
              Los reportes pueden exportarse en formato PDF e incluyen todos los datos estadísticos,
              gráficos y detalles de los casos analizados durante el período seleccionado.
            </p>
            <button className="text-[10px] font-semibold text-primary hover:text-primary/80 underline">
              Configurar reporte personalizado
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
