import { cn } from "@/shared/lib/mergeClass";
import { getResultDisplay, getResultIcon } from "../lib/constants";
import {
  CodeTestResultStatus,
  TestCase,
} from "@/entities/interview/types/types";

interface TestPanelProps {
  isAILoading: boolean;
  testCases: TestCase[];
  activeTestId: string;
  setActiveTestId: (id: string) => void;
  testResults: { [key: string]: CodeTestResultStatus };
  onRunTests: () => void;
}

export const TestPanel: React.FC<TestPanelProps> = ({
  isAILoading,
  testCases,
  activeTestId,
  testResults,
  onRunTests,
  setActiveTestId,
}) => {
  const activeCase = testCases.find((tc) => tc.id === activeTestId);

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
            disabled={isAILoading}
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
                  {getResultDisplay(testResults[activeTestId])}
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
            <div className="flex space-x-2 justify-end text-right border-t absolute border-zinc-200 bg-zinc-50 w-full bottom-0 right-0 p-2">
              <button
                onClick={onRunTests}
                disabled={isAILoading}
                className={cn(
                  "px-6 py-2 rounded-lg text-white font-medium transition-colors duration-200 cursor-pointer",
                  "bg-white border text-blue-700 border-blue-700",
                  isAILoading && "opacity-50 cursor-not-allowed bg-blue-700"
                )}
              >
                {isAILoading ? "Running Tests..." : "Запустить тесты"}
              </button>
              <button
                onClick={onRunTests}
                disabled={isAILoading}
                className={cn(
                  "px-6 py-2 rounded-lg text-white font-medium transition-colors duration-200 cursor-pointer",
                  "bg-blue-500 hover:bg-blue-700",
                  isAILoading && "opacity-50 cursor-not-allowed bg-blue-700"
                )}
              >
                {isAILoading ? "Отправка..." : "Отправить код"}
              </button>
            </div>
          </section>
        ) : (
          <div className="text-gray-500 text-center py-8">
            <p className="mb-2">No test case selected.</p>
            <p>Please select a test case or add a new one.</p>
            <button
              disabled={isAILoading}
              className={cn(
                "mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md",
                isAILoading && "opacity-50 cursor-not-allowed"
              )}
            >
              Add First Test Case
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
