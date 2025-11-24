import { useMutation, useQueryClient } from "@tanstack/react-query";
import { submitCode } from "../api/interviewService";
import { INTERVIEW_DETAIL_QUERY } from "../lib/queryKeys";
import { Interview } from "../types/types";

export const useCodeSubmit = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: submitCode,
    onMutate: async (variables) => {
      const queryKey = [INTERVIEW_DETAIL_QUERY, variables.interviewId];

      await queryClient.cancelQueries({ queryKey });

      const previousInterview = queryClient.getQueryData<Interview>(queryKey);

      return { previousInterview };
    },

    onSuccess: (data, variables) => {
      const queryKey = [INTERVIEW_DETAIL_QUERY, variables.interviewId];
      queryClient.setQueryData(queryKey, data);
    },
  });
};
