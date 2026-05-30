import type { Config } from "tailwindcss";

const config: Config = {
  // Logical-properties support: border-s, ps-*, ms-* work with dir="rtl" / dir="ltr".

  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#0d9488", // teal-600 — calm, clinical, trustworthy
          fg: "#0f766e",
          soft: "#ccfbf1",
        },
        critical: "#dc2626",
        high: "#ea580c",
        preventive: "#0d9488",
        info: "#64748b",
      },
      borderRadius: {
        xl: "0.9rem",
      },
    },
  },
  plugins: [],
};

export default config;
