import { useState, useEffect } from 'react';
import Header from './components/Header';
import Home from './components/Home';
import ImageUpload from './components/ImageUpload';
import CaseManagement from './components/CaseManagement';
import Reports from './components/Reports';
import UserPanel from './components/UserPanel';
import AdminPanel from './components/AdminPanel';
import Login from './components/Login';
import Footer from './components/Footer';
import Signup from './components/Signup';
import { apiClient } from './services/api';

type Section = 'home' | 'upload' | 'cases' | 'reports' | 'panel';

function App() {
  const [showSignup, setShowSignup] = useState(false);
  const [currentSection, setCurrentSection] = useState<Section>('home');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [userRole, setUserRole] = useState<string>('MEDICO');

  // Restaurar autenticación desde localStorage al cargar
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      apiClient.getMe().then((response) => {
        if (response.data) {
          setIsAuthenticated(true);
          setUserRole(response.data.role || 'MEDICO');
          setCurrentSection('home');
        } else {
          apiClient.setToken(null);
        }
        setIsLoading(false);
      }).catch(() => {
        apiClient.setToken(null);
        setIsLoading(false);
      });
    } else {
      setIsLoading(false);
    }
  }, []);

  const handleLogin = () => {
    // Obtener el rol después del login
    apiClient.getMe().then((response) => {
      if (response.data) {
        setUserRole(response.data.role || 'MEDICO');
      }
    });
    setIsAuthenticated(true);
    setCurrentSection('home');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground text-sm">Cargando...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    if (showSignup) {
      return <Signup onSignup={handleLogin} onBack={() => setShowSignup(false)} />;
    }
    return <Login onLogin={handleLogin} onSignup={() => setShowSignup(true)} />;
  }
  
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Header 
        currentSection={currentSection} 
        onSectionChange={setCurrentSection}
        userRole={userRole}
      />
      <main className="flex-grow">
        {currentSection === 'home' && <Home onGetStarted={() => setCurrentSection('upload')} />}
        {currentSection === 'upload' && <ImageUpload />}
        {currentSection === 'cases' && <CaseManagement />}
        {currentSection === 'reports' && <Reports />}
        {currentSection === 'panel' && (
          userRole === 'ADMIN' ? <AdminPanel /> : <UserPanel />
        )}
      </main>
      <Footer />
    </div>
  );
}

export default App;
