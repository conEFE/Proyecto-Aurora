import { useEffect } from 'react';

/** Ejecuta `fn` al montar y cada `ms`, pausando mientras la pestaña está oculta. */
export function usePolling(fn: () => void, ms: number) {
  useEffect(() => {
    fn();
    let timer: number | undefined;
    const start = () => {
      window.clearInterval(timer);
      timer = window.setInterval(fn, ms);
    };
    const onVisibility = () => {
      if (document.visibilityState === 'visible') {
        fn();
        start();
      } else {
        window.clearInterval(timer);
      }
    };
    start();
    document.addEventListener('visibilitychange', onVisibility);
    return () => {
      window.clearInterval(timer);
      document.removeEventListener('visibilitychange', onVisibility);
    };
  }, [fn, ms]);
}
