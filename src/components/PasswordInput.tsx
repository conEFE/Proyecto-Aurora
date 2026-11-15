import { forwardRef, useState, type InputHTMLAttributes } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import { cn } from '../lib/cn';
import { inputClass } from './ui';

type Props = Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> & {
  /** Clases del campo (la de `className` va al contenedor, p. ej. el ancho). */
  inputClassName?: string;
};

/** Campo de contraseña con un botón para mostrarla u ocultarla. */
const PasswordInput = forwardRef<HTMLInputElement, Props>(function PasswordInput({ className, inputClassName, ...props }, ref) {
  const [visible, setVisible] = useState(false);
  return (
    <div className={cn('relative', className)}>
      <input ref={ref} {...props} type={visible ? 'text' : 'password'} className={cn(inputClass, 'pr-11', inputClassName)} />
      <button
        type="button"
        onClick={() => setVisible((v) => !v)}
        aria-pressed={visible}
        aria-label={visible ? 'Ocultar contraseña' : 'Mostrar contraseña'}
        title={visible ? 'Ocultar contraseña' : 'Mostrar contraseña'}
        className="absolute inset-y-0 right-0 w-10 grid place-items-center rounded-r-lg text-muted-foreground hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      >
        {visible ? <EyeOff aria-hidden className="w-[18px] h-[18px]" /> : <Eye aria-hidden className="w-[18px] h-[18px]" />}
      </button>
    </div>
  );
});

export default PasswordInput;
