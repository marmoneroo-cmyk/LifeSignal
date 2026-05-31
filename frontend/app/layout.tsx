import type { Metadata, Viewport } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import { LanguageProvider } from "@/lib/i18n";
import { AuthGate } from "@/components/AuthGate";

export const metadata: Metadata = {
  title: "LifeSignal — Personal Health Intelligence",
  description:
    "A clinical decision-support layer that surfaces trends, gaps, and preventive opportunities from your own health and insurance data.",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "LifeSignal",
  },
};

export const viewport: Viewport = {
  themeColor: "#0d9488",
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <LanguageProvider>
          <AuthProvider>
            <AuthGate>{children}</AuthGate>
          </AuthProvider>
        </LanguageProvider>
      </body>
    </html>
  );
}
