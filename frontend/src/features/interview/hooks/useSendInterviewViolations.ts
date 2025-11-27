import { useEffect, useRef } from "react";
import { useBanInterview } from "@/entities/interview/hooks/useBanInterview";
import { getViolations } from "@/shared/lib/antiCheat/storage";
import type { AntiCheatViolationType } from "@/shared/lib/antiCheat/types";

const getViolationReason = (type: string): string => {
  const violationMap: Record<AntiCheatViolationType, string> = {
    TAB_SWITCH: "Переключение на другую вкладку",
    WINDOW_BLUR: "Потеря фокуса окна браузера",
    DEVTOOLS_OPEN: "Открытие инструментов разработчика",
    COPY_PASTE: "Копирование и вставка",
    CONTEXT_MENU: "Открытие контекстного меню",
    SCREENSHOT: "Попытка сделать скриншот",
  };
  return violationMap[type as AntiCheatViolationType] || "Нарушение правил";
};

export const useSendInterviewViolations = (interviewId: string) => {
  const banInterviewMutation = useBanInterview();
  const hasSentViolations = useRef(false);

  useEffect(() => {
    if (hasSentViolations.current) return;

    const violations = getViolations(interviewId);
    if (violations.length > 0) {
      const uniqueViolationTypes = Array.from(
        new Set(violations.map((v) => v.type))
      );
      const reasons = uniqueViolationTypes.map((type) =>
        getViolationReason(type)
      );

      banInterviewMutation.mutate({
        interviewId,
        reasons,
      });

      hasSentViolations.current = true;
    }
  }, [interviewId, banInterviewMutation]);
};

