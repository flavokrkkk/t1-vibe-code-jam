import { cn } from "@/shared/lib/mergeClass";
import { Mic, ChevronUp, Check, X, Loader2 } from "lucide-react";
import React, {
  useCallback,
  useMemo,
  useState,
  useRef,
  useEffect,
} from "react";
import { useComputerVoiceRecorder } from "../hooks/useComputerVoiceRecorder";
import { useInterviewAudioMessage } from "@/entities/interview/hooks/useInterviewAudioMessage";

interface ChatInputProps {
  isLoading: boolean;
  interviewId: string;
  onSendMessage: (message: string) => void;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  isLoading,
  interviewId,
  onSendMessage,
}) => {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const shouldSendAudioRef = useRef(true);

  const { mutate: sendAudioMessage } = useInterviewAudioMessage();
  const {
    isRecording,
    elapsedSec,
    error: recordingError,
    startRecording,
    stopRecording,
  } = useComputerVoiceRecorder({
    sendCallback: (blob) => {
      if (shouldSendAudioRef.current) {
        sendAudioMessage({ interviewId, audioBlob: blob });
      }
      shouldSendAudioRef.current = true;
    },
  });

  const formatTime = useCallback((seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${String(secs).padStart(2, "0")}`;
  }, []);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      const scrollHeight = textarea.scrollHeight;
      const maxHeight = 200;
      textarea.style.height = `${Math.min(scrollHeight, maxHeight)}px`;
    }
  }, [message]);

  const isMultiLine = useMemo(() => {
    const textarea = textareaRef.current;
    if (!textarea) return false;
    return textarea.scrollHeight > 50;
  }, [message]);

  const handleMessageChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      setMessage(e.target.value);
    },
    []
  );

  const handleSend = useCallback(() => {
    if (message.trim() && !isLoading) {
      onSendMessage(message);
      setMessage("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  }, [message, isLoading, onSendMessage]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend]
  );

  const handleMicClick = useCallback(async () => {
    if (isRecording) {
      stopRecording();
    } else {
      try {
        shouldSendAudioRef.current = true;
        await startRecording();
      } catch (error) {
        console.error("Failed to start recording:", error);
      }
    }
  }, [isRecording, startRecording, stopRecording]);

  const handleCancelRecording = useCallback(() => {
    shouldSendAudioRef.current = false;
    stopRecording();
  }, [stopRecording]);

  const handleSendVoice = useCallback(() => {
    shouldSendAudioRef.current = true;
    stopRecording();
  }, [stopRecording]);

  const isSendButtonDisabled = useMemo(
    () => isLoading || !message.trim(),
    [isLoading, message]
  );

  const needsScrollbar = useMemo(() => {
    const textarea = textareaRef.current;
    if (!textarea) return false;
    return textarea.scrollHeight > 200;
  }, [message]);

  return (
    <div className="md:px-4 lg:px-10 w-full max-w-[844px]">
      <div className="mx-auto px-4 md:px-0 pb-4 rounded-4xl relative">
        <div className="relative overflow-visible">
          {isRecording ? (
            <div className="w-full min-h-[50px] rounded-[24px] shadow-sm mb-[13px] px-12 py-3 pr-20 bg-white border border-gray-200 flex items-center relative">
              <div className="flex-1 flex items-center px-2">
                <div className="flex-1 border-b-2 border-dotted border-gray-400"></div>
                <span className="ml-3 text-sm text-gray-500">
                  {formatTime(elapsedSec)}
                </span>
              </div>
              <button
                type="button"
                className={cn(
                  "absolute right-12 h-6 w-6 flex items-center cursor-pointer justify-center text-gray-700 hover:text-gray-900 transition-all duration-200",
                  "disabled:opacity-50 disabled:cursor-not-allowed"
                )}
                disabled={isLoading}
                onClick={handleCancelRecording}
              >
                <X className="h-5 w-5" />
              </button>
              <button
                type="button"
                disabled={isLoading}
                className={cn(
                  "absolute right-2 h-8 w-8 rounded-full cursor-pointer",
                  "bg-black hover:bg-gray-800",
                  "text-white transition-all shadow-sm duration-200",
                  "disabled:opacity-50 disabled:cursor-not-allowed",
                  "active:scale-95 flex items-center justify-center"
                )}
                onClick={handleSendVoice}
              >
                <Check className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <div
              className={cn(
                "w-full min-h-[50px] rounded-[24px] shadow-sm",
                "bg-white border border-gray-200",
                "focus-within:border-gray-300",
                "transition-all",
                "relative",
                "flex flex-col"
              )}
            >
              <div className="relative flex-1 flex items-stretch">
                <textarea
                  ref={textareaRef}
                  value={message}
                  placeholder="Напишите сообщение... (Shift+Enter для новой строки)"
                  disabled={isLoading}
                  rows={1}
                  className={cn(
                    "w-full min-h-[50px] max-h-[200px] resize-none scrollbar-hide",
                    "px-4 py-3.5 md:py-3 pr-20",
                    "bg-transparent",
                    "text-sm md:text-base text-gray-900 placeholder:text-gray-400",
                    "focus:outline-none",
                    "transition-all",
                    "disabled:opacity-50 disabled:cursor-not-allowed",
                    needsScrollbar && "overflow-y-auto custom-scrollbar",
                    !needsScrollbar && "overflow-hidden"
                  )}
                  style={{
                    height: "auto",
                  }}
                  onChange={handleMessageChange}
                  onKeyDown={handleKeyDown}
                />
                <button
                  type="button"
                  className={cn(
                    "absolute right-12 h-6 w-6 flex items-center cursor-pointer justify-center text-gray-700 hover:text-gray-900 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed",
                    isMultiLine ? "bottom-3" : "top-[50%] -translate-y-1/2",
                    isRecording && "text-red-500"
                  )}
                  disabled={isLoading}
                  onClick={handleMicClick}
                >
                  <Mic className="h-5 w-5" />
                </button>
                <button
                  type="button"
                  onClick={handleSend}
                  disabled={isSendButtonDisabled}
                  className={cn(
                    "absolute right-2 h-8 w-8 rounded-full cursor-pointer",
                    "bg-black hover:bg-gray-800",
                    "text-white transition-all shadow-sm duration-200",
                    "disabled:opacity-50 disabled:cursor-not-allowed",
                    "active:scale-95 p-0",
                    "flex items-center justify-center",
                    isMultiLine ? "bottom-2" : "top-[50%] -translate-y-1/2"
                  )}
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <ChevronUp className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>
          )}

          {recordingError && (
            <p className="text-xs text-red-500 mt-2 px-4">{recordingError}</p>
          )}
        </div>
      </div>
    </div>
  );
};
