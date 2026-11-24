"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { LayoutDashboard, Key, Settings, Menu, X } from "lucide-react";
import { ThemeSelector } from "./theme-selector";
import { useState, useMemo } from "react";
import { useLanguage } from "@/contexts/language-context";

const getNavItems = (t: any) => [
  { href: "/", label: t.nav.dashboard, icon: LayoutDashboard },
  { href: "/credentials", label: t.nav.credentials, icon: Key },
  { href: "/settings", label: t.nav.settings, icon: Settings },
];

export function Navigation() {
  const { t } = useLanguage();
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const navItems = useMemo(() => getNavItems(t), [t]);

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="md:hidden fixed bottom-4 left-4 z-50 p-2 glass-card rounded-lg"
        aria-label="Toggle menu"
      >
        {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
      </button>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/50 z-30"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Navigation */}
      <nav className={cn(
        "glass-card w-64 h-screen p-6 flex flex-col",
        "fixed md:relative z-40",
        "transition-transform duration-300 ease-in-out",
        isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
      )}>
      <div className="mb-8">
        <Link 
          href="https://hireal.info" 
          target="_blank" 
          rel="noopener noreferrer"
          className="flex items-center gap-2 mb-2 pl-3 hover:opacity-80 transition-opacity"
        >
          <img 
            src="/logo.png" 
            alt="Hireal Logo" 
            width={32} 
            height={32} 
            className="w-8 h-8 object-contain"
          />
          <div className="text-2xl font-bold accent-text">RealDevs</div>
        </Link>
        
      </div>

      <div className="flex-1 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setIsOpen(false)}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-lg transition-all",
                isActive
                  ? "bg-primary text-primary-foreground"
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
        
        <div className="text-xs text-muted-foreground text-center pt-4">
          <p>{t.common.poweredBy} <span className="font-semibold">Hireal Inc.</span></p>
        </div>
      </div>
      {/* https://github.com/SimonSaysGiveMeSmile */}
    </nav>
    </>
  );
}

