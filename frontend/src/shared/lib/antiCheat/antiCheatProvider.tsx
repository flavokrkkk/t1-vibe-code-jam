import React, { createContext, useContext, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAntiCheatDetection } from "./useAntiCheatDetection";
import {
  getWarnings,
  addWarning,
  hasReachedMaxWarnings,
  MAX_WARNINGS_COUNT,
} from "./storage";
import type { AntiCheatViolation, AntiCheatWarning } from "./types";
import { ERouteNames } from "@/shared/lib/routeVariables";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/shared/ui/dialog/dialog";
import { Button } from "@/shared/ui/button/button";
import { cn } from "@/shared/lib/mergeClass";

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
  const navigate = useNavigate();
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

      if (hasReachedMaxWarnings(interviewId)) {
        setTimeout(() => {
          navigate(`/${ERouteNames.DASHBOARD_ROUTE}`, { replace: true });
        }, 2000);
      }
    },
    [enabled, interviewId, navigate, onWarning]
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
  warningNumber,
  onClose,
}) => {
  const isMaxWarnings = warningNumber >= MAX_WARNINGS_COUNT;

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

          <DialogHeader className="space-y-2 text-center flex flex-col items-center">
            <DialogTitle className="text-2xl font-bold tracking-tight text-gray-900 text-center w-full">
              {isMaxWarnings
                ? "Превышен лимит предупреждений"
                : "Предупреждение"}
            </DialogTitle>
            <DialogDescription className="text-gray-700 leading-relaxed text-sm text-center w-full">
              {getViolationMessage(violation.type)}
            </DialogDescription>
          </DialogHeader>

          <div className="w-full text-center space-y-2 mb-4">
            <p
              className={cn(
                "text-base",
                isMaxWarnings ? "text-red-600" : "text-yellow-600"
              )}
            >
              {warningNumber} из {MAX_WARNINGS_COUNT}
            </p>
          </div>

          <div className="w-full flex justify-center">
            <Button
              onClick={onClose}
              className="rounded-xl bg-white text-blue-700 px-7 cursor-pointer py-2.5 border-blue-700 border text-sm font-medium shadow-md hover:bg-zinc-100 focus:ring-2 focus:ring-blue-300"
            >
              Понятно
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
