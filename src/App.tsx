import { useEffect, useState } from 'react';
import Header, { type Section } from './components/Header';
import Home from './components/Home';
import ImageUpload from './components/ImageUpload';
import CaseManagement from './components/CaseManagement';
import Reports from './components/Reports';
import UserPanel from './components/UserPanel';
import AdminPanel from './components/AdminPanel';
import Login from './components/Login';
import Footer from './components/Footer';
import { apiClient } from './services/api';
import type { Me } from './types';

function App() {
  const [currentSection, setCurrentSection] = useState<Section>('home');
  const [me, setMe] = useState<Me | null>(null);
  const [isLoading, setIsLoading] = useState(true);

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

  if (!me) {
    return <Login onLogin={loadMe} />;
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Header currentSection={currentSection} onSectionChange={setCurrentSection} me={me} />
      <main className="flex-grow">
        {currentSection === 'home' && <Home onGetStarted={() => setCurrentSection('cases')} />}
        {currentSection === 'upload' && <ImageUpload />}
        {currentSection === 'cases' && <CaseManagement me={me} />}
        {currentSection === 'reports' && <Reports />}
        {currentSection === 'panel' && (me.role === 'ADMIN' ? <AdminPanel /> : <UserPanel />)}
      </main>
      <Footer />
    </div>
  );
}

export default App;
