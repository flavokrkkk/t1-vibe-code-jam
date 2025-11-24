import { Interview, InterviewStatus } from "@/entities/interview/types/types";
import React, { useState, useRef, useMemo } from "react";
import { ChatMessageBubble } from "./interviewChatMessgaeBubble";
import { ChatInput } from "./interviewChatInput";
import { TaskCodeEditor } from "@/features/code/ui/taskCodeEditor";
import { useChatAutoScroll } from "@/shared/hooks/useChatAutoScroll";
import { cn } from "@/shared/lib/mergeClass";
import { useInterviewMessage } from "@/entities/interview/hooks/useInterviewMessage";
import { useCodeSubmit } from "@/entities/interview/hooks/useCodeSubmit";
import FeedbackPanel from "./interviewFeedbackPanel";

interface InterviewChatProps {
  initialInterview: Interview;
}

export const InterviewChat: React.FC<InterviewChatProps> = ({
  initialInterview,
}) => {
  const currentStep =
    initialInterview.steps[initialInterview.current_step_index];

  const [isAILoading] = useState(false);
  const [currentCode, setCurrentCode] = useState(
    currentStep.code_task?.initial_code ?? ""
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

  const { currentCodeTask, currentTestResults } = useMemo(() => {
    return {
      currentCodeTask: currentStep.code_task,
      currentTestResults: currentStep.code_test_results ?? [],
    };
  }, [currentStep]);

  useChatAutoScroll<HTMLDivElement>(chatContainerRef, [
    initialInterview.chat_messages,
  ]);

  return (
    <div className="flex h-screen text-white w-full space-x-2 p-2">
      <div className="flex-grow flex bg-white flex-col rounded-3xl w-full items-center">
        <div className="flex items-center justify-between px-4 py-2 bg-[#3d66ff] transition-colors ease-in-out cursor-pointer rounded-t-[22px] w-full">
          <div className="flex items-center gap-3">
            <span className="text-[17px]">Frontend разработчик</span>
            <span className="text-xs text-zinc-200">
              ({initialInterview.current_step_index + 1} из{" "}
              {initialInterview.amount_of_tasks +
                (initialInterview.steps[0].type === "DIALOG" ? 0 : 0)}
              )
            </span>
          </div>
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

      {currentCodeTask && !isInterviewCompleted && (
        <div className="w-1/2 flex-shrink-0">
          <TaskCodeEditor
            isAILoading={isAILoading}
            initialCode={currentCodeTask.initial_code || ""}
            language={currentCodeTask.language}
            testCases={currentCodeTask.test_cases}
            currentTestResults={currentTestResults || []}
            onCodeChange={handleCodeChange}
            onRunTests={handleRunTests}
          />
        </div>
      )}
    </div>
  );
};
