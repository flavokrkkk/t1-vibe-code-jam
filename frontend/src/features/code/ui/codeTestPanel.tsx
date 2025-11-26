import { cn } from "@/shared/lib/mergeClass";
import { getResultDisplay, getResultIcon } from "../lib/constants";
import {
  CodeTestResultStatus,
  TestCase,
} from "@/entities/interview/types/types";
import { useRunCodeTests } from "@/entities/interview/hooks/useRunCodeTests";
import { useSubmitCodeToStep } from "@/entities/interview/hooks/useSubmitCodeToStep";
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
}) => {
  const activeCase = testCases.find((tc) => tc.id === activeTestId);

  const { mutate: runCodeTests, isPending: isRunningTests } = useRunCodeTests();
  const { mutate: submitCodeToStep, isPending: isSubmittingCode } =
    useSubmitCodeToStep();

  const [testResult, setTestResult] = useState<string | null>(null);

  const isLoading = isAILoading || isRunningTests || isSubmittingCode;

  useEffect(() => {
    setTestResult(null);
  }, [sourceCode, activeTestId]);

  const handleRunTests = () => {
    if (!sourceCode || testCases.length === 0) return;

    const testCasesForApi = testCases.map((tc) => ({
      input: tc.input,
      expected_output: tc.expected_output,
    }));

    runCodeTests(
      {
        sourceCode,
        language,
        testCases: testCasesForApi,
      },
      {
        onSuccess: (result) => {
          setTestResult(result);
        },
        onError: (error) => {
          console.error("Error running tests:", error);
          setTestResult(`Ошибка: ${error.message}`);
        },
      }
    );
  };

  const handleSubmitCode = () => {
    if (!sourceCode) return;

    submitCodeToStep(
      {
        interviewId,
        stepId,
        userCode: sourceCode,
      },
      {
        onSuccess: () => {
          onRunTests();
        },
        onError: (error) => {
          console.error("Error submitting code:", error);
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
                <div className="bg-zinc-100 p-3 rounded-lg min-h-[70px] flex items-center border border-zinc-200">
                  {testResult ? (
                    <pre className="text-sm whitespace-pre-wrap">
                      {testResult}
                    </pre>
                  ) : (
                    getResultDisplay(testResults[activeTestId])
                  )}
                </div>
              </div>

              <div>
                <h3 className="text-md font-semibold mb-2 text-indigo-700">
                  Expected Output:
                </h3>
                <div className="bg-zinc-100 p-3 rounded-lg font-mono text-sm overflow-x-auto border border-zinc-200 text-zinc-800">
                  <pre>{JSON.stringify(activeCase.expected_output)}</pre>
                </div>
              </div>
            </div>
          </section>
        ) : (
          <div className="text-gray-500 text-center py-8 h-full flex flex-col justify-center items-center">
            <p className="mb-1">Тестовый случай не выбран.</p>
            <p>Пожалуйста, выберите тестовый случай или добавьте новый.</p>
            {/* <button
              disabled={isAILoading}
              className={cn(
                "mt-4 px-4 py-2.5 cursor-pointer bg-blue-600 hover:bg-blue-700 text-white rounded-3xl",
                isAILoading && "opacity-50 cursor-not-allowed"
              )}
            >
              Добавить первый тестовый случай
            </button> */}
          </div>
        )}

        <div className="flex space-x-2 justify-end text-right border-t absolute border-zinc-200 bg-zinc-50 w-full bottom-0 right-0 p-2">
          <button
            onClick={handleRunTests}
            disabled={isLoading || !sourceCode || testCases.length === 0}
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
            {isSubmittingCode ? "Отправка..." : "Отправить код"}
          </button>
        </div>
      </div>
    </div>
  );
};
