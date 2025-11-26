import { CodeTestResult, TestCase } from "@/entities/interview/types/types";
import CodeEditor from "./codeEditor";
import { ChevronUp } from "lucide-react";
import { TestPanel } from "./codeTestPanel";
import { cn } from "@/shared/lib/mergeClass";
import { useCodeTaskTests } from "../hooks/useCodeTaskTests";
import { useEditorPanelLayout } from "../hooks/useEditorPanelLayout";

interface TaskCodeEditorProps {
  isAILoading: boolean;
  initialCode: string;
  language: string;
  testCases: TestCase[];
  currentTestResults: CodeTestResult[];
  onCodeChange: (newCode: string | undefined) => void;
  onRunTests: () => void;
  sourceCode: string;
  interviewId: string;
  stepId: string;
}

export const TaskCodeEditor: React.FC<TaskCodeEditorProps> = ({
  isAILoading,
  initialCode,
  language,
  testCases,
  currentTestResults,
  onCodeChange,
  onRunTests,
  sourceCode,
  interviewId,
  stepId,
}) => {
  const {
    isCodeEditorMaximized,
    isTestPanelFolded,
    editorHeight,
    testPanelHeight,
    handleToggleMaximizeEditor,
    handleToggleFoldTestPanel,
  } = useEditorPanelLayout();

  const { activeTestId, setActiveTestId, mappedTestResults } = useCodeTaskTests(
    {
      testCases,
      currentTestResults: currentTestResults,
    }
  );

  return (
    <div className="flex flex-col h-full p-0 space-y-2">
      <CodeEditor
        initialCode={initialCode}
        language={language}
        onCodeChange={onCodeChange}
        isMaximized={isCodeEditorMaximized}
        onToggleMaximize={handleToggleMaximizeEditor}
        editorHeight={editorHeight}
      />
      {!isCodeEditorMaximized && (
        <div
          className="bg-zinc-300 text-white mt-0 shadow-lg flex flex-col transition-all duration-300 ease-in-out rounded-2xl"
          style={{ height: testPanelHeight }}
        >
          <div
            className={cn(
              "flex justify-between items-center bg-[#3d66ff] rounded-t-[22px] transition-colors ease-in-out px-4 py-2",
              isTestPanelFolded && "rounded-[22px]"
            )}
          >
            <div className="flex items-center gap-2">
              <span className="text-sm">Тесты</span>
            </div>
            <button
              onClick={handleToggleFoldTestPanel}
              className="p-1 rounded-xl bg-white text-indigo-400 transition-colors cursor-pointer"
              title={isTestPanelFolded ? "Развернуть" : "Свернуть"}
              disabled={isAILoading}
            >
              <ChevronUp
                size={18}
                className={cn(
                  "transition-transform duration-300",
                  isTestPanelFolded && "rotate-180"
                )}
              />
            </button>
          </div>

          {!isTestPanelFolded && (
            <div className="flex-grow overflow-auto custom-scrollbar bg-white rounded-b-2xl h-full">
              <TestPanel
                isAILoading={isAILoading}
                testCases={testCases}
                activeTestId={activeTestId}
                testResults={mappedTestResults}
                setActiveTestId={setActiveTestId}
                onRunTests={onRunTests}
                sourceCode={sourceCode}
                language={language}
                interviewId={interviewId}
                stepId={stepId}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
};
