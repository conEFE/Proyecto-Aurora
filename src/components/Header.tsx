import { Activity, Upload, FolderOpen, FileText, LogOut, User, Settings } from 'lucide-react';
import { apiClient } from '../services/api';

type Section = 'home' | 'upload' | 'cases' | 'reports' | 'panel';

interface HeaderProps {
  currentSection: Section;
  onSectionChange: (section: Section) => void;
  userRole: string;
}

export default function Header({ currentSection, onSectionChange, userRole }: HeaderProps) {
  const isAdmin = userRole === 'ADMIN';
  
  const navItems = [
    { id: 'home' as Section, label: 'Inicio', icon: Activity },
    { id: 'upload' as Section, label: 'Análisis', icon: Upload },
    { id: 'cases' as Section, label: 'Casos', icon: FolderOpen },
    { id: 'reports' as Section, label: 'Reportes', icon: FileText },
    { 
      id: 'panel' as Section, 
      label: isAdmin ? 'Admin' : 'Mi Panel', 
      icon: isAdmin ? Settings : User 
    },
  ];

  return (
    <header className="sticky top-0 z-50 bg-card/80 backdrop-blur-md border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-12">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <Activity className="w-4 h-4 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-sm font-semibold text-foreground leading-tight">
                {isAdmin ? 'Panel de Administración' : 'Panel de Usuario'}
              </h1>
              <p className="text-[10px] text-muted-foreground">Sistema IA YOLO</p>
            </div>
          </div>

          <button
            onClick={() => {
              apiClient.setToken(null);
              window.location.reload();
            }}
            className="flex items-center space-x-1 px-2 py-1 text-xs text-muted-foreground hover:text-foreground hover:bg-accent rounded transition-colors"
          >
            <LogOut className="w-3 h-3" />
            <span className="hidden sm:inline">Salir</span>
          </button>
        </div>

        <nav className="flex space-x-1 pb-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentSection === item.id;

            return (
              <button
                key={item.id}
                onClick={() => onSectionChange(item.id)}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
