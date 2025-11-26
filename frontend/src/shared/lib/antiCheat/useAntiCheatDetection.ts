import { useEffect, useRef, useCallback } from "react";
import type { AntiCheatViolation } from "./types";

interface UseAntiCheatDetectionOptions {
  interviewId: string;
  onViolation: (violation: AntiCheatViolation) => void;
  enabled?: boolean;
}

export const useAntiCheatDetection = ({
  interviewId,
  onViolation,
  enabled = true,
}: UseAntiCheatDetectionOptions) => {
  const devToolsOpenRef = useRef<boolean>(false);

  const reportViolation = useCallback(
    (violation: AntiCheatViolation) => {
      if (!enabled) return;
      onViolation(violation);
    },
    [enabled, onViolation]
  );

  // Отслеживание переключения вкладок
  useEffect(() => {
    if (!enabled) return;

    const handleVisibilityChange = () => {
      if (document.hidden) {
        reportViolation({
          type: "TAB_SWITCH",
          timestamp: new Date().toISOString(),
          details: "Пользователь переключился на другую вкладку",
        });
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [enabled, reportViolation]);

  // Отслеживание потери фокуса окна
  useEffect(() => {
    if (!enabled) return;

    const handleBlur = () => {
      reportViolation({
        type: "WINDOW_BLUR",
        timestamp: new Date().toISOString(),
        details: "Окно браузера потеряло фокус",
      });
    };

    window.addEventListener("blur", handleBlur);
    return () => {
      window.removeEventListener("blur", handleBlur);
    };
  }, [enabled, reportViolation]);
  console.log(interviewId);
  // Отслеживание DevTools
  useEffect(() => {
    if (!enabled) return;

    const checkDevTools = () => {
      const widthThreshold = window.outerWidth - window.innerWidth > 160;
      const heightThreshold = window.outerHeight - window.innerHeight > 160;

      if ((widthThreshold || heightThreshold) && !devToolsOpenRef.current) {
        devToolsOpenRef.current = true;
        reportViolation({
          type: "DEVTOOLS_OPEN",
          timestamp: new Date().toISOString(),
          details: "Обнаружено открытие DevTools",
        });
      } else if (!widthThreshold && !heightThreshold) {
        devToolsOpenRef.current = false;
      }
    };

    const interval = setInterval(checkDevTools, 1000);
    return () => clearInterval(interval);
  }, [enabled, reportViolation]);

  // Блокировка копирования/вставки
  useEffect(() => {
    if (!enabled) return;

    const handleCopy = (e: ClipboardEvent) => {
      e.preventDefault();
      reportViolation({
        type: "COPY_PASTE",
        timestamp: new Date().toISOString(),
        details: "Попытка копирования текста",
      });
      return false;
    };

    const handlePaste = (e: ClipboardEvent) => {
      e.preventDefault();
      reportViolation({
        type: "COPY_PASTE",
        timestamp: new Date().toISOString(),
        details: "Попытка вставки текста",
      });
      return false;
    };

    const handleCut = (e: ClipboardEvent) => {
      e.preventDefault();
      reportViolation({
        type: "COPY_PASTE",
        timestamp: new Date().toISOString(),
        details: "Попытка вырезания текста",
      });
      return false;
    };

    document.addEventListener("copy", handleCopy);
    document.addEventListener("paste", handlePaste);
    document.addEventListener("cut", handleCut);

    return () => {
      document.removeEventListener("copy", handleCopy);
      document.removeEventListener("paste", handlePaste);
      document.removeEventListener("cut", handleCut);
    };
  }, [enabled, reportViolation]);

  // Блокировка контекстного меню
  useEffect(() => {
    if (!enabled) return;

    const handleContextMenu = (e: MouseEvent) => {
      e.preventDefault();
      reportViolation({
        type: "CONTEXT_MENU",
        timestamp: new Date().toISOString(),
        details: "Попытка открыть контекстное меню",
      });
      return false;
    };

    document.addEventListener("contextmenu", handleContextMenu);
    return () => {
      document.removeEventListener("contextmenu", handleContextMenu);
    };
  }, [enabled, reportViolation]);

  // Блокировка выделения текста
  useEffect(() => {
    if (!enabled) return;

    const handleSelectStart = (e: Event) => {
      e.preventDefault();
      return false;
    };

    const handleDragStart = (e: DragEvent) => {
      e.preventDefault();
      return false;
    };

    document.addEventListener("selectstart", handleSelectStart);
    document.addEventListener("dragstart", handleDragStart);

    return () => {
      document.removeEventListener("selectstart", handleSelectStart);
      document.removeEventListener("dragstart", handleDragStart);
    };
  }, [enabled]);

  // Отслеживание скриншотов (PrintScreen)
  useEffect(() => {
    if (!enabled) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "PrintScreen") {
        e.preventDefault();
        reportViolation({
          type: "SCREENSHOT",
          timestamp: new Date().toISOString(),
          details: "Попытка сделать скриншот",
        });
        return false;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [enabled, reportViolation]);

  // Блокировка F12 и других горячих клавиш DevTools
  useEffect(() => {
    if (!enabled) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (
        e.key === "F12" ||
        (e.ctrlKey && e.shiftKey && (e.key === "I" || e.key === "J")) ||
        (e.ctrlKey && e.key === "U")
      ) {
        e.preventDefault();
        reportViolation({
          type: "DEVTOOLS_OPEN",
          timestamp: new Date().toISOString(),
          details: `Попытка открыть DevTools (${e.key})`,
        });
        return false;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [enabled, reportViolation]);
};
