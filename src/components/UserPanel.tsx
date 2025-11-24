import { useState, useEffect } from 'react';
import { User, Users, MessageSquare, Calendar, Mail, Phone, Loader2, AlertCircle } from 'lucide-react';
import { apiClient } from '../services/api';

interface UserInfo {
  id: number;
  rut: string;
  email: string;
  role: string;
}

interface Patient {
  id: number;
  rut: string;
  first_name?: string;
  last_name?: string;
  birth_date?: string;
}

interface SupportTicket {
  id: number;
  title: string;
  description: string;
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  created_at: string;
}

export default function UserPanel() {
  const [userInfo, setUserInfo] = useState<UserInfo>({
    id: 0,
    rut: 'Cargando...',
    email: 'Cargando...',
    role: 'MEDICO',
  });
  const [patients, setPatients] = useState<Patient[]>([]);
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Cargar información del usuario
      const userData = await apiClient.getUserInfo();
      console.log('getUserInfo response:', userData); // Debug
      if (userData.data) {
        setUserInfo(userData.data);
      } else {
        console.error('Error getUserInfo:', userData.error);
        // Inicializar con datos por defecto si falla
        setUserInfo({
          id: 0,
          rut: 'N/A',
          email: 'N/A',
          role: 'MEDICO',
        });
      }

      // Cargar pacientes asociados
      const patientsResponse = await apiClient.getUserPatients();
      console.log('getUserPatients response:', patientsResponse); // Debug
      if (patientsResponse.data) {
        setPatients(patientsResponse.data);
      } else {
        console.error('Error getUserPatients:', patientsResponse.error);
        setPatients([]); // Asegurar que sea un array vacío
      }

      // Cargar tickets de soporte
      const ticketsResponse = await apiClient.getSupportTickets();
      console.log('getSupportTickets response:', ticketsResponse); // Debug
      if (ticketsResponse.data) {
        setTickets(ticketsResponse.data);
      } else {
        console.error('Error getSupportTickets:', ticketsResponse.error);
        setTickets([]); // Asegurar que sea un array vacío
      }
    } catch (err) {
      console.error('Error completo en loadData:', err);
      setError('Error al cargar datos del panel');
      // Asegurar que loading se desactive incluso si hay error
      setUserInfo({
        id: 0,
        rut: 'N/A',
        email: 'N/A',
        role: 'MEDICO',
      });
      setPatients([]);
      setTickets([]);
    } finally {
      setLoading(false); // Asegurar que siempre se desactive
    }
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      open: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      in_progress: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
      resolved: 'bg-green-500/10 text-green-400 border-green-500/20',
      closed: 'bg-muted text-muted-foreground border-border',
    };

    const labels = {
      open: 'Abierto',
      in_progress: 'En Proceso',
      resolved: 'Resuelto',
      closed: 'Cerrado',
    };

    return (
      <span className={`px-2 py-0.5 text-[10px] font-semibold rounded border ${styles[status as keyof typeof styles]}`}>
        {labels[status as keyof typeof labels]}
      </span>
    );
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

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      <div className="mb-4">
        <h2 className="text-lg font-bold text-foreground">Panel de Usuario</h2>
        <p className="mt-0.5 text-xs text-muted-foreground">
          Información personal, pacientes asociados y tickets de soporte
        </p>
      </div>

      {error && (
        <div className="mb-3 bg-destructive/10 border border-destructive/20 text-destructive-foreground px-3 py-2 rounded text-xs">
          {error}
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-4">
        {/* Información del Usuario */}
        <div className="lg:col-span-1">
          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
                <User className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-foreground">Información Personal</h3>
                <p className="text-[10px] text-muted-foreground">Médico</p>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center space-x-2 text-xs">
                <Mail className="w-3.5 h-3.5 text-muted-foreground" />
                <span className="text-muted-foreground">Email:</span>
                <span className="text-foreground">{userInfo?.email ?? 'Cargando...'}</span>
              </div>
              <div className="flex items-center space-x-2 text-xs">
                <User className="w-3.5 h-3.5 text-muted-foreground" />
                <span className="text-muted-foreground">RUT:</span>
                <span className="text-foreground">{userInfo?.rut ?? 'Cargando...'}</span>
              </div>
              <div className="flex items-center space-x-2 text-xs">
                <Calendar className="w-3.5 h-3.5 text-muted-foreground" />
                <span className="text-muted-foreground">Rol:</span>
                <span className="text-foreground">{userInfo?.role ?? 'MEDICO'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Pacientes Asociados */}
        <div className="lg:col-span-1">
          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-foreground">Pacientes Asociados</h3>
              <Users className="w-4 h-4 text-primary" />
            </div>

            {patients.length > 0 ? (
              <div className="space-y-2">
                {patients.map((patient) => (
                  <div
                    key={patient.id}
                    className="p-2 bg-secondary/30 border border-border rounded text-xs"
                  >
                    <p className="font-medium text-foreground">
                      {patient.first_name || ''} {patient.last_name || ''}
                    </p>
                    <p className="text-[10px] text-muted-foreground">RUT: {patient.rut}</p>
                  </div>
                ))}
                <button className="w-full mt-2 text-xs text-primary hover:text-primary/80 font-medium">
                  Ver todos los pacientes →
                </button>
              </div>
            ) : (
              <div className="text-center py-6 text-muted-foreground">
                <Users className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-xs">No hay pacientes asociados</p>
              </div>
            )}
          </div>
        </div>

        {/* Tickets de Soporte */}
        <div className="lg:col-span-1">
          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-foreground">Tickets de Soporte</h3>
              <MessageSquare className="w-4 h-4 text-primary" />
            </div>

            {tickets.length > 0 ? (
              <div className="space-y-2">
                {tickets.map((ticket) => (
                  <div
                    key={ticket.id}
                    className="p-2 bg-secondary/30 border border-border rounded"
                  >
                    <div className="flex items-start justify-between mb-1">
                      <p className="text-xs font-medium text-foreground">{ticket.title}</p>
                      {getStatusBadge(ticket.status)}
                    </div>
                    <p className="text-[10px] text-muted-foreground line-clamp-2">
                      {ticket.description}
                    </p>
                    <p className="text-[10px] text-muted-foreground mt-1">
                      {new Date(ticket.created_at).toLocaleDateString()}
                    </p>
                  </div>
                ))}
                <button className="w-full mt-2 text-xs text-primary hover:text-primary/80 font-medium">
                  Crear nuevo ticket →
                </button>
              </div>
            ) : (
              <div className="text-center py-6 text-muted-foreground">
                <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-xs">No hay tickets</p>
                <button className="mt-2 text-xs text-primary hover:text-primary/80 font-medium">
                  Crear ticket
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
