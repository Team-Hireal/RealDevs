import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";

const inter = Inter({ subsets: ["latin"] });

const SITE_URL = "https://www.realdevs.pro";
const TITLE = "RealDevs — Team Trend Analytics for Engineering Teams";
const DESCRIPTION =
  "Track team trends and identify risks without surveillance. RealDevs summarizes GitHub commits, pull requests and contributor momentum across your repos.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: TITLE,
  description: DESCRIPTION,
  applicationName: "RealDevs",
  alternates: { canonical: "/" },
  icons: {
    icon: "/logo.png",
  },
  openGraph: {
    type: "website",
    url: SITE_URL,
    siteName: "RealDevs",
    title: TITLE,
    description: DESCRIPTION,
    images: [{ url: "/og.png", width: 1200, height: 630, alt: "RealDevs team trend analytics dashboard" }],
  },
  twitter: {
    card: "summary_large_image",
    title: TITLE,
    description: DESCRIPTION,
    images: ["/og.png"],
  },
};

const jsonLd = [
  {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: "RealDevs",
    url: SITE_URL,
    description: DESCRIPTION,
    publisher: { "@type": "Organization", name: "Hireal Inc." },
  },
  {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    name: "RealDevs",
    url: SITE_URL,
    description: DESCRIPTION,
    image: `${SITE_URL}/og.png`,
    applicationCategory: "BusinessApplication",
    operatingSystem: "Web",
    publisher: { "@type": "Organization", name: "Hireal Inc." },
    author: { "@type": "Person", name: "Simon Tian", url: "https://www.hisimon.pro" },
  },
];

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
        <div className="sr-only">
          <p>
            RealDevs is a team trend analytics dashboard for team leads and startup founders. It
            tracks commits, pull requests and contributions across your GitHub repositories, ranks
            contributor momentum, and flags risks such as inactive members, single points of failure
            and stale repositories — without surveillance.
          </p>
          <p>Powered by Hireal Inc.</p>
        </div>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
