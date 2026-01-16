"use client";

import React, { createContext, useContext, useEffect, useState } from "react";

export type AccentColor = "yellow" | "cyan" | "silver-blue" | "orange-gold" | "olive" | "purple" | "pink" | "customize";

interface ThemeContextType {
  accentColor: AccentColor;
  setAccentColor: (color: AccentColor) => void;
  customColorHsl: string;
  setCustomColor: (hsl: string) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const ACCENT_COLORS: Record<AccentColor, { name: string; hsl: string }> = {
  yellow: { name: "Yellow", hsl: "50 55% 62%" },
  cyan: { name: "Cyan", hsl: "180 45% 58%" },
  "silver-blue": { name: "Silver Blue", hsl: "210 35% 65%" },
  "orange-gold": { name: "Orange Gold", hsl: "35 60% 55%" },
  olive: { name: "Olive", hsl: "80 30% 55%" },
  purple: { name: "Purple", hsl: "280 45% 60%" },
  pink: { name: "Pink", hsl: "340 50% 65%" },
  customize: { name: "Customize", hsl: "160 40% 58%" },
};

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [accentColor, setAccentColorState] = useState<AccentColor>("yellow");
  const [customColorHsl, setCustomColorHsl] = useState<string>("160 40% 58%");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const savedColor = localStorage.getItem("accent-color") as AccentColor;
    const savedCustomColor = localStorage.getItem("custom-color-hsl");
    const initialColor = (savedColor && ACCENT_COLORS[savedColor]) ? savedColor : "yellow";
    setAccentColorState(initialColor);
    
    if (savedCustomColor) {
      setCustomColorHsl(savedCustomColor);
    }
    
    // Set initial CSS variable immediately
    const color = initialColor === "customize" && savedCustomColor 
      ? savedCustomColor 
      : ACCENT_COLORS[initialColor].hsl;
    document.documentElement.style.setProperty("--accent", color);
    
    // Remove all pattern classes while preserving other classes
    const bodyClasses = document.body.className.split(" ").filter(c => !c.startsWith("bg-pattern-"));
    document.body.className = bodyClasses.join(" ");
    
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted) {
      const color = accentColor === "customize" ? customColorHsl : ACCENT_COLORS[accentColor].hsl;
      document.documentElement.style.setProperty("--accent", color);
      localStorage.setItem("accent-color", accentColor);
    }
  }, [accentColor, customColorHsl, mounted]);

  const setAccentColor = (color: AccentColor) => {
    setAccentColorState(color);
  };

  const setCustomColor = (hsl: string) => {
    setCustomColorHsl(hsl);
    localStorage.setItem("custom-color-hsl", hsl);
    // Update CSS variable immediately
    if (accentColor === "customize") {
      document.documentElement.style.setProperty("--accent", hsl);
    }
  };

  // Always provide the context, even before mounting
  return (
    <ThemeContext.Provider value={{ accentColor, setAccentColor, customColorHsl, setCustomColor }}>
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

