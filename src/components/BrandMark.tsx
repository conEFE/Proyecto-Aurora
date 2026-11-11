import simboloClaro from '../assets/aurora-simbolo-claro.png';
import simboloClaroChico from '../assets/aurora-simbolo-claro-96.png';
import simboloOscuro from '../assets/aurora-simbolo-oscuro.png';
import simboloOscuroChico from '../assets/aurora-simbolo-oscuro-96.png';
import { cn } from '../lib/cn';

/** Símbolo oficial de Aurora con transparencia real, una versión por tema. */
export default function BrandMark({
  className,
  alt = '',
  size = 'sm',
}: {
  className?: string;
  alt?: string;
  size?: 'sm' | 'lg';
}) {
  const claro = size === 'lg' ? simboloClaro : simboloClaroChico;
  const oscuro = size === 'lg' ? simboloOscuro : simboloOscuroChico;
  return (
    <span className={cn('relative inline-block w-11 h-7 shrink-0', className)}>
      <img src={claro} alt={alt} className="absolute inset-0 w-full h-full object-contain dark:hidden" />
      <img src={oscuro} alt={alt} className="absolute inset-0 w-full h-full object-contain hidden dark:block" />
    </span>
  );
}
