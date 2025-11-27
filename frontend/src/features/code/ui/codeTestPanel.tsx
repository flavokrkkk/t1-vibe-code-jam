import { cn } from "@/shared/lib/mergeClass";
import { getResultDisplay, getResultIcon } from "../lib/constants";
import {
  CodeTestResultStatus,
  TestCase,
} from "@/entities/interview/types/types";
import { useRunCodeTests } from "@/entities/interview/hooks/useRunCodeTests";
import { useSkipStep } from "@/entities/interview/hooks/useSkipStep";
import { useState, useEffect } from "react";

interface TestPanelProps {
  isAILoading: boolean;
  testCases: TestCase[];
  activeTestId: string;
  setActiveTestId: (id: string) => void;
  testResults: { [key: string]: CodeTestResultStatus };
  onRunTests: () => void;
  sourceCode: string;
  language: string;
  interviewId: string;
  stepId: string;
  codeTaskId: string;
}

export const TestPanel: React.FC<TestPanelProps> = ({
  isAILoading,
  testCases,
  activeTestId,
  testResults,
  onRunTests,
  setActiveTestId,
  sourceCode,
  language,
  interviewId,
  stepId,
  codeTaskId,
}) => {
  const activeCase = testCases.find((tc) => tc.id === activeTestId);

  const { mutate: runCodeTests, isPending: isRunningTests } = useRunCodeTests();
  const { mutate: skipStep, isPending: isSkippingStep } = useSkipStep();

  const [testResult, setTestResult] = useState<{
    all_passed: boolean;
    results: Array<{
      passed: boolean;
      status: string | null;
      stdout: string;
      stderr: string;
      expected: string;
    }>;
  } | null>(null);

  const isLoading = isAILoading || isRunningTests || isSkippingStep;

  useEffect(() => {
    setTestResult(null);
  }, [sourceCode, activeTestId]);

  const handleRunTests = () => {
    if (!sourceCode || !codeTaskId) return;

    runCodeTests(
      {
        sourceCode,
        language,
        codeTaskId,
      },
      {
        onSuccess: (result) => {
          setTestResult(result);
        },
        onError: (error) => {
          console.error("Error running tests:", error);
          setTestResult({
            all_passed: false,
            results: [
              {
                passed: false,
                status: "error",
                stdout: "",
                stderr: error.message,
                expected: "",
              },
            ],
          });
        },
      }
    );
  };

  const handleSubmitCode = () => {
    if (!sourceCode) return;

    onRunTests();
  };

  const handleSkipStep = () => {
    skipStep(
      {
        interviewId,
        stepId,
      },
      {
        onError: (error) => {
          console.error("Error skipping step:", error);
        },
      }
    );
  };

  return (
    <div className="flex flex-col bg-white relative text-zinc-800 rounded-lg shadow-md border border-zinc-200 h-full">
      <div className="flex items-center gap-2 px-4 py-2 border-b border-zinc-200 bg-zinc-50">
        {testCases.map((tc, index) => (
          <button
            key={tc.id}
            className={cn(
              "p-2 text-sm cursor-pointer flex items-center gap-1 whitespace-nowrap transition-colors duration-200",
              tc.id === activeTestId
                ? "text-blue-600 border-b-2 border-blue-600 font-semibold"
                : "text-zinc-500 hover:text-zinc-800 border-b-2 border-transparent hover:border-zinc-300"
            )}
            onClick={() => setActiveTestId(tc.id)}
            disabled={isLoading}
          >
            {testResults[tc.id] && getResultIcon(testResults[tc.id])}
            Case {index + 1}
          </button>
        ))}
      </div>
      <div className="flex-grow px-4 pt-3 bg-white overflow-y-auto mb-16">
        {activeCase ? (
          <section className="h-full flex flex-col justify-between">
            <div className="space-y-4">
              <div>
                <h3 className="text-md font-semibold mb-2 text-indigo-700">
                  Input:
                </h3>
                <div className="bg-zinc-100 p-3 rounded-lg font-mono text-sm overflow-x-auto border border-zinc-200 text-zinc-800">
                  <pre>{JSON.stringify(activeCase.input)}</pre>
                </div>
              </div>

              <div>
                <h3 className="text-md font-semibold mb-2 text-indigo-700">
                  Test Result:
                </h3>
                <div className="bg-zinc-100 p-3 rounded-lg min-h-[70px] border border-zinc-200">
                  {testResult ? (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 mb-2">
                        <span
                          className={cn(
                            "px-2 py-1 rounded text-xs font-medium",
                            testResult.all_passed
                              ? "bg-green-100 text-green-800"
                              : "bg-red-100 text-red-800"
                          )}
                        >
                          {testResult.all_passed
                            ? "Все тесты пройдены"
                            : "Тесты не пройдены"}
                        </span>
                        <span className="text-xs text-zinc-600">
                          {testResult.results.filter((r) => r.passed).length} /{" "}
                          {testResult.results.length} пройдено
                        </span>
                      </div>
                      {(() => {
                        const activeIndex = testCases.findIndex(
                          (tc) => tc.id === activeTestId
                        );
                        if (
                          activeIndex === -1 ||
                          !testResult.results[activeIndex]
                        ) {
                          return null;
                        }
                        const result = testResult.results[activeIndex];

                        return (
                          <div
                            className={cn(
                              "p-2 rounded text-xs",
                              result.passed
                                ? "bg-green-50 border border-green-200"
                                : "bg-red-50 border border-red-200"
                            )}
                          >
                            <div className="font-medium mb-1">
                              {result.passed ? "✓ Пройден" : "✗ Не пройден"}
                            </div>
                            {result.stderr && (
                              <div className="text-red-600 mb-1">
                                <span className="font-medium">Ошибка:</span>{" "}
                                {result.stderr}
                              </div>
                            )}
                            {result.stdout && (
                              <div className="text-zinc-700 mb-1">
                                <span className="font-medium">Вывод:</span>{" "}
                                {result.stdout}
                              </div>
                            )}
                            {result.expected && (
                              <div className="text-zinc-600">
                                <span className="font-medium">Ожидалось:</span>{" "}
                                {result.expected}
                              </div>
                            )}
                          </div>
                        );
                      })()}
                    </div>
                  ) : (
                    <div className="flex items-center h-full">
                      {getResultDisplay(testResults[activeTestId])}
                    </div>
                  )}
                </div>
              </div>

              <div>
                <h3 className="text-md font-semibold mb-2 text-indigo-700">
                  Expected Output:
                </h3>
                <div className="bg-zinc-100 p-3 rounded-lg font-mono text-sm overflow-x-auto border border-zinc-200 text-zinc-800">
                  {(() => {
                    const formattedExpected =
                      typeof activeCase.expected_output === "string"
                        ? activeCase.expected_output
                        : JSON.stringify(activeCase.expected_output, null, 2);

                    const activeIndex = testCases.findIndex(
                      (tc) => tc.id === activeTestId
                    );
                    const runnerExpected =
                      testResult && activeIndex !== -1
                        ? testResult.results[activeIndex]?.expected
                        : null;

                    return (
                      <>
                        <div className="mb-2">
                          <div className="text-xs text-zinc-500 mb-1">
                            Эталонное ожидаемое значение из тесткейса:
                          </div>
                          <pre>{formattedExpected}</pre>
                        </div>
                        {runnerExpected &&
                          runnerExpected !== formattedExpected && (
                            <div className="mt-2 border-t border-zinc-200 pt-2 text-xs text-zinc-700">
                              <div className="font-semibold mb-1">
                                Ожидалось по результатам прогона:
                              </div>
                              <pre>{runnerExpected}</pre>
                            </div>
                          )}
                      </>
                    );
                  })()}
                </div>
              </div>
            </div>
          </section>
        ) : (
          <div className="text-gray-500 text-center py-8 h-full flex flex-col justify-center items-center">
            <p className="mb-1">Тестовый случай не выбран.</p>
            <p>Пожалуйста, выберите тестовый случай или добавьте новый.</p>
          </div>
        )}

        <div className="flex space-x-2 justify-between items-center border-t absolute border-zinc-200 bg-zinc-50 w-full bottom-0 right-0 p-2">
          <button
            onClick={handleSkipStep}
            disabled={isLoading}
            className={cn(
              "px-6 py-2 rounded-3xl text-white font-medium transition-colors duration-200 cursor-pointer",
              "bg-zinc-500 hover:bg-zinc-700",
              isLoading && "opacity-50 cursor-not-allowed bg-zinc-700"
            )}
          >
            {isSkippingStep ? "Пропуск..." : "Пропустить"}
          </button>
          <div className="flex space-x-2">
            <button
              onClick={handleRunTests}
              disabled={isLoading || !sourceCode || !codeTaskId}
              className={cn(
                "px-6 py-2 rounded-3xl text-white font-medium transition-colors duration-200 cursor-pointer",
                "bg-white border text-blue-700 border-blue-700",
                (isLoading || !activeCase || !sourceCode) &&
                  "cursor-not-allowed opacity-35"
              )}
            >
              {isRunningTests ? "Running Tests..." : "Запустить тесты"}
            </button>
            <button
              onClick={handleSubmitCode}
              disabled={isLoading || !sourceCode}
              className={cn(
                "px-6 py-2 rounded-3xl text-white font-medium transition-colors duration-200 cursor-pointer",
                "bg-blue-500 hover:bg-blue-700",
                isLoading && "opacity-50 cursor-not-allowed bg-blue-700"
              )}
            >
              {isAILoading ? "Отправка..." : "Отправить код"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
