import { useEffect, useRef, useState } from 'react';
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
import type { Me, Patient } from './types';

function App() {
  const [currentSection, setCurrentSection] = useState<Section>('home');
  const [me, setMe] = useState<Me | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [openCaseId, setOpenCaseId] = useState<number | null>(null);
  const [openCaseNonce, setOpenCaseNonce] = useState(0);
  const [patientsNonce, setPatientsNonce] = useState(0);
  const mainRef = useRef<HTMLElement>(null);
  const firstRender = useRef(true);

  const [newCasePatient, setNewCasePatient] = useState<Patient | null>(null);
  // Sin sesión: landing pública; «Ingresar» (o el enlace /#ingresar) abre el inicio de sesión
  const [showLogin, setShowLogin] = useState(() => window.location.hash === '#ingresar');

  const openCase = (caseId: number) => {
    setOpenCaseId(caseId);
    setNewCasePatient(null);
    setOpenCaseNonce((n) => n + 1);
    setCurrentSection('cases');
  };

  // Desde Pacientes: abre «Nuevo caso» con el paciente ya elegido
  const newCaseFor = (patient: Patient) => {
    setOpenCaseId(null);
    setNewCasePatient(patient);
    setOpenCaseNonce((n) => n + 1);
    setCurrentSection('cases');
  };

  const loadMe = async () => {
    const response = await apiClient.getMe();
    if (response.data) {
      setMe(response.data);
      setCurrentSection(response.data.role === 'ADMIN' ? 'panel' : 'home');
    } else {
      apiClient.setToken(null);
      setMe(null);
    }
    setIsLoading(false);
  };

  useEffect(() => {
    if (localStorage.getItem('auth_token')) {
      loadMe();
    } else {
      setIsLoading(false);
    }
  }, []);

  // Al cambiar de sección, el foco pasa al contenido para que el lector de pantalla lo anuncie.
  useEffect(() => {
    if (firstRender.current) {
      firstRender.current = false;
      return;
    }
    mainRef.current?.focus();
  }, [currentSection]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loading label="Cargando Aurora Care…" />
      </div>
    );
  }

  if (!me) {
    if (!showLogin) {
      return (
        <Landing
          onLogin={() => {
            setShowLogin(true);
            window.scrollTo(0, 0);
          }}
        />
      );
    }
    return <Login onLogin={loadMe} onBack={() => setShowLogin(false)} />;
  }

  if (me.must_change_password) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center px-4 py-10">
        <ChangePassword forced onDone={loadMe} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background lg:flex">
      <Header
        currentSection={currentSection}
        onSectionChange={(section) => {
          setNewCasePatient(null);
          // «Casos» desde el menú siempre vuelve a la lista
          if (section === 'cases') {
            setOpenCaseId(null);
            setOpenCaseNonce((n) => n + 1);
          }
          if (section === 'patients') setPatientsNonce((n) => n + 1);
          setCurrentSection(section);
        }} onOpenCase={openCase} me={me} />
      <main ref={mainRef} tabIndex={-1} className="flex-1 min-w-0 focus:outline-none">
        {currentSection === 'home' && <Home me={me} onGetStarted={() => setCurrentSection('queue')} />}
        {currentSection === 'queue' && <TriageQueue me={me} onOpenCase={openCase} />}
        {currentSection === 'config' && <TriageConfigPanel me={me} />}
        {currentSection === 'patients' && <PatientsPanel key={patientsNonce} onOpenCase={openCase} onNewCase={newCaseFor} />}
        {currentSection === 'cases' && (
          <CaseManagement key={openCaseNonce} me={me} initialCaseId={openCaseId} newCasePatient={newCasePatient} />
        )}
        {currentSection === 'dashboard' && <Dashboard me={me} />}
        {currentSection === 'privacy' && me.role !== 'ADMIN' && <PrivacyPanel me={me} />}
        {currentSection === 'profile' && <Profile me={me} onUpdated={setMe} />}
        {currentSection === 'panel' && me.role === 'ADMIN' && <AdminPanel />}
      </main>
    </div>
  );
}

export default App;
