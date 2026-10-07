import { useState } from 'react';
import { Lock, User, Activity, Shield } from 'lucide-react';
import { apiClient } from '../services/api';

interface LoginProps {
  onLogin: () => void;
  onSignup?: () => void;
}

export default function Login({ onLogin, onSignup }: LoginProps) {
  const [rut, setRut] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const response = await apiClient.login(rut, password);
    
    if (response.data && response.data.access_token) {
      apiClient.setToken(response.data.access_token);
      onLogin();
    } else {
      alert(response.error || 'Error al iniciar sesión');
    }
  };

  return (
    <div className="min-h-screen bg-background flex">
      <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full">
          <div className="bg-card border border-border rounded-lg p-6">
            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-primary rounded-lg mb-3">
                <Activity className="w-6 h-6 text-primary-foreground" />
              </div>
              <h2 className="text-lg font-bold text-foreground">Bienvenido</h2>
              <p className="mt-1 text-xs text-muted-foreground">
                Plataforma de Apoyo Diagnóstico Oncológico
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="rut" className="block text-xs font-medium text-foreground mb-1">
                  Usuario
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-2.5 flex items-center pointer-events-none">
                    <User className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <input
                    id="rut"
                    type="text"
                    value={rut}
                    onChange={(e) => setRut(e.target.value)}
                    className="block w-full pl-8 pr-3 py-2 bg-background border border-input rounded text-sm text-foreground focus:ring-2 focus:ring-primary focus:border-transparent"
                    placeholder="Ingrese su RUT"
                    required
                  />
                </div>
              </div>

              <div>
                <label htmlFor="password" className="block text-xs font-medium text-foreground mb-1">
                  Contraseña
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-2.5 flex items-center pointer-events-none">
                    <Lock className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="block w-full pl-8 pr-3 py-2 bg-background border border-input rounded text-sm text-foreground focus:ring-2 focus:ring-primary focus:border-transparent"
                    placeholder="••••••••"
                    required
                  />
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <input
                    id="remember-me"
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="h-3.5 w-3.5 text-primary focus:ring-primary border-input rounded"
                  />
                  <label htmlFor="remember-me" className="ml-1.5 block text-xs text-muted-foreground">
                    Recordarme
                  </label>
                </div>
                <button
                  type="button"
                  className="text-xs font-medium text-primary hover:text-primary/80"
                >
                  ¿Olvidó su contraseña?
                </button>
              </div>

              <button
                type="submit"
                className="w-full flex items-center justify-center py-2 px-4 border border-transparent rounded text-sm text-primary-foreground bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary font-semibold transition-colors"
              >
                Iniciar Sesión Seguro
              </button>
              <button
                type="button"
                onClick={() => onSignup?.()}
                className="w-full mt-2 text-center text-xs text-primary hover:text-primary/80 font-medium"
              >
                ¿No tienes cuenta? Crear una
              </button>
            </form>

            <div className="mt-4 pt-4 border-t border-border">
              <div className="flex items-center justify-center space-x-1.5 text-[10px] text-muted-foreground">
                <Shield className="w-3 h-3 text-green-400" />
                <span>Conexión segura con encriptación SSL</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="hidden lg:flex lg:flex-1 bg-gradient-to-br from-primary/20 to-primary/10 items-center justify-center p-8">
        <div className="max-w-lg text-foreground space-y-6">
          <div>
            <h1 className="text-2xl font-bold mb-2">
              Detección Temprana de Cáncer de Mama
            </h1>
            <p className="text-sm text-muted-foreground">
              Sistema de inteligencia artificial basado en YOLO para análisis automatizado de
              imágenes médicas con precisión superior al 90%.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
