import { useEffect, useMemo, useState } from "react";
import type { Interview } from "@/entities/interview/types/types";
import { InterviewStatus } from "@/entities/interview/types/types";

// Хук для вычисления флага завершённого интервью
export const useInterviewCompleted = (interview: Interview) =>
  useMemo(
    () =>
      interview.status === InterviewStatus.COMPLETED ||
      (interview.overall_feedback !== null && interview.total_score !== null),
    [interview]
  );

// Хук таймера интервью
export const useInterviewTimer = (
  interview: Interview,
  isCompleted: boolean
) => {
  const [elapsedTime, setElapsedTime] = useState(0);

  useEffect(() => {
    const interviewStart = new Date(interview.created_at).getTime();

    const updateElapsed = () => {
      const now = Date.now();
      const diffSeconds = Math.max(
        0,
        Math.floor((now - interviewStart) / 1000)
      );
      setElapsedTime(diffSeconds);
    };

    updateElapsed();

    if (isCompleted) {
      return;
    }

    const intervalId = setInterval(updateElapsed, 1000);

    return () => clearInterval(intervalId);
  }, [interview.created_at, isCompleted]);

  const formatted = useMemo(() => {
    const minutes = Math.floor(elapsedTime / 60)
      .toString()
      .padStart(2, "0");
    const seconds = (elapsedTime % 60).toString().padStart(2, "0");
    return `${minutes}:${seconds}`;
  }, [elapsedTime]);

  return { elapsedTime, formatted };
};

// Хук для расчёта прогресса по шагам
export const useInterviewProgress = (interview: Interview) =>
  useMemo(() => {
    const totalTasks = interview.amount_of_tasks;
    const currentStep = interview.current_step_index + 1;
    const progress = Math.min((currentStep / totalTasks) * 100, 100);

    return {
      current: currentStep,
      total: totalTasks,
      percentage: progress,
    };
  }, [interview.amount_of_tasks, interview.current_step_index]);

// Хук для информации о текущей кодовой задаче
export const useCurrentCodeTask = (
  currentStep: Interview["steps"][number] | undefined
) =>
  useMemo(() => {
    const codeTask = currentStep?.code_task;

    return {
      codeTaskData: {
        initialCode: currentStep?.user_code ?? codeTask?.initial_code ?? "",
        language: codeTask?.language ?? "typescript",
        testCases: codeTask?.test_cases ?? [],
      },
      currentTestResults: currentStep?.code_test_results ?? [],
    };
  }, [currentStep]);

// Хук для логики показа индикатора набора
export const useTypingIndicator = (
  interview: Interview,
  isAILoading: boolean
) =>
  useMemo(() => {
    const hasTypingMessage = interview.chat_messages.some(
      (msg) => msg.isTyping
    );

    if (!isAILoading && !hasTypingMessage) return false;

    const lastMessage =
      interview.chat_messages[interview.chat_messages.length - 1];

    const hasLastAnswerWithContent =
      lastMessage &&
      lastMessage.sender === "AI" &&
      lastMessage.text &&
      lastMessage.text.trim() !== "";

    if (hasLastAnswerWithContent && !hasTypingMessage) return false;

    return hasTypingMessage || isAILoading;
  }, [interview.chat_messages, isAILoading]);


