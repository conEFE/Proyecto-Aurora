import { useCallback, useState } from 'react';
import * as Menu from '@radix-ui/react-dropdown-menu';
import { Bell } from 'lucide-react';
import { apiClient } from '../services/api';
import type { AppNotification } from '../types';
import { usePolling } from '../lib/usePolling';
import { cn } from '../lib/cn';
import { formatDateTime, iconButton } from './ui';

export default function NotificationBell({ onOpenCase }: { onOpenCase: (caseId: number) => void }) {
  const [items, setItems] = useState<AppNotification[]>([]);

  const load = useCallback(async () => {
    const r = await apiClient.getNotifications();
    if (r.data) setItems(r.data);
  }, []);

  usePolling(load, 30000);

  const unread = items.filter((n) => !n.read_at).length;

  const openNotification = async (n: AppNotification) => {
    if (!n.read_at) await apiClient.markNotificationRead(n.id);
    load();
    onOpenCase(n.case_id);
  };

  return (
    <Menu.Root>
      <Menu.Trigger
        className={cn(iconButton, 'relative')}
        aria-label={unread > 0 ? `Notificaciones: ${unread} sin leer` : 'Notificaciones'}
      >
        <Bell className="w-5 h-5" />
        {unread > 0 && (
          <span
            aria-hidden
            className="absolute -top-0.5 -right-0.5 min-w-[1.25rem] h-5 px-1 rounded-full bg-alta text-[hsl(var(--background))] text-xs font-extrabold flex items-center justify-center"
          >
            {unread}
          </span>
        )}
      </Menu.Trigger>
      <Menu.Portal>
        <Menu.Content
          align="end"
          side="right"
          sideOffset={10}
          className="z-50 w-96 max-h-[28rem] overflow-y-auto bg-popover text-popover-foreground border border-border rounded-xl shadow-overlay py-1 data-[state=open]:animate-fade-in"
        >
          <Menu.Label className="px-4 py-2.5 text-sm font-bold border-b border-border">Casos de prioridad alta</Menu.Label>
          {items.length === 0 ? (
            <p className="px-4 py-6 text-sm text-muted-foreground">No hay notificaciones.</p>
          ) : (
            items.map((n) => (
              <Menu.Item
                key={n.id}
                onSelect={() => openNotification(n)}
                className="flex gap-3 px-4 py-3 border-b border-border last:border-0 cursor-pointer outline-none data-[highlighted]:bg-accent"
              >
                <span
                  aria-hidden
                  className={cn('mt-1.5 w-2 h-2 rounded-full shrink-0', n.read_at ? 'bg-transparent' : 'bg-alta')}
                />
                <span>
                  <span className={cn('block text-sm', n.read_at ? 'text-muted-foreground' : 'text-foreground font-semibold')}>
                    {n.message}
                  </span>
                  <span className="block text-xs text-muted-foreground mt-0.5">
                    {formatDateTime(n.created_at)}
                    {!n.read_at && <span className="sr-only"> (sin leer)</span>}
                  </span>
                </span>
              </Menu.Item>
            ))
          )}
        </Menu.Content>
      </Menu.Portal>
    </Menu.Root>
  );
}
