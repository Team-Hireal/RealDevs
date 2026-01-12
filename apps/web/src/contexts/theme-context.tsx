"use client";

import React, { createContext, useContext, useEffect, useState } from "react";

export type AccentColor = "gold" | "metallic-pink" | "bronze" | "copper" | "platinum" | "steel" | "rose-gold" | "titanium";

interface ThemeContextType {
  accentColor: AccentColor;
  setAccentColor: (color: AccentColor) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const ACCENT_COLORS: Record<AccentColor, { name: string; hsl: string }> = {
  gold: { name: "Gold", hsl: "45 65% 52%" },
  "metallic-pink": { name: "Metallic Pink", hsl: "335 45% 58%" },
  bronze: { name: "Bronze", hsl: "28 55% 42%" },
  copper: { name: "Copper", hsl: "18 65% 48%" },
  platinum: { name: "Platinum", hsl: "200 12% 80%" },
  steel: { name: "Steel", hsl: "210 20% 55%" },
  "rose-gold": { name: "Rose Gold", hsl: "15 45% 60%" },
  titanium: { name: "Titanium", hsl: "195 18% 65%" },
};

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [accentColor, setAccentColorState] = useState<AccentColor>("gold");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const savedColor = localStorage.getItem("accent-color") as AccentColor;
    const initialColor = (savedColor && ACCENT_COLORS[savedColor]) ? savedColor : "gold";
    setAccentColorState(initialColor);
    
    // Set initial CSS variable immediately
    const color = ACCENT_COLORS[initialColor];
    document.documentElement.style.setProperty("--accent", color.hsl);
    
    // Remove all pattern classes while preserving other classes
    const bodyClasses = document.body.className.split(" ").filter(c => !c.startsWith("bg-pattern-"));
    document.body.className = bodyClasses.join(" ");
    
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted) {
      const color = ACCENT_COLORS[accentColor];
      document.documentElement.style.setProperty("--accent", color.hsl);
      localStorage.setItem("accent-color", accentColor);
    }
  }, [accentColor, mounted]);

  const setAccentColor = (color: AccentColor) => {
    setAccentColorState(color);
  };

  // Always provide the context, even before mounting
  return (
    <ThemeContext.Provider value={{ accentColor, setAccentColor }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
}

export { ACCENT_COLORS };

