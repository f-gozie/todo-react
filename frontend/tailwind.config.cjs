module.exports = {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Dark theme base
        dark: {
          bg: '#0a0a0f',
          card: 'rgba(255, 255, 255, 0.05)',
          glass: 'rgba(255, 255, 255, 0.03)',
          border: 'rgba(255, 255, 255, 0.1)',
          'border-light': 'rgba(255, 255, 255, 0.08)',
        },
        // Text colors
        text: {
          primary: '#ffffff',
          secondary: '#a8a8b3',
        },
        // Music service brand colors
        spotify: '#1DB954',
        deezer: '#FF6D00',
        youtube: '#FF0000',
        // Status colors
        success: '#4ade80',
      },
      backgroundImage: {
        'primary-gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'secondary-gradient': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        'accent-gradient': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        'dark-radial': `
          radial-gradient(circle at 20% 50%, rgba(102, 126, 234, 0.1) 0%, transparent 50%),
          radial-gradient(circle at 80% 80%, rgba(240, 147, 251, 0.1) 0%, transparent 50%),
          radial-gradient(circle at 40% 20%, rgba(79, 172, 254, 0.1) 0%, transparent 50%)
        `,
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      borderRadius: {
        '2xl': '24px',
      },
      backdropBlur: {
        '20': '20px',
      },
      boxShadow: {
        'glow-blue': '0 10px 30px rgba(79, 172, 254, 0.3)',
        'glow-blue-hover': '0 15px 40px rgba(79, 172, 254, 0.4)',
        'glow-spotify': '0 5px 20px rgba(29, 185, 84, 0.4)',
        'glow-deezer': '0 5px 20px rgba(255, 109, 0, 0.4)',
        'glow-youtube': '0 5px 20px rgba(255, 0, 0, 0.4)',
        'glow-success': '0 0 10px #4ade80',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease',
        'fade-in-up': 'fadeInUp 0.8s ease',
        'fade-in-down': 'fadeInDown 0.8s ease',
        'glow': 'glow 3s ease-in-out infinite alternate',
        'pulse-glow': 'pulseGlow 2s infinite',
        'spin-slow': 'spin 1s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeInDown: {
          '0%': { opacity: '0', transform: 'translateY(-20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        glow: {
          '0%': { filter: 'drop-shadow(0 0 20px rgba(102, 126, 234, 0.5))' },
          '100%': { filter: 'drop-shadow(0 0 30px rgba(240, 147, 251, 0.8))' },
        },
        pulseGlow: {
          '0%, 100%': { transform: 'scale(1)', opacity: '1' },
          '50%': { transform: 'scale(1.2)', opacity: '0.8' },
        },
      },
    },
  },
  plugins: [require('@tailwindcss/forms'), require('@tailwindcss/typography')],
}; 