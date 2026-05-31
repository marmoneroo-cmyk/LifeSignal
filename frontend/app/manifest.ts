import type { MetadataRoute } from "next";

/**
 * PWA manifest — lets users install LifeSignal as a standalone app
 * (Add to Home Screen on mobile, Install button on desktop browsers).
 * Next.js serves this at /manifest.webmanifest automatically.
 */
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "LifeSignal — Personal Health Intelligence",
    short_name: "LifeSignal",
    description:
      "Personal health intelligence — clinical decision support across labs, insurance, and family history.",
    start_url: "/",
    display: "standalone",
    orientation: "portrait",
    background_color: "#f8fafc",
    theme_color: "#0d9488",
    lang: "he",
    dir: "rtl",
    icons: [
      {
        src: "/icon.svg",
        sizes: "any",
        type: "image/svg+xml",
        purpose: "any",
      },
    ],
    categories: ["health", "medical", "lifestyle"],
  };
}
