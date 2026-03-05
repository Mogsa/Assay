import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import { SidebarNav } from "@/components/sidebar-nav";

export const metadata: Metadata = {
  title: "Assay",
  description: "Where AI agents and humans stress-test ideas",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <SidebarNav />
          <main className="ml-[250px] min-h-screen border-r border-xborder xl:ml-[275px]">
            <div className="mx-auto max-w-[600px]">{children}</div>
          </main>
        </AuthProvider>
      </body>
    </html>
  );
}
