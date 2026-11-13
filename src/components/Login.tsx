import { useState } from 'react';
import { ArrowLeft, ArrowRight, Loader2, Moon, Sun } from 'lucide-react';
import { apiClient } from '../services/api';
import { useTheme } from '../lib/theme';
import { cn } from '../lib/cn';
import colaImg from '../assets/landing/cola.webp';
import BrandMark from './BrandMark';
import { ErrorMessage } from './Feedback';
import { ghostButton, iconButton, inputClass, labelClass, primaryButton } from './ui';

interface LoginProps {
  onLogin: () => void;
  /** Vuelve a la página de presentación */
  onBack?: () => void;
}

const container = 'mx-auto max-w-6xl px-4 sm:px-6';

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
    <div className="min-h-screen flex flex-col bg-background text-foreground">
      <header className="border-b border-border/70">
        <div className={cn(container, 'h-16 flex items-center justify-between gap-4')}>
          <button onClick={onBack} className="flex items-center gap-2.5 rounded-md" aria-label="Aurora Care, volver al inicio">
            <BrandMark alt="" />
            <span className="text-lg font-extrabold">Aurora Care</span>
          </button>
          <div className="flex items-center gap-1">
            {onBack && (
              <button onClick={onBack} className={cn(ghostButton, 'hidden sm:inline-flex')}>
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
      </header>

      <main className="flex-1">
        <div className={cn(container, 'py-12 sm:py-20 grid lg:grid-cols-[minmax(0,5fr)_minmax(0,7fr)] gap-12 lg:gap-16 items-center')}>
          <form onSubmit={handleSubmit} className="w-full max-w-sm mx-auto lg:mx-0 space-y-5" noValidate>
            <div>
              <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight leading-[1.05]">Ingresar</h1>
              <p className="mt-3 text-muted-foreground">Con el RUT y la contraseña que le entregó el administrador.</p>
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
                className={cn(inputClass, 'h-11')}
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
                className={cn(inputClass, 'h-11')}
                aria-invalid={error ? true : undefined}
                required
              />
            </div>

            <button type="submit" className={cn(primaryButton, 'w-full h-12 text-base')} disabled={submitting || !rut || !password}>
              {submitting ? <Loader2 aria-hidden className="w-4 h-4 animate-spin" /> : null}
              {submitting ? 'Ingresando…' : <>Ingresar <ArrowRight aria-hidden className="w-4 h-4" /></>}
            </button>

            <p className="text-sm text-muted-foreground">
              ¿Sin cuenta o la olvidó? Pídasela al administrador de su centro.
            </p>
          </form>

          <div aria-hidden className="hidden lg:block relative">
            <div className="absolute -inset-x-6 top-10 -bottom-6 rounded-3xl bg-muted border border-border" />
            <div className="relative rounded-2xl border border-border bg-card overflow-hidden shadow-[0_30px_60px_-30px_hsl(var(--shadow)/0.35)]">
              <div className="h-9 flex items-center gap-2 px-4 border-b border-border">
                <span className="w-2.5 h-2.5 rounded-full bg-border" />
                <span className="w-2.5 h-2.5 rounded-full bg-border" />
                <span className="w-2.5 h-2.5 rounded-full bg-border" />
                <span className="ml-3 text-xs text-muted-foreground">Cola de triage</span>
              </div>
              <img src={colaImg} alt="" className="block w-full h-auto" />
            </div>
            <p className="relative mt-10 px-2 text-2xl font-extrabold tracking-tight">Los casos urgentes, primero.</p>
          </div>
        </div>
      </main>

      <footer className="border-t border-border">
        <div className={cn(container, 'py-8 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-sm text-muted-foreground')}>
          <div className="flex items-center gap-2">
            <BrandMark alt="" />
            <span className="font-bold text-foreground">Aurora Care</span>
            <span>© 2026</span>
          </div>
          <p>Apoya, no reemplaza, el criterio médico.</p>
        </div>
      </footer>
    </div>
  );
}
