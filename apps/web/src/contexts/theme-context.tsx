"use client";

import React, { createContext, useContext, useEffect, useState } from "react";

export type AccentColor = "blue" | "green" | "purple" | "red" | "orange" | "cyan" | "pink" | "white";

interface ThemeContextType {
  accentColor: AccentColor;
  setAccentColor: (color: AccentColor) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const ACCENT_COLORS: Record<AccentColor, { name: string; hsl: string }> = {
  blue: { name: "Blue", hsl: "210 100% 50%" },
  green: { name: "Green", hsl: "142 76% 36%" },
  purple: { name: "Purple", hsl: "262 83% 58%" },
  red: { name: "Red", hsl: "0 84% 60%" },
  orange: { name: "Orange", hsl: "25 95% 53%" },
  cyan: { name: "Cyan", hsl: "188 94% 43%" },
  pink: { name: "Pink", hsl: "330 81% 60%" },
  white: { name: "White", hsl: "0 0% 100%" },
};

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [accentColor, setAccentColorState] = useState<AccentColor>("blue");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("accent-color") as AccentColor;
    const initialColor = (saved && ACCENT_COLORS[saved]) ? saved : "blue";
    setAccentColorState(initialColor);
    
    // Set initial CSS variable immediately
    const color = ACCENT_COLORS[initialColor];
    document.documentElement.style.setProperty("--accent", color.hsl);
    
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

