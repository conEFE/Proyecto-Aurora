import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { Toaster } from 'sonner';
import App from './App.tsx';
import { ThemeProvider } from './lib/theme';
import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider>
      <App />
      <Toaster
        position="bottom-right"
        toastOptions={{
          className: 'font-sans text-sm',
          style: {
            background: 'hsl(var(--popover))',
            color: 'hsl(var(--popover-foreground))',
            border: '1px solid hsl(var(--border))',
          },
        }}
      />
    </ThemeProvider>
  </StrictMode>
);
