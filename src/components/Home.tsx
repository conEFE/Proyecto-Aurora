import { ArrowRight, ListOrdered, ShieldCheck, Stethoscope } from 'lucide-react';
import logoAurora from '../assets/logo-aurora.png';

interface HomeProps {
  onGetStarted: () => void;
}

const FEATURES = [
  {
    icon: ListOrdered,
    title: 'Priorización de casos',
    description: 'Triage por reglas y puntaje ponderado, con el desglose de cada factor a la vista del médico.',
  },
  {
    icon: ShieldCheck,
    title: 'Datos protegidos',
    description: 'Imágenes cifradas, acceso por rol, consentimiento registrado y bitácora de auditoría (Ley 19.628).',
  },
  {
    icon: Stethoscope,
    title: 'El médico decide',
    description: 'La plataforma apoya, no reemplaza, el criterio clínico. Todo nivel puede corregirse con motivo.',
  },
];

export default function Home({ onGetStarted }: HomeProps) {
  return (
    <div className="bg-background min-h-[calc(100vh-4rem)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid lg:grid-cols-2 gap-6 items-center">
          <div className="space-y-4">
            <h3 className="text-base font-bold text-foreground leading-tight">
              Detección temprana y priorización de casos sospechosos de{' '}
              <span className="text-primary">cáncer de mama</span>
            </h3>
            <p className="text-xs text-muted-foreground">
              Registre pacientes y casos, cargue imágenes y trabaje sobre una cola priorizada. El análisis de
              imágenes funciona hoy con un proveedor <strong className="text-amber-300">simulado</strong>: sus
              resultados se marcan como «IA SIMULADA» y no tienen valor clínico.
            </p>
            <button
              onClick={onGetStarted}
              className="flex items-center space-x-1.5 bg-primary hover:bg-primary/90 text-primary-foreground px-4 py-2 rounded text-xs font-semibold transition-colors"
            >
              <span>Ir a los casos</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="flex flex-col items-center justify-center">
            <img src={logoAurora} alt="Proyecto Aurora" className="h-56 w-auto mb-4" />
            <h1 className="text-xl font-bold text-foreground mb-1">PROYECTO AURORA</h1>
            <p className="text-xs text-muted-foreground text-center max-w-md">
              Plataforma de apoyo a la detección temprana y triage. Proyecto de título — INACAP.
            </p>
          </div>
        </div>

        <div className="mt-6 grid md:grid-cols-3 gap-4">
          {FEATURES.map(({ icon: Icon, title, description }) => (
            <div key={title} className="bg-card border border-border p-4 rounded-lg">
              <div className="w-8 h-8 bg-primary/10 rounded flex items-center justify-center mb-2">
                <Icon className="w-4 h-4 text-primary" />
              </div>
              <h3 className="text-sm font-semibold text-foreground mb-1">{title}</h3>
              <p className="text-xs text-muted-foreground">{description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
