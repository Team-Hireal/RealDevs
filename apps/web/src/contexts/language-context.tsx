"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { Language, getTranslation, Translations } from "@/lib/translations";
import { api } from "@/lib/api";

interface LanguageContextType {
  language: Language;
  setLanguage: (language: Language) => void;
  t: Translations;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

const LANGUAGE_SETTING_KEY = "language";

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<Language>("en");
  const [mounted, setMounted] = useState(false);

  // Load language from settings on mount
  useEffect(() => {
    const loadLanguage = async () => {
      try {
        const settings = await api.getSettings();
        const savedLanguage = settings.settings[LANGUAGE_SETTING_KEY] as Language;
        
        // Validate language code
        const validLanguages: Language[] = ["en", "zh", "fr", "es", "de"];
        if (savedLanguage && validLanguages.includes(savedLanguage)) {
          setLanguageState(savedLanguage);
        }
      } catch (error) {
        console.error("Failed to load language setting:", error);
      } finally {
        setMounted(true);
      }
    };

    loadLanguage();
  }, []);

  const setLanguage = async (newLanguage: Language) => {
    setLanguageState(newLanguage);
    
    // Save to settings
    try {
      await api.updateSetting(LANGUAGE_SETTING_KEY, newLanguage);
    } catch (error) {
      console.error("Failed to save language setting:", error);
    }
  };

  const t = getTranslation(language);

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return context;
}
