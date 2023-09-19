module.exports = {
  purge: ['./pages/**/*.{js,ts,jsx,tsx}', './components/**/*.{js,ts,jsx,tsx}', './templates/**/*.{js,ts,jsx,tsx}'],
  content: [],
  theme: {
    extend: {
      colors: {
        primaryMuted: '#666666',
        primary: '#0f4e8a',
        primaryDark: '#00194B',
        onPrimary: '#ffffff',
        primaryContainer: '#9AC4FF',
        onPrimaryContainer: '#000000',
        secondary: '#EA5B2D',
        onSecondary: '#ffffff',
        secondaryContainer: '#FFBD85',
        onSecondaryContainer: '#000000',
        surface: '#ffffff',
        onSurface: '#333333',
        surfaceContainer: '#f2f2f2',
        onSurfaceContainer: '#000000',
      },
      fontFamily: {
        sans: ['Titillium Web', 'sans-serif'],
      },
    },
  },
  variants: {
    textColor: ['responsive', 'hover', 'focus', 'active']
  },
  plugins: [],
}
