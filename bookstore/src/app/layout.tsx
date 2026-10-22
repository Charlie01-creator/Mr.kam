import type { Metadata } from "next";
import { Source_Serif_4, Public_Sans } from "next/font/google";
import "./globals.css";
import { site } from "@/config/site";
import { Header, Footer } from "@/components/SiteChrome";

const serif = Source_Serif_4({ subsets: ["latin"], variable: "--font-serif", display: "swap" });
const sans = Public_Sans({ subsets: ["latin"], variable: "--font-sans", display: "swap" });

const base = process.env.SITE_URL ?? "http://localhost:3000";

export const metadata: Metadata = {
  metadataBase: new URL(base),
  title: { default: `${site.name} | Mathematics textbooks in Uganda`, template: `%s | ${site.name}` },
  description: "Mathematics, statistics and numerical methods textbooks for students and teachers in Uganda.",
  alternates: { canonical: "/" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${serif.variable} ${sans.variable}`}>
      <body>
        <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:left-2 focus:top-2 focus:bg-paper focus:p-2">Skip to content</a>
        <Header />
        <main id="main">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
