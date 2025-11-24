import { useState, useEffect } from 'react';
import { Users, UserPlus, Settings, Shield, BarChart3, Activity, Loader2, AlertCircle } from 'lucide-react';
import { apiClient } from '../services/api';

interface SystemStats {
  total_users: number;
  total_cases: number;
  total_patients: number;
  active_sessions: number;
}

interface RecentUser {
  id: number;
  rut: string;
  email: string;
  role: string;
  created_at: string;
}

export default function AdminPanel() {
  const [stats, setStats] = useState<SystemStats>({
    total_users: 0,
    total_cases: 0,
    total_patients: 0,
    active_sessions: 0,
  });
  const [recentUsers, setRecentUsers] = useState<RecentUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Cargar estadísticas del sistema
      const statsResponse = await apiClient.getAdminStats();
      if (statsResponse.data) {
        setStats(statsResponse.data);
      }

      // Cargar usuarios recientes
      const usersResponse = await apiClient.getRecentUsers();
      if (usersResponse.data) {
        setRecentUsers(usersResponse.data);
      }
    } catch (err) {
      setError('Error al cargar datos de administración');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      </div>
    );
  }

  const statCards = [
    {
      label: 'Total Usuarios',
      value: stats.total_users,
      icon: Users,
      color: 'blue',
    },
    {
      label: 'Total Casos',
      value: stats.total_cases,
      icon: Activity,
      color: 'pink',
    },
    {
      label: 'Total Pacientes',
      value: stats.total_patients,
      icon: UserPlus,
      color: 'green',
    },
    {
      label: 'Sesiones Activas',
      value: stats.active_sessions,
      icon: BarChart3,
      color: 'orange',
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      <div className="mb-4">
        <h2 className="text-lg font-bold text-foreground">Panel de Administración</h2>
        <p className="mt-0.5 text-xs text-muted-foreground">
          Gestión del sistema, usuarios y configuración
        </p>
      </div>

      {error && (
        <div className="mb-3 bg-destructive/10 border border-destructive/20 text-destructive-foreground px-3 py-2 rounded text-xs">
          {error}
        </div>
      )}

      {/* Estadísticas */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          const colorClasses = {
            blue: 'bg-blue-500/10 text-blue-400',
            pink: 'bg-primary/10 text-primary',
            green: 'bg-green-500/10 text-green-400',
            orange: 'bg-orange-500/10 text-orange-400',
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
              <p className="text-xl font-bold text-foreground">{stat.value.toLocaleString()}</p>
              <p className="text-[10px] text-muted-foreground mt-0.5">{stat.label}</p>
            </div>
          );
        })}
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        {/* Gestión de Usuarios */}
        <div className="lg:col-span-2 bg-card border border-border rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-foreground">Gestión de Usuarios</h3>
            <Shield className="w-4 h-4 text-primary" />
          </div>

          <div className="space-y-2 mb-3">
            <button className="w-full px-3 py-2 bg-primary hover:bg-primary/90 text-primary-foreground rounded text-xs font-semibold transition-colors">
              Crear Nuevo Usuario
            </button>
            <button className="w-full px-3 py-2 bg-secondary hover:bg-secondary/80 text-foreground rounded text-xs font-medium transition-colors">
              Ver Todos los Usuarios
            </button>
          </div>

          <div className="border-t border-border pt-3">
            <h4 className="text-xs font-semibold text-foreground mb-2">Usuarios Recientes</h4>
            {recentUsers.length > 0 ? (
              <div className="space-y-2">
                {recentUsers.map((user) => (
                  <div
                    key={user.id}
                    className="p-2 bg-secondary/30 border border-border rounded text-xs"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-foreground">{user.email}</p>
                        <p className="text-[10px] text-muted-foreground">RUT: {user.rut} • {user.role}</p>
                      </div>
                      <span className="px-2 py-0.5 bg-primary/10 text-primary text-[10px] font-semibold rounded">
                        {user.role}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-muted-foreground">No hay usuarios recientes</p>
            )}
          </div>
        </div>

        {/* Acciones Rápidas */}
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="text-sm font-semibold text-foreground mb-3">Acciones Rápidas</h3>
            <div className="space-y-2">
              <button className="w-full px-3 py-2 bg-secondary hover:bg-secondary/80 text-foreground rounded text-xs font-medium transition-colors text-left">
                <Settings className="w-3.5 h-3.5 inline mr-2" />
                Configuración del Sistema
              </button>
              <button className="w-full px-3 py-2 bg-secondary hover:bg-secondary/80 text-foreground rounded text-xs font-medium transition-colors text-left">
                <BarChart3 className="w-3.5 h-3.5 inline mr-2" />
                Ver Reportes Completos
              </button>
              <button className="w-full px-3 py-2 bg-secondary hover:bg-secondary/80 text-foreground rounded text-xs font-medium transition-colors text-left">
                <Shield className="w-3.5 h-3.5 inline mr-2" />
                Gestión de Permisos
              </button>
            </div>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="text-sm font-semibold text-foreground mb-3">Estado del Sistema</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground">Base de Datos</span>
                <span className="text-green-400 font-semibold">● Activa</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground">API</span>
                <span className="text-green-400 font-semibold">● Operativa</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground">Modelo YOLO</span>
                <span className="text-green-400 font-semibold">● Disponible</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
