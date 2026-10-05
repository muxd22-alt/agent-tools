/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        graphite: {
          950: '#0B0D0F',
          900: '#101317',
          800: '#161A1F',
          700: '#1E242B',
          600: '#2A323B',
          500: '#3C4652'
        },
        paper: {
          100: '#ECE9E2',
          300: '#C7C2B8',
          500: '#8B9199'
        },
        signal: {
          amber: '#F5A623',
          cyan: '#4FD1C5',
          rose: '#E8615A',
          violet: '#9A8CFF'
        }
      },
      fontFamily: {
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
        sans: ['"Inter"', 'system-ui', '-apple-system', 'sans-serif']
      },
      backgroundImage: {
        grid: 'linear-gradient(to right, rgba(255,255,255,0.035) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.035) 1px, transparent 1px)'
      },
      backgroundSize: {
        grid: '28px 28px'
      },
      keyframes: {
        blink: {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.25 }
        },
        sweep: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' }
        }
      },
      animation: {
        blink: 'blink 2.4s ease-in-out infinite',
        sweep: 'sweep 3s linear infinite'
      }
    }
  },
  plugins: []
}
