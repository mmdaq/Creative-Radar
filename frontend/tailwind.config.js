/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fdf4ff',
          100: '#fce7f6',
          200: '#f8b4f7',
          300: '#f480f5',
          400: '#ee59f5',
          500: '#d633ff',
          600: '#b03abf',
          700: '#8a2be2',
          800: '#6c2299',
          900: '#4b1771',
        }
      }
    },
  },
  plugins: [],
}
