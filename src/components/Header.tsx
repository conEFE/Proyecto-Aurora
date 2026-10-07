import {
  Activity,
  Upload,
  FolderOpen,
  FileText,
  ListOrdered,
  LogOut,
  User,
  Settings,
  SlidersHorizontal,
  type LucideIcon,
} from 'lucide-react';
import { apiClient } from '../services/api';
import type { Me, Role } from '../types';
import { ROLE_LABELS } from '../types';
import NotificationBell from './NotificationBell';

export type Section = 'home' | 'queue' | 'upload' | 'cases' | 'reports' | 'config' | 'panel';

interface HeaderProps {
  currentSection: Section;
  onSectionChange: (section: Section) => void;
  onOpenCase: (caseId: number) => void;
  me: Me;
}

interface NavItem {
  id: Section;
  label: string;
  icon: LucideIcon;
  roles: Role[];
}

const CLINICAL: Role[] = ['MEDICO', 'ADMINISTRATIVO'];

const NAV_ITEMS: NavItem[] = [
  { id: 'home', label: 'Inicio', icon: Activity, roles: CLINICAL },
  { id: 'queue', label: 'Cola de triage', icon: ListOrdered, roles: CLINICAL },
  { id: 'cases', label: 'Casos', icon: FolderOpen, roles: CLINICAL },
  { id: 'upload', label: 'Imágenes', icon: Upload, roles: CLINICAL },
  { id: 'reports', label: 'Reportes', icon: FileText, roles: ['MEDICO'] },
  { id: 'config', label: 'Parámetros', icon: SlidersHorizontal, roles: ['MEDICO', 'ADMIN'] },
  { id: 'panel', label: 'Mi panel', icon: User, roles: CLINICAL },
  { id: 'panel', label: 'Administración', icon: Settings, roles: ['ADMIN'] },
];

export default function Header({ currentSection, onSectionChange, onOpenCase, me }: HeaderProps) {
  const navItems = NAV_ITEMS.filter((item) => item.roles.includes(me.role));

  return (
    <header className="sticky top-0 z-50 bg-card/80 backdrop-blur-md border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-12">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <Activity className="w-4 h-4 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-sm font-semibold text-foreground leading-tight">Proyecto Aurora</h1>
              <p className="text-[10px] text-muted-foreground">
                {me.full_name} · {ROLE_LABELS[me.role]}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1">
          {me.role === 'MEDICO' && <NotificationBell onOpenCase={onOpenCase} />}
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
        </div>

        <nav className="flex space-x-1 pb-1 overflow-x-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentSection === item.id;
            return (
              <button
                key={`${item.id}-${item.label}`}
                onClick={() => onSectionChange(item.id)}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded text-xs font-medium transition-colors whitespace-nowrap ${
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
