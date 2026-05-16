/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['Sora', 'sans-serif'],
        body:    ['DM Sans', 'sans-serif'],
        mono:    ['JetBrains Mono', 'monospace'],
      },
      colors: {
        ink:    '#08080f',
        surface:'#111118',
        panel:  '#16161f',
        border: '#232334',
        muted:  '#3a3a52',
        text:   '#e2e2f0',
        dim:    '#8888aa',
        accent: '#7c6af7',
        glow:   '#a89cf7',
        green:  '#4ade80',
        red:    '#f87171',
        amber:  '#fbbf24',
      },
      boxShadow: {
        glow: '0 0 24px rgba(124, 106, 247, 0.25)',
        card: '0 2px 16px rgba(0,0,0,0.4)',
      },
      animation: {
        'fade-up':   'fadeUp 0.4s ease forwards',
        'pulse-dot': 'pulseDot 1.2s ease-in-out infinite',
        'shimmer':   'shimmer 1.6s linear infinite',
      },
      keyframes: {
        fadeUp: {
          '0%':   { opacity: 0, transform: 'translateY(12px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
        pulseDot: {
          '0%, 100%': { opacity: 1, transform: 'scale(1)' },
          '50%':      { opacity: 0.4, transform: 'scale(0.75)' },
        },
        shimmer: {
          '0%':   { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
    },
  },
  plugins: [],
}
