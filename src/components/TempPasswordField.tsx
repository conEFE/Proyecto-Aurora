import { useState, type InputHTMLAttributes } from 'react';
import { Check, Copy, KeyRound } from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '../lib/cn';
import { generateTempPassword } from '../utils/password';
import PasswordInput from './PasswordInput';
import { secondaryButton } from './ui';

type Props = Omit<InputHTMLAttributes<HTMLInputElement>, 'type' | 'value' | 'onChange'> & {
  value: string;
  onChange: (value: string) => void;
  /** Ancho u otras clases del campo. */
  fieldClassName?: string;
};

/**
 * Contraseña temporal para otra persona: se puede escribir o generar al azar, y copiar para entregarla. Al generarla
 * queda visible, para que el administrador la vea antes de copiarla.
 */
export default function TempPasswordField({ value, onChange, fieldClassName, className, ...props }: Props) {
  const [visible, setVisible] = useState(false);
  const [copied, setCopied] = useState(false);

  const generate = () => {
    onChange(generateTempPassword());
    setVisible(true);
    setCopied(false);
  };

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      toast.success('Contraseña copiada');
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error('No se pudo copiar. Selecciónela y cópiela a mano.');
    }
  };

  return (
    <div className={cn('flex flex-wrap items-center gap-2', className)}>
      <PasswordInput
        {...props}
        className={cn('min-w-0 flex-1', fieldClassName)}
        inputClassName="tracking-wide"
        value={value}
        onChange={(e) => {
          onChange(e.target.value);
          setCopied(false);
        }}
        visible={visible}
        onVisibleChange={setVisible}
      />
      <button type="button" className={secondaryButton} onClick={generate}>
        <KeyRound aria-hidden className="w-4 h-4" />
        Generar
      </button>
      <button type="button" className={secondaryButton} onClick={copy} disabled={!value}
        aria-label="Copiar contraseña" title="Copiar contraseña">
        {copied ? <Check aria-hidden className="w-4 h-4" /> : <Copy aria-hidden className="w-4 h-4" />}
        <span className="sr-only sm:not-sr-only">{copied ? 'Copiada' : 'Copiar'}</span>
      </button>
    </div>
  );
}
