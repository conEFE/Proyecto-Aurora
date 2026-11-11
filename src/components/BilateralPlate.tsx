import type { ReactNode } from 'react';
import { cn } from '../lib/cn';

interface BreastDiagramProps {
  side: 'DERECHA' | 'IZQUIERDA';
  active?: boolean;
  className?: string;
}

/**
 * Diagrama de mama como en la orden de mamografía: contorno, pezón y marcas horarias (12, 3, 6, 9).
 * Es una referencia de lado, no una localización de la lesión.
 */
export function BreastDiagram({ side, active = false, className }: BreastDiagramProps) {
  const stroke = active ? 'hsl(var(--brand))' : 'hsl(var(--muted-foreground) / 0.45)';
  return (
    <svg viewBox="0 0 120 120" aria-hidden className={cn('w-28 h-28', className)}>
      <circle cx="60" cy="60" r="50" fill={active ? 'hsl(var(--brand) / 0.06)' : 'none'} stroke={stroke} strokeWidth="1.5" />
      <circle cx="60" cy="60" r="32" fill="none" stroke={stroke} strokeWidth="1" strokeDasharray="2 4" />
      <path d="M60 6v9M60 105v9M6 60h9M105 60h9" stroke={stroke} strokeWidth="1.5" strokeLinecap="round" />
      <circle cx="60" cy="60" r="4.5" fill={stroke} />
      {/* La axila (cola de Spence) hacia afuera de cada lado, como se dibuja visto de frente */}
      <path
        d={side === 'DERECHA' ? 'M20 32 Q8 24 4 14' : 'M100 32 Q112 24 116 14'}
        fill="none"
        stroke={stroke}
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </svg>
  );
}

interface PlateSideProps {
  side: 'DERECHA' | 'IZQUIERDA';
  active: boolean;
  caption: ReactNode;
  children?: ReactNode;
}

function PlateSide({ side, active, caption, children }: PlateSideProps) {
  return (
    <div className="flex flex-col items-center text-center min-w-0">
      <BreastDiagram side={side} active={active} />
      <p className="mt-2 text-sm">
        <span className={cn('font-bold', active ? 'text-foreground' : 'text-muted-foreground')}>
          {side === 'DERECHA' ? 'Derecha' : 'Izquierda'}
        </span>
        <span className="text-muted-foreground"> · {caption}</span>
      </p>
      {children && <div className="mt-3 w-full">{children}</div>}
    </div>
  );
}

interface BilateralPlateProps {
  right: { active: boolean; caption: ReactNode; content?: ReactNode };
  left: { active: boolean; caption: ReactNode; content?: ReactNode };
  footer?: ReactNode;
  className?: string;
}

/** Lámina bilateral D/I: la firma visual de Aurora. Derecha a la izquierda, como en la orden. */
export default function BilateralPlate({ right, left, footer, className }: BilateralPlateProps) {
  return (
    <div className={cn('border border-border rounded-xl p-5', className)}>
      <div className="grid grid-cols-2 gap-6 divide-x divide-border">
        <PlateSide side="DERECHA" active={right.active} caption={right.caption}>
          {right.content}
        </PlateSide>
        <div className="pl-6">
          <PlateSide side="IZQUIERDA" active={left.active} caption={left.caption}>
            {left.content}
          </PlateSide>
        </div>
      </div>
      {footer && <div className="mt-5 pt-4 border-t border-border">{footer}</div>}
    </div>
  );
}
