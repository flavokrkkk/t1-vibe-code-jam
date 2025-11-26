import { DateTime } from "luxon";
import ReactMarkdown from "react-markdown";
import React from "react";
import { ChatMessage } from "@/entities/message/types/types";
import { cn } from "@/shared/lib/mergeClass";
import { motion } from "framer-motion";

interface ChatMessageBubbleProps {
  message: ChatMessage;
}

export const ChatMessageBubble: React.FC<ChatMessageBubbleProps> = ({
  message,
}) => {
  const isUser = message.sender === "USER";
  const isSpeechPlaceholder = isUser && message.text === "speach_id";
  const bubbleClasses = isUser
    ? "bg-blue-500 transition-colors ease-in-out text-white self-end rounded-br-none"
    : "bg-white text-zinc-700 self-start rounded-bl-none border border-blue-400/20";

  const formattedTime = React.useMemo(() => {
    const dateTime = DateTime.fromISO(message.created_at);
    return dateTime.isValid ? dateTime.toFormat("HH:mm") : "";
  }, [message.created_at]);

  return (
    <div
      className={cn(
        "max-w-[70%] min-w-0 p-4 rounded-3xl my-2 break-words",
        bubbleClasses
      )}
      style={{ overflowWrap: "break-word", wordBreak: "break-word" }}
    >
      <div className="break-words" style={{ overflowWrap: "break-word" }}>
        {isSpeechPlaceholder ? (
          <div
            className="flex items-end gap-1 h-6"
            aria-label="Голосовое сообщение"
          >
            {[0, 1, 2, 3].map((i) => (
              <motion.span
                key={i}
                className="w-2.5 rounded-full bg-white/80"
                animate={{
                  scaleY: [0.4, 1, 0.5],
                  opacity: [0.6, 1, 0.6],
                }}
                transition={{
                  duration: 1.2,
                  repeat: Infinity,
                  delay: i * 0.15,
                  ease: "easeInOut",
                }}
                style={{
                  transformOrigin: "center bottom",
                  height: `${8 + i * 4}px`,
                }}
              />
            ))}
          </div>
        ) : (
          <ReactMarkdown
            components={{
              p: ({ children }) => (
                <p
                  className="break-words"
                  style={{
                    overflowWrap: "break-word",
                    wordBreak: "break-word",
                  }}
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
        )}
      </div>
      <div className="text-xs text-right opacity-75 mt-1">{formattedTime}</div>
    </div>
  );
};
