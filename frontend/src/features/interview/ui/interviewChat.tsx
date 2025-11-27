import { Interview } from "@/entities/interview/types/types";
import React, { useState, useRef, useEffect } from "react";
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
import { useUploadInterviewReport } from "../hooks/useUploadInterviewReport";
import { motion } from "framer-motion";
import { TypingIndicator } from "./typingIndicator";
import { Image } from "@/shared/ui/image/image";
import {
  useCurrentCodeTask,
  useInterviewCompleted,
  useInterviewProgress,
  useInterviewTimer,
  useTypingIndicator,
} from "../hooks/useInterviewChat";
import { useCurrentUser } from "@/entities/user/hooks/useCurrentUser";

interface InterviewChatProps {
  initialInterview: Interview;
}

export const InterviewChat: React.FC<InterviewChatProps> = ({
  initialInterview,
}) => {
  const { data: currentUser } = useCurrentUser();
  const currentStep =
    initialInterview.steps[initialInterview.current_step_index];

  const isCurrentStepCodeTask = currentStep?.type === "CODE_TASK";

  const [currentCode, setCurrentCode] = useState(
    currentStep?.user_code ?? currentStep?.code_task?.initial_code ?? ""
  );
  const chatContainerRef = useRef<HTMLDivElement>(null);

  const { mutate: sendMessage, isPending: isSendingMessage } =
    useInterviewMessage();

  const { mutate: submitCode, isPending: isSubmittingCode } = useCodeSubmit();
  const { uploadInterviewReport, isUploading } = useUploadInterviewReport();

  const isInterviewCompleted = useInterviewCompleted(initialInterview);
  const isAILoading = isSendingMessage || isSubmittingCode || isUploading;
  const { formatted: formattedElapsedTime } = useInterviewTimer(
    initialInterview,
    isInterviewCompleted
  );

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

  const progressData = useInterviewProgress(initialInterview);
  const { codeTaskData, currentTestResults } = useCurrentCodeTask(currentStep);

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
    isAILoading,
  ]);

  const shouldShowTypingIndicator = useTypingIndicator(
    initialInterview,
    isAILoading
  );

  return (
    <div className="flex h-screen text-white w-full space-x-2 p-2">
      <div className="flex-grow flex bg-white flex-col z-10 rounded-3xl w-full items-center">
        <div className="flex flex-col bg-[#3d66ff] transition-colors ease-in-out rounded-t-[22px] w-full">
          <div className="flex items-center justify-between px-5 py-2 gap-4">
            <div className="flex gap-3 flex-1 min-w-0 flex-col sm:flex-row sm:items-center sm:justify-between">
              <div className="flex flex-col min-w-0">
                <span className="text-[17px] font-medium truncate pb-[2px]">
                  {initialInterview.job_role_description}
                </span>
                {currentUser?.username && (
                  <span className="text-[11px] text-zinc-100/90 truncate">
                    Кандидат:{" "}
                    <span className="font-semibold">
                      {currentUser.username}
                    </span>
                  </span>
                )}
              </div>
              <div className="flex items-center gap-3 text-[11px] text-zinc-100/90 mt-1 sm:mt-0">
                <span className="inline-flex items-center gap-1 rounded-full bg-white/10 px-2 py-0.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-300 animate-pulse" />
                  <span className="uppercase tracking-wide">Интервью</span>
                </span>
                <span className="inline-flex items-center gap-1 rounded-full bg-white/10 px-2 py-0.5">
                  <span className="opacity-80">Время:</span>
                  <span className="font-mono font-semibold">
                    {formattedElapsedTime}
                  </span>
                </span>
              </div>
            </div>
            <div className="text-xs text-zinc-100 whitespace-nowrap ml-2">
              Шаг {progressData.current} из {progressData.total}
            </div>
            {isInterviewCompleted && (
              <Button
                className={cn(
                  "flex items-center space-x-1 w-full sm:w-auto rounded-xl",
                  "text-white text-[13px] p-2 px-4",
                  "hover:bg-white/30 font-medium",
                  "bg-white/20 border-white/30",
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
                  {({ blob, url, loading }) => {
                    const href = typeof url === "string" ? url : undefined;
                    const fileName = `Interview_${initialInterview.job_role_description.slice(
                      0,
                      30
                    )}_${new Date().toISOString().split("T")[0]}.pdf`;

                    const handleClick = async () => {
                      if (!blob || isUploading) return;

                      try {
                        await uploadInterviewReport({
                          interviewId: initialInterview.id,
                          file: blob,
                          fileName,
                        });
                      } catch (error) {
                        // eslint-disable-next-line no-console
                        console.error(
                          "Failed to upload interview report before download",
                          error
                        );
                      }
                    };

                    return (
                      <a
                        href={href}
                        download={fileName}
                        onClick={handleClick}
                        className="flex items-center space-x-1"
                      >
                        <FileText className="w-4 h-4" />
                        <span>
                          {loading || isUploading
                            ? "Генерация..."
                            : "Скачать отчет"}
                        </span>
                      </a>
                    );
                  }}
                </PDFDownloadLink>
              </Button>
            )}
          </div>

          {!isInterviewCompleted && (
            <div className="px-5 pb-3">
              <div className="relative w-full h-2 bg-white/20 rounded-full overflow-hidden">
                <motion.div
                  className="absolute top-0 left-0 h-full bg-white rounded-full shadow-lg"
                  initial={{ width: 0 }}
                  animate={{ width: `${progressData.percentage}%` }}
                  transition={{
                    duration: 0.6,
                    ease: [0.4, 0, 0.2, 1],
                  }}
                  style={{
                    background:
                      "linear-gradient(90deg, #ffffff 0%, #e0e7ff 100%)",
                  }}
                >
                  <motion.div
                    className="absolute inset-0 bg-white/30"
                    animate={{
                      x: ["-100%", "100%"],
                    }}
                    transition={{
                      duration: 1.5,
                      repeat: Infinity,
                      ease: "linear",
                    }}
                    style={{
                      background:
                        "linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)",
                      width: "50%",
                    }}
                  />
                </motion.div>
              </div>
            </div>
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
              <div
                className={cn(
                  "flex flex-col max-w-[844px] w-full min-w-0 py-2 px-4",
                  isCurrentStepCodeTask && "xl:px-10"
                )}
              >
                {initialInterview.chat_messages.map((msg) => (
                  <ChatMessageBubble key={msg.id} message={msg} />
                ))}
                {shouldShowTypingIndicator && (
                  <div className="flex gap-4 my-2 justify-start py-4">
                    <div className="flex-shrink-0">
                      <Image
                        src="/images/Avatar.png"
                        alt="AI Assistant"
                        className="h-8 w-8 rounded-full"
                      />
                    </div>
                    <div
                      className={cn(
                        "max-w-[85%] min-w-0 rounded-3xl break-words flex flex-col",
                        "bg-white text-zinc-700 self-start rounded-bl-none"
                      )}
                      style={{
                        overflowWrap: "break-word",
                        wordBreak: "break-word",
                      }}
                    >
                      <div className="mb-2">
                        <span
                          className="inline-flex items-center px-3 py-1 rounded-lg text-xs font-medium border"
                          style={{
                            borderColor: "#8b5cf6",
                            backgroundColor: "#8b5cf620",
                            color: "#8b5cf6",
                          }}
                        >
                          Интервьюер
                        </span>
                      </div>
                      <div
                        className="break-words"
                        style={{ overflowWrap: "break-word" }}
                      >
                        <TypingIndicator />
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <ChatInput
              interviewId={initialInterview.id}
              isCurrentStepCodeTask={isCurrentStepCodeTask}
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
            sourceCode={currentCode}
            interviewId={initialInterview.id}
            stepId={currentStep?.id ?? ""}
            codeTaskId={
              currentStep?.code_task?.id ?? currentStep?.code_task_id ?? ""
            }
          />
        </div>
      )}
    </div>
  );
};
