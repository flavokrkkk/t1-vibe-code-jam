import React, { createContext, useContext, useState, useCallback } from "react";
import { useAntiCheatDetection } from "./useAntiCheatDetection";
import { getWarnings, addWarning } from "./storage";
import type { AntiCheatViolation, AntiCheatWarning } from "./types";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/shared/ui/dialog/dialog";

interface AntiCheatContextValue {
  warnings: number;
  showWarning: (violation: AntiCheatViolation) => void;
  clearWarnings: () => void;
}

const AntiCheatContext = createContext<AntiCheatContextValue | null>(null);

interface AntiCheatProviderProps {
  interviewId: string;
  children: React.ReactNode;
  onWarning?: (warning: AntiCheatWarning) => void;
  enabled?: boolean;
}

export const AntiCheatProvider: React.FC<AntiCheatProviderProps> = ({
  interviewId,
  children,
  onWarning,
  enabled = true,
}) => {
  const [warnings, setWarnings] = useState(() => getWarnings(interviewId));
  const [currentViolation, setCurrentViolation] =
    useState<AntiCheatViolation | null>(null);

  const handleViolation = useCallback(
    (violation: AntiCheatViolation) => {
      if (!enabled) return;

      const newWarningCount = addWarning(interviewId);
      setWarnings(newWarningCount);

      const warning: AntiCheatWarning = {
        violation,
        warningNumber: newWarningCount,
      };

      onWarning?.(warning);
      setCurrentViolation(violation);
    },
    [enabled, interviewId, onWarning]
  );

  const clearWarnings = useCallback(() => {
    setWarnings(0);
    setCurrentViolation(null);
  }, []);

  useAntiCheatDetection({
    interviewId,
    onViolation: handleViolation,
    enabled,
  });

  const value: AntiCheatContextValue = {
    warnings,
    showWarning: handleViolation,
    clearWarnings,
  };

  return (
    <AntiCheatContext.Provider value={value}>
      {children}
      {currentViolation && (
        <WarningDialog
          violation={currentViolation}
          warningNumber={warnings}
          onClose={() => setCurrentViolation(null)}
        />
      )}
    </AntiCheatContext.Provider>
  );
};

export const useAntiCheat = (): AntiCheatContextValue => {
  const context = useContext(AntiCheatContext);
  if (!context) {
    throw new Error("useAntiCheat must be used within AntiCheatProvider");
  }
  return context;
};

interface WarningDialogProps {
  violation: AntiCheatViolation;
  warningNumber: number;
  onClose: () => void;
}

const WarningDialog: React.FC<WarningDialogProps> = ({
  violation,
  onClose,
}) => {
  const getViolationMessage = (type: AntiCheatViolation["type"]): string => {
    switch (type) {
      case "TAB_SWITCH":
        return "Обнаружено переключение на другую вкладку";
      case "WINDOW_BLUR":
        return "Окно браузера потеряло фокус";
      case "DEVTOOLS_OPEN":
        return "Обнаружено открытие инструментов разработчика";
      case "COPY_PASTE":
        return "Копирование и вставка заблокированы";
      case "CONTEXT_MENU":
        return "Контекстное меню заблокировано";
      case "SCREENSHOT":
        return "Попытка сделать скриншот заблокирована";
      default:
        return "Обнаружено нарушение правил";
    }
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-md rounded-3xl border-0 bg-white p-8 shadow-xl animate-in fade-in-50 zoom-in-95">
        <div className="flex flex-col items-center space-y-0">
          <div className="flex justify-center">
            <img
              src="/images/alert-2.png"
              alt="Предупреждение"
              className="w-28 h-28 object-contain"
            />
          </div>

          <DialogHeader className="space-y-2 text-center flex flex-col items-center mb-6">
            <DialogTitle className="text-2xl font-bold tracking-tight text-gray-900 text-center w-full">
              Предупреждение
            </DialogTitle>
            <DialogDescription className="text-gray-700 leading-relaxed text-base text-center w-full">
              {getViolationMessage(violation.type)}
            </DialogDescription>
          </DialogHeader>
          {/* 
          <div className="w-full flex justify-center">
            <Button
              onClick={onClose}
              className="rounded-xl bg-white text-blue-700 px-7 cursor-pointer py-2.5 border-blue-700 border text-sm font-medium shadow-md hover:bg-zinc-100 focus:ring-2 focus:ring-blue-300"
            >
              Понятно
            </Button>
          </div> */}
        </div>
      </DialogContent>
    </Dialog>
  );
};
