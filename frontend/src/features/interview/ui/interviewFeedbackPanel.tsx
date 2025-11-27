import { Interview } from "@/entities/interview/types/types";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/shared/ui/select/select";
import React, { useMemo, useState } from "react";
import { useSendInterviewViolations } from "../hooks/useSendInterviewViolations";

interface FeedbackPanelProps {
  interview: Interview;
}

const FeedbackPanel: React.FC<FeedbackPanelProps> = ({ interview }) => {
  const [selectStepId, setSelectStepId] = useState(
    interview.steps[0]?.id || ""
  );

  useSendInterviewViolations(interview.id);

  const currentStep = useMemo(() => {
    return interview.steps.find((step) => step.id === selectStepId);
  }, [selectStepId]);

  const dialogSteps = interview.steps.filter(
    (step) => step.type === "DIALOG" && step.score !== null
  );
  const codeTaskSteps = interview.steps.filter(
    (step) => step.type === "CODE_TASK" && step.score !== null
  );

  const averageDialogScore =
    dialogSteps.length > 0
      ? dialogSteps.reduce((sum, step) => sum + (step.score || 0), 0) /
        dialogSteps.length
      : 0;

  const averageCodeScore =
    codeTaskSteps.length > 0
      ? codeTaskSteps.reduce((sum, step) => sum + (step.code_score || 0), 0) /
        codeTaskSteps.length
      : 0;

  return (
    <div className="overflow-y-auto flex custom-scrollbar w-full items-center text-gray-800 h-full">
      <div className="min-w-1/3 max-w-1/3 h-full p-4">
        <section className="w-full h-full border-t flex flex-col space-y-4 p-4 bg-[#3d66ff] rounded-3xl">
          <Select value={selectStepId} onValueChange={setSelectStepId}>
            <SelectTrigger className="w-full cursor-pointer rounded-xl bg-white text-blue-500 border-0 text-[13px] focus:ring-1 focus:ring-blue-500 py-6 px-3">
              <SelectValue placeholder="Выбрать роль" />
            </SelectTrigger>
            <SelectContent className="bg-white text-blue-700 rounded-xl border-0">
              {interview.steps.map((step, i) => (
                <SelectItem
                  key={step.id}
                  value={step.id}
                  className="p-3 rounded-xl cursor-pointer"
                >
                  Вопрос {i + 1}/{interview.steps.length}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {currentStep && (
            <div className="bg-white p-5 rounded-3xl shadow-md border border-gray-200 flex flex-col  overflow-auto">
              <h4 className="text-lg font-bold mb-2">
                Шаг {1 + 1}:{" "}
                {currentStep.type === "DIALOG"
                  ? "Диалоговый Вопрос"
                  : "Кодовая Задача"}
              </h4>
              {currentStep.question_text && (
                <p className="text-gray-600 text-sm mb-2 italic">
                  Вопрос: {currentStep.question_text}
                </p>
              )}
              {currentStep.user_answer && (
                <p className="text-gray-700 text-sm mb-2">
                  Ваш ответ: {currentStep.user_answer}
                </p>
              )}
              {currentStep.user_code && (
                <div className="bg-gray-100 p-3 rounded-md text-sm font-mono my-2">
                  <h5 className="font-semibold mb-1">Ваш код:</h5>
                  <pre className="whitespace-pre-wrap break-words">
                    {currentStep.user_code}
                  </pre>
                </div>
              )}
              {currentStep.score !== null && (
                <p className="text-md font-semibold mt-auto pt-2">
                  Оценка за шаг:{" "}
                  <span className="text-green-600">
                    {currentStep.score}/100
                  </span>
                </p>
              )}
              {(() => {
                const feedbackText =
                  currentStep.type === "CODE_TASK"
                    ? currentStep.code_feedback || currentStep.feedback
                    : currentStep.feedback || currentStep.code_feedback;

                if (!feedbackText) return null;

                return (
                  <div className="mt-2 text-sm text-gray-800 bg-blue-50 p-3 rounded-md">
                    <h5 className="font-semibold text-blue-800">Фидбэк AI:</h5>
                    <p className="whitespace-pre-wrap">{feedbackText}</p>
                  </div>
                );
              })()}
              {currentStep.code_test_results &&
                currentStep.code_test_results.length > 0 && (
                  <div className="mt-2 text-sm">
                    <h5 className="font-semibold">Результаты тестов:</h5>
                    <ul className="list-disc list-inside ml-2">
                      {currentStep.code_test_results.map((test) => (
                        <li
                          key={test.test_id}
                          className={
                            test.status === "PASSED"
                              ? "text-green-600"
                              : "text-red-600"
                          }
                        >
                          {test.test_id}: {test.status}{" "}
                          {test.details && `(${test.details})`}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
            </div>
          )}
        </section>
      </div>

      <section className="w-full h-full overflow-auto p-4 space-y-4">
        <div className="bg-gradient-to-r from-blue-300 to-[#3d66ff] p-6 rounded-3xl text-white text-center">
          <h3 className="text-xl font-semibold mb-2">Общий балл</h3>
          <p className="text-5xl font-extrabold">
            {interview.total_score ?? 80}/100
          </p>
          <p className="text-lg mt-2">
            {interview.overall_feedback
              ? "Интервью завершено с общей оценкой"
              : "Общая оценка доступна."}
          </p>
        </div>
        {interview.overall_feedback && (
          <div className="bg-white p-6 rounded-3xl border border-blue-400">
            <h3 className="text-xl font-semibold mb-3">Общий отзыв</h3>
            <p className="text-gray-700 whitespace-pre-wrap">
              {interview.overall_feedback}
            </p>
          </div>
        )}
        <h3 className="text-2xl font-bold text-center mt-6 mb-4">
          Аналитика производительности
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white p-5 rounded-3xl border border-blue-400">
            <h4 className="text-lg font-bold text-gray-700 mb-2">
              Средний балл за Диалог
            </h4>
            <p className="text-3xl font-extrabold text-indigo-500">
              {averageDialogScore.toFixed(0)}/100
            </p>
          </div>
          <div className="bg-white p-5 rounded-3xl border border-blue-400">
            <h4 className="text-lg font-bold text-gray-700 mb-2">
              Средний балл за Кодовые Задачи
            </h4>
            <p className="text-3xl font-extrabold text-purple-500">
              {averageCodeScore.toFixed(0)}/100
            </p>
          </div>
          <div className="bg-white p-5 rounded-3xl border border-blue-400">
            <h4 className="text-lg font-bold text-gray-700 mb-2">
              Навыки и области для роста
            </h4>
            <p className="text-gray-700">
              Например: "Кандидат продемонстрировал solid‑ный уровень знаний
              React, но есть пробелы в практической реализации оптимизаций."
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default FeedbackPanel;
