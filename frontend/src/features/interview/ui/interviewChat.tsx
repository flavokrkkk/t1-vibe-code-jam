import { Interview, InterviewStatus } from "@/entities/interview/types/types";
import React, { useState, useRef, useMemo, useEffect } from "react";
import { ChatMessageBubble } from "./interviewChatMessgaeBubble";
import { ChatInput } from "./interviewChatInput";
import { TaskCodeEditor } from "@/features/code/ui/taskCodeEditor";
import { useChatAutoScroll } from "@/shared/hooks/useChatAutoScroll";
import { cn } from "@/shared/lib/mergeClass";
import { useInterviewMessage } from "@/entities/interview/hooks/useInterviewMessage";
import { useCodeSubmit } from "@/entities/interview/hooks/useCodeSubmit";
import FeedbackPanel from "./interviewFeedbackPanel";
import { FileText } from "lucide-react";
import { PDFDownloadLink } from "@react-pdf/renderer";
import { Button } from "@/shared/ui/button/button";
import InterviewReport from "./interviewReport";

interface InterviewChatProps {
  initialInterview: Interview;
}

export const InterviewChat: React.FC<InterviewChatProps> = ({
  initialInterview,
}) => {
  const currentStep =
    initialInterview.steps[initialInterview.current_step_index];

  const isCurrentStepCodeTask = currentStep?.type === "CODE_TASK";

  const [isAILoading] = useState(false);
  const [currentCode, setCurrentCode] = useState(
    currentStep?.user_code ?? currentStep?.code_task?.initial_code ?? ""
  );
  const chatContainerRef = useRef<HTMLDivElement>(null);

  const { mutate: sendMessage } = useInterviewMessage();

  const { mutate: submitCode } = useCodeSubmit();

  const handleSendMessage = async (text: string) => {
    if (isAILoading) return;

    sendMessage({ interviewId: initialInterview.id, text });
  };

  const handleCodeChange = (newCode: string | undefined) => {
    if (!newCode) return;
    setCurrentCode(newCode);
  };

  const handleRunTests = () => {
    if (!currentStep) return;
    submitCode({
      interviewId: initialInterview.id,
      stepId: currentStep.id,
      userCode: currentCode,
    });
  };

  const isInterviewCompleted = useMemo(() => {
    return (
      initialInterview.status === InterviewStatus.COMPLETED ||
      (initialInterview.overall_feedback !== null &&
        initialInterview.total_score !== null)
    );
  }, [initialInterview]);

  const { codeTaskData, currentTestResults } = useMemo(() => {
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

  useEffect(() => {
    if (isCurrentStepCodeTask) {
      const newCode =
        currentStep?.user_code ?? currentStep?.code_task?.initial_code ?? "";
      setCurrentCode(newCode);
    }
  }, [
    currentStep?.id,
    isCurrentStepCodeTask,
    currentStep?.user_code,
    currentStep?.code_task?.initial_code,
  ]);

  useChatAutoScroll<HTMLDivElement>(chatContainerRef, [
    initialInterview.chat_messages,
  ]);

  return (
    <div className="flex h-screen text-white w-full space-x-2 p-2">
      <div className="flex-grow flex bg-white flex-col z-10 rounded-3xl w-full items-center">
        <div className="flex items-center justify-between px-5 py-3 bg-[#3d66ff] transition-colors ease-in-out rounded-t-[22px] w-full">
          <div className="flex items-center gap-3">
            <span className="text-[17px]">
              {initialInterview.job_role_description}
            </span>
            {!isInterviewCompleted && (
              <span className="text-xs text-zinc-200">
                ({initialInterview.current_step_index + 1} из{" "}
                {initialInterview.amount_of_tasks +
                  (initialInterview.steps[0]?.type === "DIALOG" ? 0 : 0)}
                )
              </span>
            )}
          </div>
          {isInterviewCompleted && (
            <Button
              className={cn(
                "flex items-center space-x-1 w-full sm:w-auto rounded-xl",
                "text-white text-[13px] p-2 px-4",
                "hover:bg-white/30 font-medium",
                "bg-white/20 border border-white/30",
                "focus:ring-1 focus:ring-white/50",
                "transition-all duration-200"
              )}
              asChild
            >
              <PDFDownloadLink
                document={<InterviewReport interview={initialInterview} />}
                fileName={`Interview_${initialInterview.job_role_description.slice(
                  0,
                  30
                )}_${new Date().toISOString().split("T")[0]}.pdf`}
              >
                {({ loading }) => (
                  <>
                    <FileText className="w-4 h-4" />
                    <span>{loading ? "Генерация..." : "Скачать отчет"}</span>
                  </>
                )}
              </PDFDownloadLink>
            </Button>
          )}
        </div>
        {isInterviewCompleted ? (
          <FeedbackPanel interview={initialInterview} />
        ) : (
          <>
            <div
              ref={chatContainerRef}
              className={cn(
                "flex-grow overflow-y-auto overflow-x-hidden flex flex-col custom-scrollbar w-full items-center"
              )}
            >
              <div className="flex flex-col max-w-[800px] w-full min-w-0 p-2 px-4">
                {initialInterview.chat_messages.map((msg) => (
                  <ChatMessageBubble key={msg.id} message={msg} />
                ))}
                {isAILoading && (
                  <ChatMessageBubble
                    message={{
                      id: "loading-ai",
                      sender: "AI",
                      text: "ИИ думает...",
                      timestamp: new Date().toISOString(),
                    }}
                  />
                )}
              </div>
            </div>

            <ChatInput
              interviewId={initialInterview.id}
              onSendMessage={handleSendMessage}
              isLoading={isAILoading}
            />
          </>
        )}
      </div>

      {isCurrentStepCodeTask && !isInterviewCompleted && (
        <div className="w-1/2 flex-shrink-0">
          <TaskCodeEditor
            isAILoading={isAILoading}
            initialCode={codeTaskData.initialCode}
            language={codeTaskData.language}
            testCases={codeTaskData.testCases}
            currentTestResults={currentTestResults}
            onCodeChange={handleCodeChange}
            onRunTests={handleRunTests}
          />
        </div>
      )}
    </div>
  );
};
