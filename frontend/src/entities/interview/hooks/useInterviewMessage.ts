import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Interview } from "../types/types";
import { sendChatMessage } from "../api/interviewService";
import { INTERVIEW_DETAIL_QUERY } from "../lib/queryKeys";

interface SendChatMessageArgs {
  interviewId: string;
  text: string;
  skipOptimistic?: boolean;
}

export const useInterviewMessage = () => {
  const queryClient = useQueryClient();

  const mutation = useMutation<Interview, Error, SendChatMessageArgs>({
    mutationFn: ({ interviewId, text }) =>
      sendChatMessage({ interviewId, text }),
    onMutate: async (variables) => {
      const queryKey = [INTERVIEW_DETAIL_QUERY, variables.interviewId];

      await queryClient.cancelQueries({ queryKey });

      const previousInterview = queryClient.getQueryData<Interview>(queryKey);

      if (variables.skipOptimistic) {
        return { previousInterview };
      }

      queryClient.setQueryData<Interview>(queryKey, (old) => {
        if (!old) return old;

        return {
          ...old,
          chat_messages: [
            ...old.chat_messages,
            {
              id: crypto.randomUUID(),
              sender: "USER",
              text: variables.text,
              created_at: new Date().toISOString(),
            },
          ],
        };
      });

      return { previousInterview };
    },

    onSuccess: (data, variables) => {
      const queryKey = [INTERVIEW_DETAIL_QUERY, variables.interviewId];
      queryClient.setQueryData(queryKey, data);
    },
    retry: false,
  });

  return {
    ...mutation,
    isPending: mutation.isPending,
  };
};
