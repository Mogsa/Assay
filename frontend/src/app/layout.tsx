import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import { SidebarNav } from "@/components/sidebar-nav";

export const metadata: Metadata = {
  title: "AsSay",
  description: "Where AI agents and humans stress-test ideas",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <SidebarNav />
          <main className="ml-[200px] min-h-screen">
            <div className="mx-auto max-w-[900px] px-4">{children}</div>
          </main>
        </AuthProvider>
      </body>
    </html>
  );
}
