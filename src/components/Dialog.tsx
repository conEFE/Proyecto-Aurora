import * as RadixDialog from '@radix-ui/react-dialog';
import { X } from 'lucide-react';
import type { ReactNode } from 'react';
import { cn } from '../lib/cn';
import { iconButton } from './ui';

interface DialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: string;
  children: ReactNode;
  footer?: ReactNode;
  size?: 'md' | 'lg';
}

/**
 * Diálogo accesible (Radix): foco atrapado, Esc para cerrar, foco devuelto al disparador
 * y título/descripción enlazados para lectores de pantalla.
 */
export default function Dialog({ open, onOpenChange, title, description, children, footer, size = 'md' }: DialogProps) {
  return (
    <RadixDialog.Root open={open} onOpenChange={onOpenChange}>
      <RadixDialog.Portal>
        <RadixDialog.Overlay className="fixed inset-0 z-50 bg-[hsl(var(--shadow)/0.55)] data-[state=open]:animate-fade-in" />
        <RadixDialog.Content
          className={cn(
            'fixed left-1/2 top-1/2 z-50 -translate-x-1/2 -translate-y-1/2 w-[calc(100vw-2rem)] max-h-[88vh] flex flex-col',
            'bg-popover text-popover-foreground border border-border rounded-2xl shadow-overlay data-[state=open]:animate-fade-in',
            size === 'lg' ? 'max-w-3xl' : 'max-w-xl',
          )}
        >
          <div className="flex items-start justify-between gap-4 px-6 pt-5 pb-4 border-b border-border">
            <div>
              <RadixDialog.Title className="text-lg font-bold">{title}</RadixDialog.Title>
              {description ? (
                <RadixDialog.Description className="mt-0.5 text-sm text-muted-foreground">{description}</RadixDialog.Description>
              ) : (
                <RadixDialog.Description className="sr-only">{title}</RadixDialog.Description>
              )}
            </div>
            <RadixDialog.Close className={cn(iconButton, '-mr-2')} aria-label="Cerrar">
              <X className="w-5 h-5" />
            </RadixDialog.Close>
          </div>
          <div className="px-6 py-5 overflow-y-auto">{children}</div>
          {footer && <div className="flex justify-end gap-2 px-6 py-4 border-t border-border">{footer}</div>}
        </RadixDialog.Content>
      </RadixDialog.Portal>
    </RadixDialog.Root>
  );
}
