import {
  Activity,
  BarChart3,
  FolderOpen,
  KeyRound,
  ListOrdered,
  LogOut,
  Moon,
  Settings,
  ShieldCheck,
  SlidersHorizontal,
  Sun,
  Upload,
  type LucideIcon,
} from 'lucide-react';
import { useCallback, useState } from 'react';
import { apiClient } from '../services/api';
import { usePolling } from '../lib/usePolling';
import type { Me, Role } from '../types';
import { ROLE_LABELS } from '../types';
import { useTheme } from '../lib/theme';
import { cn } from '../lib/cn';
import BrandMark from './BrandMark';
import NotificationBell from './NotificationBell';
import ChangePassword from './ChangePassword';
import Dialog from './Dialog';
import { iconButton } from './ui';

export type Section = 'home' | 'queue' | 'upload' | 'cases' | 'dashboard' | 'config' | 'privacy' | 'panel';

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

// eslint-disable-next-line react-refresh/only-export-components
export const NAV_ITEMS: NavItem[] = [
  { id: 'home', label: 'Inicio', icon: Activity, roles: CLINICAL },
  { id: 'queue', label: 'Cola de triage', icon: ListOrdered, roles: CLINICAL },
  { id: 'cases', label: 'Casos', icon: FolderOpen, roles: CLINICAL },
  { id: 'upload', label: 'Cargar imágenes', icon: Upload, roles: CLINICAL },
  { id: 'dashboard', label: 'Dashboard', icon: BarChart3, roles: ['MEDICO', 'ADMINISTRATIVO', 'ADMIN'] },
  { id: 'config', label: 'Parámetros', icon: SlidersHorizontal, roles: ['MEDICO', 'ADMIN'] },
  { id: 'privacy', label: 'Privacidad', icon: ShieldCheck, roles: CLINICAL },
  { id: 'panel', label: 'Administración', icon: Settings, roles: ['ADMIN'] },
];

/** Barra lateral fija: marca, secciones por rol, usuario, tema y salida. */
export default function Header({ currentSection, onSectionChange, onOpenCase, me }: HeaderProps) {
  const navItems = NAV_ITEMS.filter((item) => item.roles.includes(me.role));
  const { theme, toggleTheme } = useTheme();
  const clinical = me.role !== 'ADMIN';
  const [alta, setAlta] = useState<number | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const loadAlta = useCallback(async () => {
    if (!clinical) return;
    const r = await apiClient.getQueue(true);
    if (r.data) setAlta(r.data.filter((q) => q.level === 'ALTA').length);
  }, [clinical]);
  usePolling(loadAlta, 60000);

  return (
    <aside className="lg:sticky lg:top-0 lg:h-screen w-full lg:w-[232px] shrink-0 flex flex-col bg-sidebar border-b lg:border-b-0 lg:border-r border-border">
      <div className="flex items-center justify-between gap-2 px-4 py-4">
        <div className="flex items-center gap-2.5">
          <BrandMark />
          <div className="leading-tight">
            <p className="text-base font-extrabold text-foreground">Aurora</p>
            <p className="text-xs text-muted-foreground">Triage de cáncer de mama</p>
          </div>
        </div>
      </div>

      <nav aria-label="Secciones" className="px-3 py-2 flex lg:flex-col gap-0.5 overflow-x-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentSection === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSectionChange(item.id)}
              aria-current={isActive ? 'page' : undefined}
              className={cn(
                'group flex items-center gap-3 h-10 px-3 rounded-lg text-sm whitespace-nowrap transition-colors',
                isActive
                  ? 'bg-card text-foreground font-bold ring-1 ring-border'
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent',
              )}
            >
              <Icon aria-hidden className={cn('w-[18px] h-[18px]', isActive ? 'text-brand' : '')} />
              {item.label}
              {item.id === 'queue' && alta !== null && alta > 0 && (
                <span className="ml-auto inline-flex items-center gap-1 text-xs font-extrabold text-alta" aria-label={`${alta} casos de prioridad alta`}>
                  <span aria-hidden className="w-2.5 h-2.5 rounded-full border-[2.5px] border-current" />
                  {alta}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      <div className="mt-auto hidden lg:block border-t border-border px-4 py-4">
        <p className="text-sm font-semibold text-foreground truncate">{me.full_name}</p>
        <p className="text-xs text-muted-foreground">{ROLE_LABELS[me.role]}</p>
        <div className="mt-3 flex items-center gap-1">
          {me.role === 'MEDICO' && <NotificationBell onOpenCase={onOpenCase} />}
          <button
            onClick={toggleTheme}
            className={iconButton}
            aria-label={theme === 'dark' ? 'Usar tema claro' : 'Usar tema oscuro'}
            title={theme === 'dark' ? 'Tema claro' : 'Tema oscuro'}
          >
            {theme === 'dark' ? <Sun className="w-[18px] h-[18px]" /> : <Moon className="w-[18px] h-[18px]" />}
          </button>
          <button
            onClick={() => setShowPassword(true)}
            className={iconButton}
            aria-label="Cambiar contraseña"
            title="Cambiar contraseña"
          >
            <KeyRound className="w-[18px] h-[18px]" />
          </button>
          <button
            onClick={() => {
              apiClient.setToken(null);
              window.location.reload();
            }}
            className="ml-auto inline-flex items-center gap-2 h-9 px-3 rounded-lg text-sm text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
          >
            <LogOut aria-hidden className="w-4 h-4" />
            Salir
          </button>
        </div>
      </div>
      <Dialog open={showPassword} onOpenChange={setShowPassword} title="Cambiar contraseña" description="Al guardar, se cierran las demás sesiones abiertas.">
        <ChangePassword embedded onCancel={() => setShowPassword(false)} />
      </Dialog>
    </aside>
  );
}
