import { useCallback, useEffect, useRef, useState } from 'react';
import { Bell } from 'lucide-react';
import { apiClient } from '../services/api';
import type { AppNotification } from '../types';
import { formatDateTime } from './ui';

export default function NotificationBell({ onOpenCase }: { onOpenCase: (caseId: number) => void }) {
  const [items, setItems] = useState<AppNotification[]>([]);
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const load = useCallback(async () => {
    const r = await apiClient.getNotifications();
    if (r.data) setItems(r.data);
  }, []);

  useEffect(() => {
    load();
    const timer = window.setInterval(load, 30000);
    return () => window.clearInterval(timer);
  }, [load]);

  useEffect(() => {
    const close = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', close);
    return () => document.removeEventListener('mousedown', close);
  }, []);

  const unread = items.filter((n) => !n.read_at).length;

  const openNotification = async (n: AppNotification) => {
    if (!n.read_at) await apiClient.markNotificationRead(n.id);
    setOpen(false);
    load();
    onOpenCase(n.case_id);
  };

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((v) => !v)}
        className="relative p-1.5 rounded hover:bg-accent text-muted-foreground hover:text-foreground"
        aria-label={`Notificaciones (${unread} sin leer)`}
      >
        <Bell className="w-4 h-4" />
        {unread > 0 && (
          <span className="absolute -top-0.5 -right-0.5 min-w-[16px] h-4 px-1 rounded-full bg-red-500 text-white text-[9px] font-bold flex items-center justify-center">
            {unread}
          </span>
        )}
      </button>
      {open && (
        <div className="absolute right-0 mt-1 w-80 max-h-96 overflow-y-auto bg-card border border-border rounded-lg shadow-xl z-50">
          <div className="px-3 py-2 border-b border-border text-xs font-semibold text-foreground">Casos ALTA</div>
          {items.length === 0 ? (
            <p className="px-3 py-4 text-xs text-muted-foreground">Sin notificaciones</p>
          ) : (
            items.map((n) => (
              <button
                key={n.id}
                onClick={() => openNotification(n)}
                className={`w-full text-left px-3 py-2 border-b border-border hover:bg-secondary/40 ${n.read_at ? 'opacity-60' : ''}`}
              >
                <p className="text-xs text-foreground">{n.message}</p>
                <p className="text-[10px] text-muted-foreground">{formatDateTime(n.created_at)}</p>
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}
