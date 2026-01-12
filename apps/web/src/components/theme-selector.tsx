"use client";

import { useTheme, ACCENT_COLORS, type AccentColor } from "@/contexts/theme-context";
import { Palette } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";

export function ThemeSelector() {
  const { accentColor, setAccentColor } = useTheme();

  return (
    <div className="space-y-6">
      <div className="space-y-3">
        <div className="flex items-center gap-2 text-sm font-medium">
          <Palette className="w-4 h-4" />
          <span>Accent Color</span>
        </div>
        <div className="grid grid-cols-4 gap-2">
          {(Object.keys(ACCENT_COLORS) as AccentColor[]).map((color) => {
            const isActive = accentColor === color;
            const colorData = ACCENT_COLORS[color];
            
            return (
              <button
                key={color}
                onClick={() => setAccentColor(color)}
                className={cn(
                  "relative h-10 w-full rounded-md border-2 transition-all",
                  "hover:scale-105 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-background",
                  isActive
                    ? "border-foreground ring-2 ring-offset-2 ring-offset-background"
                    : "border-border hover:border-foreground/50"
                )}
                style={{
                  backgroundColor: `hsl(${colorData.hsl})`,
                }}
                title={colorData.name}
                aria-label={`Select ${colorData.name} accent color`}
              >
                {isActive && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="h-2 w-2 rounded-full bg-foreground" />
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export function ThemeSelectorCard({ className }: { className?: string }) {
  return (
    <Card className={cn("glass-card", className)}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Palette className="w-5 h-5" />
          Theme
        </CardTitle>
        <CardDescription>
          Choose your accent color to customize the appearance
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ThemeSelector />
      </CardContent>
    </Card>
  );
}

