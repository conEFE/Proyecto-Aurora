import { useEffect, useRef, useState } from 'react';
import { Navigate, Route, Routes, useLocation, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import Header, { type Section } from './components/Header';
import Home from './components/Home';
import PatientsPanel from './components/PatientsPanel';
import CaseManagement from './components/CaseManagement';
import Dashboard from './components/Dashboard';
import AdminPanel from './components/AdminPanel';
import Landing from './components/Landing';
import Login from './components/Login';
import TriageQueue from './components/TriageQueue';
import TriageConfigPanel from './components/TriageConfigPanel';
import { Loading } from './components/Feedback';
import ChangePassword from './components/ChangePassword';
import PrivacyPanel from './components/PrivacyPanel';
import Profile from './components/Profile';
import { apiClient } from './services/api';
import type { Me, Patient, Role } from './types';

/** Dirección de cada sección del menú. */
const SECTION_PATHS: Record<Section, string> = {
  home: '/inicio',
  queue: '/cola',
  patients: '/pacientes',
  cases: '/casos',
  dashboard: '/dashboard',
  config: '/parametros',
  privacy: '/privacidad',
  panel: '/administracion',
  profile: '/perfil',
};

const CLINICAL: Role[] = ['MEDICO', 'ADMINISTRATIVO'];
const SECTION_ROLES: Record<Section, Role[]> = {
  home: CLINICAL,
  queue: CLINICAL,
  patients: CLINICAL,
  cases: CLINICAL,
  dashboard: ['MEDICO', 'ADMINISTRATIVO', 'ADMIN'],
  config: ['MEDICO', 'ADMIN'],
  privacy: CLINICAL,
  panel: ['ADMIN'],
  profile: ['MEDICO', 'ADMINISTRATIVO', 'ADMIN'],
};

const TITLES: Record<Section, string> = {
  home: 'Inicio',
  queue: 'Cola de triage',
  patients: 'Pacientes',
  cases: 'Casos',
  dashboard: 'Dashboard',
  config: 'Parámetros',
  privacy: 'Privacidad',
  panel: 'Administración',
  profile: 'Mi perfil',
};

function homePath(me: Me): string {
  return me.role === 'ADMIN' ? SECTION_PATHS.panel : SECTION_PATHS.home;
}

function sectionOf(pathname: string): Section | null {
  const first = '/' + (pathname.split('/')[1] ?? '');
  const entry = (Object.entries(SECTION_PATHS) as Array<[Section, string]>).find(([, p]) => p === first);
  return entry ? entry[0] : null;
}

/** Solo deja entrar a una sección si el rol la tiene; si no, a su inicio. */
function Guard({ me, section, children }: { me: Me; section: Section; children: JSX.Element }) {
  return SECTION_ROLES[section].includes(me.role) ? children : <Navigate to={homePath(me)} replace />;
}

function CasesRoute({ me, creating = false }: { me: Me; creating?: boolean }) {
  const { ref } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const statePatient = (location.state as { patient?: Patient } | null)?.patient ?? null;
  // La paciente elegida también va en la dirección (?paciente=<id>), para no perderla al recargar
  const [searchParams] = useSearchParams();
  const paramId = creating ? Number(searchParams.get('paciente')) || null : null;
  const [loaded, setLoaded] = useState<Patient | null | undefined>(undefined);
  useEffect(() => {
    if (!paramId || statePatient?.id === paramId) return;
    let active = true;
    apiClient.getPatient(paramId).then((r) => active && setLoaded(r.data ?? null));
    return () => {
      active = false;
    };
  }, [paramId, statePatient?.id]);
  const patient = statePatient ?? loaded ?? null;
  if (paramId && !statePatient && loaded === undefined) return <Loading label="Cargando paciente…" />;
  return (
    <CaseManagement
      key={creating ? `nuevo-${patient?.id ?? ''}` : ref ?? 'lista'}
      me={me}
      caseRef={ref ?? null}
      creating={creating}
      newCasePatient={patient}
      onOpenCase={(r, replace) => navigate(`/casos/${r}`, { replace })}
      onNewCase={() => navigate('/casos/nuevo')}
      onBack={() => navigate('/casos')}
    />
  );
}

function PatientsRoute({ onOpenCase }: { onOpenCase: (caseId: number) => void }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const patientId = id && /^\d+$/.test(id) ? Number(id) : null;
  return (
    <PatientsPanel
      patientId={patientId}
      onOpenPatient={(pid) => navigate(`/pacientes/${pid}`)}
      onBack={() => navigate('/pacientes')}
      onOpenCase={onOpenCase}
      onNewCase={(p) => navigate(`/casos/nuevo?paciente=${p.id}`, { state: { patient: p } })}
    />
  );
}

function PrivacyRoute({ me }: { me: Me }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const patientId = id && /^\d+$/.test(id) ? Number(id) : null;
  // Al volver, se recuperan la vista y los filtros con que se abrió la ficha
  const back = (location.state as { back?: string } | null)?.back ?? '';
  return (
    <PrivacyPanel
      me={me}
      patientId={patientId}
      onOpenPatient={(pid) => navigate(`/privacidad/pacientes/${pid}`, { state: { back: location.search } })}
      onBack={() => navigate(`/privacidad${back}`)}
    />
  );
}

function AdminRoute({ me }: { me: Me }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const userId = id && /^\d+$/.test(id) ? Number(id) : null;
  return (
    <AdminPanel
      meId={me.id}
      userId={userId}
      onOpenUser={(uid) => navigate(`/administracion/usuarios/${uid}`)}
      onBack={() => navigate('/administracion')}
    />
  );
}

function App() {
  const [me, setMe] = useState<Me | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();
  const mainRef = useRef<HTMLElement>(null);
  const firstRender = useRef(true);
  const section = sectionOf(location.pathname);

  const openCase = (caseId: number) => navigate(`/casos/${caseId}`);

  const loadMe = async (redirectTo?: string) => {
    const response = await apiClient.getMe();
    if (response.data) {
      setMe(response.data);
      if (redirectTo) navigate(redirectTo, { replace: true });
    } else {
      apiClient.setToken(null);
      setMe(null);
    }
    setIsLoading(false);
  };

  useEffect(() => {
    // Enlaces antiguos: /#ingresar
    if (window.location.hash === '#ingresar') navigate('/ingresar', { replace: true });
    if (localStorage.getItem('auth_token')) loadMe();
    else setIsLoading(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Título de la pestaña y foco en el contenido al cambiar de pantalla (para lectores de pantalla)
  useEffect(() => {
    document.title = section ? `${TITLES[section]} · Aurora Care` : 'Aurora Care';
    if (firstRender.current) {
      firstRender.current = false;
      return;
    }
    mainRef.current?.focus();
  }, [location.pathname, section]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loading label="Cargando Aurora Care…" />
      </div>
    );
  }

  if (!me) {
    const from = (location.state as { from?: string } | null)?.from;
    return (
      <Routes>
        <Route path="/" element={<Landing onLogin={() => navigate('/ingresar')} />} />
        <Route
          path="/ingresar"
          element={<Login onLogin={() => loadMe(from && from !== '/ingresar' ? from : undefined)} onBack={() => navigate('/')} />}
        />
        {/* Cualquier otra dirección pide iniciar sesión y vuelve ahí después */}
        <Route path="*" element={<Navigate to="/ingresar" replace state={{ from: location.pathname }} />} />
      </Routes>
    );
  }

  if (me.must_change_password) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center px-4 py-10">
        <ChangePassword forced onDone={() => loadMe()} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background lg:flex">
      <Header
        currentSection={section ?? (me.role === 'ADMIN' ? 'panel' : 'home')}
        onSectionChange={(s) => navigate(SECTION_PATHS[s])}
        onOpenCase={openCase}
        me={me}
      />
      <main ref={mainRef} tabIndex={-1} className="flex-1 min-w-0 focus:outline-none">
        <Routes>
          <Route path="/inicio" element={<Guard me={me} section="home"><Home me={me} onGetStarted={() => navigate('/cola')} /></Guard>} />
          <Route path="/cola" element={<Guard me={me} section="queue"><TriageQueue me={me} onOpenCase={openCase} /></Guard>} />
          <Route path="/pacientes" element={<Guard me={me} section="patients"><PatientsRoute onOpenCase={openCase} /></Guard>} />
          <Route path="/pacientes/:id" element={<Guard me={me} section="patients"><PatientsRoute onOpenCase={openCase} /></Guard>} />
          <Route path="/casos" element={<Guard me={me} section="cases"><CasesRoute me={me} /></Guard>} />
          <Route path="/casos/nuevo" element={<Guard me={me} section="cases"><CasesRoute me={me} creating /></Guard>} />
          <Route path="/casos/:ref" element={<Guard me={me} section="cases"><CasesRoute me={me} /></Guard>} />
          <Route path="/dashboard" element={<Guard me={me} section="dashboard"><Dashboard me={me} /></Guard>} />
          <Route path="/parametros" element={<Guard me={me} section="config"><TriageConfigPanel me={me} /></Guard>} />
          <Route path="/privacidad" element={<Guard me={me} section="privacy"><PrivacyRoute me={me} /></Guard>} />
          <Route path="/privacidad/pacientes/:id" element={<Guard me={me} section="privacy"><PrivacyRoute me={me} /></Guard>} />
          <Route path="/perfil" element={<Guard me={me} section="profile"><Profile me={me} onUpdated={setMe} /></Guard>} />
          <Route path="/administracion" element={<Guard me={me} section="panel"><AdminRoute me={me} /></Guard>} />
          <Route path="/administracion/usuarios/:id" element={<Guard me={me} section="panel"><AdminRoute me={me} /></Guard>} />
          <Route path="*" element={<Navigate to={homePath(me)} replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
