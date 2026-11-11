/** @type {import('tailwindcss').Config} */
const token = (name) => `hsl(var(--${name}) / <alpha-value>)`;

export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        background: token('background'),
        foreground: token('foreground'),
        card: { DEFAULT: token('card'), foreground: token('card-foreground') },
        popover: { DEFAULT: token('popover'), foreground: token('popover-foreground') },
        primary: { DEFAULT: token('primary'), foreground: token('primary-foreground') },
        secondary: { DEFAULT: token('secondary'), foreground: token('secondary-foreground') },
        muted: { DEFAULT: token('muted'), foreground: token('muted-foreground') },
        accent: { DEFAULT: token('accent'), foreground: token('accent-foreground') },
        destructive: { DEFAULT: token('destructive'), foreground: token('destructive-foreground') },
        brand: token('brand'),
        border: token('border'),
        input: token('input'),
        ring: token('ring'),
        sidebar: token('sidebar'),
        alta: token('alta'),
        media: token('media'),
        baja: token('baja'),
        sim: token('sim'),
        proto: token('proto'),
        info: token('info'),
      },
      fontFamily: {
        sans: ['"Atkinson Hyperlegible Next Variable"', 'system-ui', 'sans-serif'],
      },
      // Escala legible para uso clínico prolongado: 13 px es el mínimo.
      fontSize: {
        xs: ['0.8125rem', { lineHeight: '1.15rem' }],
        sm: ['0.9375rem', { lineHeight: '1.4rem' }],
        base: ['1rem', { lineHeight: '1.5rem' }],
        lg: ['1.125rem', { lineHeight: '1.6rem' }],
        xl: ['1.375rem', { lineHeight: '1.8rem', letterSpacing: '-0.01em' }],
        '2xl': ['1.75rem', { lineHeight: '2.1rem', letterSpacing: '-0.015em' }],
        '3xl': ['2.25rem', { lineHeight: '2.6rem', letterSpacing: '-0.02em' }],
      },
      boxShadow: {
        overlay: '0 18px 48px -12px hsl(var(--shadow) / 0.45), 0 2px 6px hsl(var(--shadow) / 0.18)',
      },
      keyframes: {
        'fade-in': { from: { opacity: '0' }, to: { opacity: '1' } },
      },
      animation: {
        'fade-in': 'fade-in 160ms ease-out',
      },
    },
  },
  plugins: [],
};
