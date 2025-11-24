import { ArrowRight, Shield, Zap, CheckCircle } from 'lucide-react';
import logoAurora from '../assets/logo-aurora.png';

interface HomeProps {
  onGetStarted: () => void;
}

export default function Home({ onGetStarted }: HomeProps) {
  const features = [
    {
      icon: Zap,
      title: 'Detección Temprana',
      description: 'Análisis rápido y preciso mediante algoritmos YOLO',
    },
    {
      icon: Shield,
      title: 'Seguridad Garantizada',
      description: 'Protección de datos médicos con estándares HIPAA',
    },
    {
      icon: CheckCircle,
      title: 'Alta Precisión',
      description: 'Modelo entrenado con miles de imágenes validadas',
    },
  ];

  return (
    <div className="bg-background min-h-[calc(100vh-4rem)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid lg:grid-cols-2 gap-6 items-center">
          <div className="space-y-4">
            <div className="space-y-2">
              <h3 className="text-sm font-bold text-foreground leading-tight">
                Sistema de Apoyo Diagnóstico con{' '}
                <span className="text-primary">Inteligencia Artificial</span>
              </h3>
              <p className="text-xs text-muted-foreground">
                Plataforma basada en IA para la detección temprana de cáncer de mama mediante análisis automatizado de imágenes médicas.
              </p>
            </div>

            <div className="flex gap-2">
              <button
                onClick={onGetStarted}
                className="flex items-center space-x-1.5 bg-primary hover:bg-primary/90 text-primary-foreground px-4 py-2 rounded text-xs font-semibold transition-colors"
              >
                <span>Ingresar al Sistema</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="pt-4 border-t border-border">
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-lg font-bold text-primary">92%</p>
                  <p className="text-[10px] text-muted-foreground">Precisión</p>
                </div>
                <div>
                  <p className="text-lg font-bold text-primary">1,200+</p>
                  <p className="text-[10px] text-muted-foreground">Casos</p>
                </div>
                <div>
                  <p className="text-lg font-bold text-primary">&lt;3s</p>
                  <p className="text-[10px] text-muted-foreground">Tiempo</p>
                </div>
              </div>
            </div>
          </div>

          {/* Logo grande a la derecha */}
          <div className="flex flex-col items-center justify-center">
            <img 
              src={logoAurora} 
              alt="Proyecto Aurora" 
              className="h-64 w-auto mb-4"
            />
            <h1 className="text-xl font-bold text-foreground mb-2">
              PROYECTO AURORA
            </h1>
            <h2 className="text-base font-semibold text-foreground mb-2 text-center">
              Detección Temprana de Cáncer de Mama
            </h2>
            <p className="text-xs text-muted-foreground text-center max-w-md">
              Sistema de inteligencia artificial basado en YOLO para análisis automatizado de imágenes médicas con precisión superior al 90%.
            </p>
          </div>
        </div>

        <div className="mt-6 grid md:grid-cols-3 gap-4">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={index}
                className="bg-card border border-border p-4 rounded-lg"
              >
                <div className="w-8 h-8 bg-primary/10 rounded flex items-center justify-center mb-2">
                  <Icon className="w-4 h-4 text-primary" />
                </div>
                <h3 className="text-sm font-semibold text-foreground mb-1">{feature.title}</h3>
                <p className="text-xs text-muted-foreground">{feature.description}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
