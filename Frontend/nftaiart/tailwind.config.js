/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      "./app/**/*.{js,ts,jsx,tsx,mdx}",
      "./components/**/*.{js,ts,jsx,tsx,mdx}",
      "./src/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    darkMode: 'class', // Enables class-based dark mode
    theme: {
      extend: {
        colors: {
          background: 'var(--background)',
          foreground: 'var(--foreground)',
          primary: {
            DEFAULT: 'var(--primary)',
            hover: 'var(--primary-hover)'
          },
          card: 'var(--card-bg)'
        },
        borderRadius: {
          card: 'var(--radius-card)'
        },
        fontFamily: {
          sans: ['var(--font-sans)']
        },
        animation: {
          pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite'
        },
        keyframes: {
          pulse: {
            '50%': { opacity: '0.5' }
          }
        }
      },
    },
    plugins: [
      require('@tailwindcss/typography'), // For rich text formatting
      require('@tailwindcss/aspect-ratio') // For NFT image containers
    ],
  }