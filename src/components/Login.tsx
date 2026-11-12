import { useState } from 'react';
import { ArrowLeft, Loader2, Moon, Sun } from 'lucide-react';
import { apiClient } from '../services/api';
import { useTheme } from '../lib/theme';
import BrandMark from './BrandMark';
import { ErrorMessage } from './Feedback';
import { ghostButton, iconButton, inputClass, labelClass, primaryButton } from './ui';

interface LoginProps {
  onLogin: () => void;
  /** Vuelve a la página de presentación */
  onBack?: () => void;
}

export default function Login({ onLogin, onBack }: LoginProps) {
  const [rut, setRut] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const { theme, toggleTheme } = useTheme();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    const response = await apiClient.login(rut, password);
    setSubmitting(false);

    if (response.data && response.data.access_token) {
      apiClient.setToken(response.data.access_token);
      onLogin();
    } else {
      setError(response.error || 'No se pudo iniciar sesión. Revise su RUT y contraseña.');
    }
  };

  return (
    <div className="min-h-screen bg-background grid lg:grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)]">
      <div className="flex flex-col px-6 sm:px-12 py-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <BrandMark />
            <span className="text-base font-extrabold">Aurora Care</span>
          </div>
          <div className="flex items-center gap-1">
          {onBack && (
            <button onClick={onBack} className={ghostButton}>
              <ArrowLeft aria-hidden className="w-4 h-4" /> Volver al inicio
            </button>
          )}
          <button
            onClick={toggleTheme}
            className={iconButton}
            aria-label={theme === 'dark' ? 'Usar tema claro' : 'Usar tema oscuro'}
          >
            {theme === 'dark' ? <Sun className="w-[18px] h-[18px]" /> : <Moon className="w-[18px] h-[18px]" />}
          </button>
          </div>
        </div>

        <div className="flex-1 flex items-center">
          <form onSubmit={handleSubmit} className="w-full max-w-sm mx-auto lg:mx-0 lg:ml-[12%] space-y-5" noValidate>
            <div>
              <h1 className="text-3xl font-extrabold">Iniciar sesión</h1>
              <p className="mt-2 text-sm text-muted-foreground">Ingrese con el RUT y la contraseña que le entregó el administrador.</p>
            </div>

            <ErrorMessage>{error}</ErrorMessage>

            <div>
              <label htmlFor="rut" className={labelClass}>RUT</label>
              <input
                id="rut"
                type="text"
                inputMode="text"
                autoComplete="username"
                value={rut}
                onChange={(e) => setRut(e.target.value)}
                className={inputClass}
                placeholder="12.345.678-9"
                aria-invalid={error ? true : undefined}
                required
              />
            </div>

            <div>
              <label htmlFor="password" className={labelClass}>Contraseña</label>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={inputClass}
                aria-invalid={error ? true : undefined}
                required
              />
            </div>

            <button type="submit" className={`${primaryButton} w-full h-11`} disabled={submitting || !rut || !password}>
              {submitting && <Loader2 aria-hidden className="w-4 h-4 animate-spin" />}
              {submitting ? 'Ingresando…' : 'Ingresar'}
            </button>

            <p className="text-xs text-muted-foreground">
              ¿Sin cuenta o la olvidó? Pídasela al administrador de su centro.
            </p>
          </form>
        </div>

      </div>

      <div className="hidden lg:flex items-center justify-center bg-sidebar border-l border-border px-14 py-12">
        <div className="max-w-sm text-center">
          <BrandMark alt="Aurora Care" size="lg" className="w-72 h-48 mx-auto" />
          <p className="mt-6 text-3xl font-extrabold tracking-tight">Aurora Care</p>
          <p className="mt-3 text-sm text-muted-foreground">
            Los casos urgentes, primero.
          </p>
        </div>
      </div>
    </div>
  );
}
