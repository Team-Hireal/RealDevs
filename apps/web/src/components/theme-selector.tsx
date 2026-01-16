"use client";

import { useTheme, ACCENT_COLORS, type AccentColor } from "@/contexts/theme-context";
import { Palette, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { useState, useEffect, useRef } from "react";

// Helper function to convert hex to HSL
function hexToHsl(hex: string): string {
  // Remove # if present
  hex = hex.replace(/^#/, '');
  
  // Parse hex values
  const r = parseInt(hex.substring(0, 2), 16) / 255;
  const g = parseInt(hex.substring(2, 4), 16) / 255;
  const b = parseInt(hex.substring(4, 6), 16) / 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  let h = 0, s = 0, l = (max + min) / 2;

  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    
    switch (max) {
      case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
      case g: h = ((b - r) / d + 2) / 6; break;
      case b: h = ((r - g) / d + 4) / 6; break;
    }
  }

  h = Math.round(h * 360);
  s = Math.round(s * 100);
  l = Math.round(l * 100);

  return `${h} ${s}% ${l}%`;
}

// Helper function to convert HSL to hex
function hslToHex(hsl: string): string {
  const [h, s, l] = hsl.split(' ').map(v => parseInt(v));
  const sNorm = s / 100;
  const lNorm = l / 100;

  const c = (1 - Math.abs(2 * lNorm - 1)) * sNorm;
  const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
  const m = lNorm - c / 2;

  let r = 0, g = 0, b = 0;

  if (h >= 0 && h < 60) {
    r = c; g = x; b = 0;
  } else if (h >= 60 && h < 120) {
    r = x; g = c; b = 0;
  } else if (h >= 120 && h < 180) {
    r = 0; g = c; b = x;
  } else if (h >= 180 && h < 240) {
    r = 0; g = x; b = c;
  } else if (h >= 240 && h < 300) {
    r = x; g = 0; b = c;
  } else if (h >= 300 && h < 360) {
    r = c; g = 0; b = x;
  }

  const toHex = (n: number) => {
    const hex = Math.round((n + m) * 255).toString(16);
    return hex.length === 1 ? '0' + hex : hex;
  };

  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}

export function ThemeSelector() {
  const { accentColor, setAccentColor, customColorHsl, setCustomColor } = useTheme();
  const [showColorPicker, setShowColorPicker] = useState(false);
  const [tempColor, setTempColor] = useState(hslToHex(customColorHsl));
  const popupRef = useRef<HTMLDivElement>(null);

  // Close popup when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (popupRef.current && !popupRef.current.contains(event.target as Node)) {
        setShowColorPicker(false);
      }
    };

    if (showColorPicker) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [showColorPicker]);

  const handleColorClick = (color: AccentColor) => {
    if (color === "customize") {
      setShowColorPicker(true);
    } else {
      setAccentColor(color);
    }
  };

  const handleColorChange = (hex: string) => {
    setTempColor(hex);
  };

  const handleApplyCustomColor = () => {
    const hsl = hexToHsl(tempColor);
    setCustomColor(hsl);
    setAccentColor("customize");
    setShowColorPicker(false);
  };

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
            const displayHsl = color === "customize" ? customColorHsl : colorData.hsl;
            
            return (
              <button
                key={color}
                onClick={() => handleColorClick(color)}
                className={cn(
                  "relative h-10 w-full rounded-md border-2 transition-all",
                  "hover:scale-105 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-background",
                  isActive
                    ? "border-foreground ring-2 ring-offset-2 ring-offset-background"
                    : "border-border hover:border-foreground/50"
                )}
                style={{
                  backgroundColor: `hsl(${displayHsl})`,
                }}
                title={colorData.name}
                aria-label={`Select ${colorData.name} accent color`}
              >
                {color === "customize" && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <Palette className="w-4 h-4 text-foreground drop-shadow-md" />
                  </div>
                )}
                {isActive && color !== "customize" && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="h-2 w-2 rounded-full bg-foreground" />
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Color Picker Popup */}
      {showColorPicker && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
          <div ref={popupRef} className="max-w-md w-full mx-4">
            <Card className="glass-card border-border">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Palette className="w-5 h-5" />
                    Customize Color
                  </CardTitle>
                  <button
                    onClick={() => setShowColorPicker(false)}
                    className="text-muted-foreground hover:text-foreground transition-colors"
                    aria-label="Close"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
                <CardDescription>
                  Choose your custom accent color
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex flex-col items-center gap-4">
                  {/* Color Picker Input */}
                  <div className="relative w-full">
                    <input
                      type="color"
                      value={tempColor}
                      onChange={(e) => handleColorChange(e.target.value)}
                      className="w-full h-32 rounded-lg cursor-pointer border-2 border-border"
                      style={{
                        WebkitAppearance: 'none',
                        MozAppearance: 'none',
                        appearance: 'none',
                      }}
                    />
                  </div>
                  
                  {/* Color Preview */}
                  <div className="w-full p-4 rounded-lg border-2 border-border flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div 
                        className="w-12 h-12 rounded-lg border-2 border-border"
                        style={{ backgroundColor: tempColor }}
                      />
                      <div>
                        <p className="text-sm font-medium">Selected Color</p>
                        <p className="text-xs text-muted-foreground font-mono">{tempColor.toUpperCase()}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex gap-2 pt-2">
                  <Button
                    variant="outline"
                    className="flex-1"
                    onClick={() => setShowColorPicker(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    className="flex-1"
                    onClick={handleApplyCustomColor}
                  >
                    Apply
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
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

