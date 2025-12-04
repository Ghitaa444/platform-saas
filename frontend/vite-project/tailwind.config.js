/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
       
        primary: {
          DEFAULT: "#7C3AED",
          dark: "#6D28D9",
          light: "#A78BFA",
        },
        secondary: {
          DEFAULT: "#A1A1AA",
          dark: "#71717A",
          light: "#D4D4D8",
        },
        accent: {
          DEFAULT: "#9333EA",
          dark: "#7E22CE",
          light: "#C084FC",
        },
        danger: {
          DEFAULT: "#EF4444",
          dark: "#DC2626",
          light: "#FCA5A5",
        },
        neutral: {
          50: "#FAFAFA",
          100: "#F4F4F5",
          200: "#E4E4E7",
          300: "#D4D4D8",
          400: "#A1A1AA",
          500: "#71717A",
          600: "#52525B",
          700: "#3F3F46",
          800: "#27272A",
          900: "#18181B",
        },
        background: {
          DEFAULT: "#0E0E10",
          dark: "#0A0A0C",
          light: "#18181B",
        },
        card: {
          DEFAULT: "#18181B",
          dark: "#1F1F23",
        },
        text: {
          DEFAULT: "#E4E4E7",
          light: "#FAFAFA",
          muted: "#A1A1AA",
        },
      },

      fontFamily: {
        sans: ["Inter", "Poppins", "ui-sans-serif", "system-ui"],
      },

      boxShadow: {
        card: "0 8px 24px rgba(124, 58, 237, 0.1)",
        glow: "0 0 25px rgba(124, 58, 237, 0.35)",
        innerSoft: "inset 0 1px 0 rgba(255,255,255,0.05)",
      },

      backgroundImage: {
        "railway-gradient": "linear-gradient(135deg, #0E0E10 0%, #1F1F23 100%)",
        "railway-card": "linear-gradient(180deg, #1A1A1C 0%, #0F0F12 100%)",
        "accent-glow": "radial-gradient(circle at top right, rgba(124,58,237,0.2), transparent 70%)",
      },

      borderRadius: {
        xl: "1rem",
        "2xl": "1.25rem",
      },

      transitionTimingFunction: {
        smooth: "cubic-bezier(0.4, 0, 0.2, 1)",
        bounceSoft: "cubic-bezier(0.68, -0.55, 0.27, 1.55)",
      },

      animation: {
        float: "float 6s ease-in-out infinite",
        pulseSlow: "pulseSlow 4s ease-in-out infinite",
      },

      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" },
        },
        pulseSlow: {
          "0%, 100%": { opacity: 1 },
          "50%": { opacity: 0.6 },
        },
      },
    },
  },
  plugins: [require("@tailwindcss/forms")],
};
