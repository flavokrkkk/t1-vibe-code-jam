import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Interview } from "../types/types";
import { sendAudioMessage } from "../api/interviewService";
import { INTERVIEW_DETAIL_QUERY } from "../lib/queryKeys";

interface SendAudioMessageArgs {
  interviewId: string;
  audioBlob: Blob;
}

export const useInterviewAudioMessage = () => {
  const queryClient = useQueryClient();

  return useMutation<Interview, Error, SendAudioMessageArgs>({
    mutationFn: ({ interviewId, audioBlob }) =>
      sendAudioMessage({ interviewId, audioBlob }),
    onMutate: async (variables) => {
      const queryKey = [INTERVIEW_DETAIL_QUERY, variables.interviewId];

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
              text: "[Обработка аудио...]",
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
};
