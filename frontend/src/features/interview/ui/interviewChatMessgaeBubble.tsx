import { DateTime } from "luxon";
import ReactMarkdown from "react-markdown";
import React from "react";
import { ChatMessage } from "@/entities/message/types/types";
import { cn } from "@/shared/lib/mergeClass";

interface ChatMessageBubbleProps {
  message: ChatMessage;
}

export const ChatMessageBubble: React.FC<ChatMessageBubbleProps> = ({
  message,
}) => {
  const isUser = message.sender === "USER";
  const bubbleClasses = isUser
    ? "bg-blue-500 transition-colors ease-in-out text-white self-end rounded-br-none"
    : "bg-white text-zinc-700 self-start rounded-bl-none border border-blue-400/20";

  const formattedTime = React.useMemo(() => {
    const dateTime = DateTime.fromISO(message.timestamp);
    return dateTime.isValid ? dateTime.toFormat("HH:mm") : "";
  }, [message.timestamp]);

  return (
    <div
      className={cn(
        "max-w-[70%] min-w-0 p-4 rounded-xl my-2 break-words",
        bubbleClasses
      )}
      style={{ overflowWrap: "break-word", wordBreak: "break-word" }}
    >
      <div className="break-words" style={{ overflowWrap: "break-word" }}>
        <ReactMarkdown
          components={{
            p: ({ children }) => (
              <p
                className="break-words"
                style={{ overflowWrap: "break-word", wordBreak: "break-word" }}
              >
                {children}
              </p>
            ),
            code: ({ children }) => (
              <code
                className="break-words whitespace-pre-wrap overflow-x-auto block"
                style={{ overflowWrap: "break-word" }}
              >
                {children}
              </code>
            ),
            pre: ({ children }) => (
              <pre
                className="break-words whitespace-pre-wrap overflow-x-auto max-w-full"
                style={{ overflowWrap: "break-word" }}
              >
                {children}
              </pre>
            ),
          }}
        >
          {message.text}
        </ReactMarkdown>
      </div>
      <div className="text-xs text-right opacity-75 mt-1">
        {formattedTime}
      </div>
    </div>
  );
};
