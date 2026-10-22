import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: { 950: "#0B1A33", 900: "#10264A", 800: "#17356A", 700: "#1F4687" },
        paper: { DEFAULT: "#FFFFFF", warm: "#FAF7F0", line: "#E6E0D2" },
        gold: { DEFAULT: "#B8862B", soft: "#E9D3A0", ink: "#7A5712" },
        ink: { DEFAULT: "#1B2433", muted: "#4F5A6B" },
      },
      fontFamily: {
        serif: ["var(--font-serif)", "Georgia", "serif"],
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
export default config;
