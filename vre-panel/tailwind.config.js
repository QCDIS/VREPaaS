module.exports = {
  purge: ['./pages/**/*.{js,ts,jsx,tsx}', './components/**/*.{js,ts,jsx,tsx}', './templates/**/*.{js,ts,jsx,tsx}'],
  content: [],
  theme: {
    extend: {
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
