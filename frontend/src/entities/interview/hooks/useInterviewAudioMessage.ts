import { useMutation, useQueryClient } from "@tanstack/react-query";
import { sendAudioMessage } from "../api/interviewService";
import { useInterviewMessage } from "./useInterviewMessage";
import { INTERVIEW_DETAIL_QUERY } from "../lib/queryKeys";
import type { Interview } from "../types/types";

interface SendAudioMessageArgs {
  interviewId: string;
  audioBlob: Blob;
}

export const useInterviewAudioMessage = () => {
  const queryClient = useQueryClient();
  const { mutate: sendMessage } = useInterviewMessage();

  return useMutation<{ text: string }, Error, SendAudioMessageArgs>({
    mutationFn: ({ interviewId, audioBlob }) =>
      sendAudioMessage({ interviewId, audioBlob }),
    onMutate: async (variables) => {
      const queryKey = [INTERVIEW_DETAIL_QUERY, variables.interviewId];

      await queryClient.cancelQueries({ queryKey });

      const previousInterview = queryClient.getQueryData<Interview>(queryKey);

      queryClient.setQueryData<Interview>(queryKey, (old) => {
        if (!old) return old;

        return {
          ...old,
          chat_messages: [
            ...old.chat_messages,
            {
              id: crypto.randomUUID(),
              sender: "USER",
              text: "speach_id",
              created_at: new Date().toISOString(),
              isTyping: true,
            },
          ],
        };
      });

      return { previousInterview };
    },
    onSuccess: (data, variables) => {
      const queryKey = [INTERVIEW_DETAIL_QUERY, variables.interviewId];

      queryClient.setQueryData<Interview>(queryKey, (old) => {
        if (!old) return old;

        const updatedMessages = [...old.chat_messages];
        const lastIndex = updatedMessages.length - 1;

        if (lastIndex >= 0) {
          const last = updatedMessages[lastIndex];

          if (last.sender === "USER" && last.isTyping) {
            updatedMessages[lastIndex] = {
              ...last,
              text: data.text,
              isTyping: true,
            };
          }
        }

        return {
          ...old,
          chat_messages: updatedMessages,
        };
      });

      sendMessage({
        interviewId: variables.interviewId,
        text: data.text,
        skipOptimistic: true,
      });
    },
    retry: false,
  });
};
