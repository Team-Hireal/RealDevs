"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { LayoutDashboard, Key, Settings, Github } from "lucide-react";
import { ThemeSelector } from "./theme-selector";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/credentials", label: "Credentials", icon: Key },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Navigation() {
  const pathname = usePathname();

  return (
    <nav className="glass-card w-64 min-h-screen p-6 flex flex-col">
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-2">
          <Github className="w-8 h-8 accent-text" />
          <h1 className="text-2xl font-bold accent-text">RealDevs</h1>
        </div>
        <p className="text-xs text-muted-foreground">Team Momentum Analytics</p>
      </div>

      <div className="flex-1 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-lg transition-all",
                isActive
                  ? "bg-primary text-primary-foreground glow-sm"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary"
              )}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}
      </div>

      <div className="mt-auto pt-6 border-t border-border space-y-6">
        <ThemeSelector />
        <div className="text-xs text-muted-foreground">
          <p>Phase 1 MVP</p>
          <p>Local-first by design</p>
        </div>
      </div>
    </nav>
  );
}

