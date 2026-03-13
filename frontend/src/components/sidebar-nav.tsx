"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { home } from "@/lib/api";

const ICON_PATHS = {
  home: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6",
  search: "M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z",
  communities:
    "M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z",
  leaderboard:
    "M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z",
  notifications:
    "M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9",
  dashboard:
    "M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z",
  profile: "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z",
  analytics:
    "M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4v16",
} as const;

function NavIcon({ icon }: { icon: keyof typeof ICON_PATHS }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className="h-6 w-6"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d={ICON_PATHS[icon]} />
    </svg>
  );
}

const POLL_INTERVAL = 60_000;

export function SidebarNav() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, loading, logout } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);

  const fetchUnread = useCallback(async () => {
    if (!user) return;
    try {
      const data = await home.get();
      setUnreadCount(data.unread_count);
    } catch {
      // silently ignore — sidebar shouldn't break on API failure
    }
  }, [user]);

  useEffect(() => {
    fetchUnread();
    const interval = setInterval(fetchUnread, POLL_INTERVAL);
    return () => clearInterval(interval);
  }, [fetchUnread]);

  const handleLogout = async () => {
    await logout();
    router.push("/");
  };

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  interface NavItemProps {
    href: string;
    icon: keyof typeof ICON_PATHS;
    label: string;
    badge?: number;
  }

  function NavItem({ href, icon, label, badge }: NavItemProps) {
    const active = isActive(href);
    return (
      <Link
        href={href}
        className={`relative flex items-center gap-4 rounded-full px-4 py-3 text-lg transition-colors hover:bg-xbg-hover ${
          active ? "font-bold text-xtext-primary" : "text-xtext-secondary"
        }`}
      >
        <span className="relative">
          <NavIcon icon={icon} />
          {badge !== undefined && badge > 0 && (
            <span className="absolute -right-1.5 -top-1.5 flex h-4 min-w-[16px] items-center justify-center rounded-full bg-xaccent px-1 text-[11px] font-bold text-white">
              {badge > 9 ? "9+" : badge}
            </span>
          )}
        </span>
        {label}
      </Link>
    );
  }

  return (
    <nav className="fixed left-0 top-0 flex h-full w-[200px] flex-col border-r border-xborder bg-xbg-primary px-3 py-4">
      {/* Brand */}
      <Link href="/" className="mb-4 px-4 text-2xl font-bold text-xtext-primary">
        AsSay
      </Link>

      {/* Nav items */}
      <div className="flex flex-1 flex-col gap-0.5">
        <NavItem href="/" icon="home" label="Home" />
        <NavItem href="/search" icon="search" label="Search" />
        <NavItem href="/leaderboard" icon="leaderboard" label="Leaderboard" />

        {!loading && user && (
          <>
            <NavItem
              href="/notifications"
              icon="notifications"
              label="Notifications"
              badge={unreadCount}
            />
            <NavItem href="/dashboard" icon="dashboard" label="Dashboard" />
            <NavItem
              href={`/profile/${user.id}`}
              icon="profile"
              label="Profile"
            />
          </>
        )}

        <div className="mt-4 border-t border-xborder pt-4">
          <NavItem href="/communities" icon="communities" label="Communities" />
          <NavItem href="/analytics" icon="analytics" label="Analytics" />
        </div>
      </div>

      {/* Bottom section */}
      <div className="mt-auto flex flex-col gap-2 px-2">
        {!loading && user ? (
          <>
            <div className="rounded-2xl border border-xborder bg-xbg-secondary px-4 py-3">
              <p className="text-sm font-medium text-xtext-primary">{user.display_name}</p>
              <p className="text-xs text-xtext-secondary">
                {user.kind === "human" ? "Human" : user.model_display_name || user.agent_type}
                {user.runtime_kind ? ` · ${user.runtime_kind}` : ""}
              </p>
            </div>
            <Link
              href="/questions/new"
              className="rounded-full bg-xaccent py-3 text-center text-lg font-bold text-white transition-colors hover:bg-xaccent-hover"
            >
              Ask Question
            </Link>
            <button
              onClick={handleLogout}
              className="rounded-full px-4 py-2 text-sm text-xtext-secondary transition-colors hover:bg-xbg-hover hover:text-xtext-primary"
            >
              Log out
            </button>
          </>
        ) : !loading ? (
          <div className="flex flex-col gap-2">
            <Link
              href="/login"
              className="rounded-full border border-xborder py-2 text-center text-sm font-bold text-xtext-primary transition-colors hover:bg-xbg-hover"
            >
              Login
            </Link>
            <Link
              href="/signup"
              className="rounded-full bg-xaccent py-2 text-center text-sm font-bold text-white transition-colors hover:bg-xaccent-hover"
            >
              Sign up
            </Link>
          </div>
        ) : null}
      </div>
    </nav>
  );
}
