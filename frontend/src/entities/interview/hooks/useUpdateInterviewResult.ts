import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateInterviewResult } from "../api/interviewService";
import {
  INTERVIEW_DETAIL_QUERY,
  UPDATE_INTERVIEW_RESULT_MUTATION,
} from "../lib/queryKeys";
import { Interview } from "../types/types";

interface UpdateInterviewResultParams {
  interviewId: string;
  resultUrl: string;
}

interface UseUpdateInterviewResultOptions {
  onSuccess?: (interview: Interview) => void;
  onError?: (error: Error) => void;
}

export const useUpdateInterviewResult = (
  options?: UseUpdateInterviewResultOptions
) => {
  const queryClient = useQueryClient();

  return useMutation<Interview, Error, UpdateInterviewResultParams>({
    mutationKey: [UPDATE_INTERVIEW_RESULT_MUTATION],
    mutationFn: ({ interviewId, resultUrl }) =>
      updateInterviewResult({ interviewId, resultUrl }),
    onMutate: async (variables) => {
      const queryKey = [INTERVIEW_DETAIL_QUERY, variables.interviewId];

      await queryClient.cancelQueries({ queryKey });

      const previousInterview = queryClient.getQueryData<Interview>(queryKey);

      return { previousInterview };
    },
    onSuccess: (data, variables) => {
      const queryKey = [INTERVIEW_DETAIL_QUERY, variables.interviewId];
      queryClient.setQueryData(queryKey, data);
      options?.onSuccess?.(data);
    },
    onError: (error) => {
      options?.onError?.(error);
    },
  });
};

