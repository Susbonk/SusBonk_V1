/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      fontFamily: {
        'poppins': ['Poppins', 'sans-serif'],
      },
      colors: {
        'susbonk-lime': '#CCFF00',
        'susbonk-orange': '#FF8A00',
      },
      boxShadow: {
        'brutal': '4px 4px 0px 0px rgba(0,0,0,1)',
        'brutal-lg': '6px 6px 0px 0px rgba(0,0,0,1)',
        'brutal-sm': '2px 2px 0px 0px rgba(0,0,0,1)',
        'brutal-xl': '8px 8px 0px 0px rgba(0,0,0,1)',
      },
      animation: {
        'wobble': 'wobble 0.3s ease-in-out',
        'bonk': 'bonk 0.4s ease-in-out',
      }
    },
  },
  plugins: [],
}
