import { useState } from 'react';
import { User, Lock, Mail, UserCircle, Loader2 } from 'lucide-react';
import { apiClient } from '../services/api';

interface SignupProps {
  onSignup: () => void;
  onBack: () => void;
}

export default function Signup({ onBack }: SignupProps) {
  const [rut, setRut] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [role, setRole] = useState('MEDICO');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Las contraseñas no coinciden');
      return;
    }

    if (password.length < 6) {
      setError('La contraseña debe tener al menos 6 caracteres');
      return;
    }

    setLoading(true);
    try {
      const response = await apiClient.signup(rut, email, password, role);
      if (response.data) {
        alert('Usuario creado exitosamente. Ahora puedes iniciar sesión.');
        onBack();
      } else {
        setError(response.error || 'Error al crear usuario');
      }
    } catch {
      setError('Error al crear usuario');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="text-center mb-6">
            <div className="inline-flex items-center justify-center w-12 h-12 bg-primary/10 rounded-lg mb-3">
              <UserCircle className="w-6 h-6 text-primary" />
            </div>
            <h2 className="text-lg font-bold text-foreground">Crear Cuenta</h2>
            <p className="mt-1 text-xs text-muted-foreground">Registra un nuevo usuario</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="rut" className="block text-xs font-medium text-foreground mb-1">
                RUT *
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
                  placeholder="12345678-9"
                  required
                />
              </div>
            </div>

            <div>
              <label htmlFor="email" className="block text-xs font-medium text-foreground mb-1">
                Email *
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-2.5 flex items-center pointer-events-none">
                  <Mail className="h-4 w-4 text-muted-foreground" />
                </div>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="block w-full pl-8 pr-3 py-2 bg-background border border-input rounded text-sm text-foreground focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder="usuario@ejemplo.com"
                  required
                />
              </div>
            </div>

            <div>
              <label htmlFor="role" className="block text-xs font-medium text-foreground mb-1">
                Rol *
              </label>
              <select
                id="role"
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="block w-full px-3 py-2 bg-background border border-input rounded text-sm text-foreground focus:ring-2 focus:ring-primary focus:border-transparent"
              >
                <option value="MEDICO">Médico</option>
                <option value="ADMIN">Administrador</option>
              </select>
            </div>

            <div>
              <label htmlFor="password" className="block text-xs font-medium text-foreground mb-1">
                Contraseña *
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
                  minLength={6}
                />
              </div>
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-xs font-medium text-foreground mb-1">
                Confirmar Contraseña *
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-2.5 flex items-center pointer-events-none">
                  <Lock className="h-4 w-4 text-muted-foreground" />
                </div>
                <input
                  id="confirmPassword"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="block w-full pl-8 pr-3 py-2 bg-background border border-input rounded text-sm text-foreground focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder="••••••••"
                  required
                  minLength={6}
                />
              </div>
            </div>

            {error && (
              <div className="bg-destructive/10 border border-destructive/20 text-destructive-foreground px-3 py-2 rounded text-xs">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center py-2 px-4 border border-transparent rounded text-sm text-primary-foreground bg-primary hover:bg-primary/90 disabled:bg-muted disabled:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary font-semibold transition-colors"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  <span>Creando cuenta...</span>
                </>
              ) : (
                'Crear Cuenta'
              )}
            </button>

            <button
              type="button"
              onClick={onBack}
              className="w-full text-center text-xs text-primary hover:text-primary/80 font-medium"
            >
              Volver al login
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}