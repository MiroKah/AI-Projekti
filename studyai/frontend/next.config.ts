import type { NextConfig } from "next";

/**
 * Next.js-konfiguraatio.
 * Palvelinpuolen kutsut backendille ohjataan Docker-verkossa BACKEND_INTERNAL_URL:n kautta.
 */
const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Salli kuvat tarvittaessa ulkoisista lähteistä (esim. myöhemmin avatarit)
  images: {
    remotePatterns: [],
  },
  // Backend-osoite välitetään ympäristömuuttujana (ks. .env.local.example)
  env: {
    NEXT_PUBLIC_API_BASE_URL:
      process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000",
  },
};

export default nextConfig;
