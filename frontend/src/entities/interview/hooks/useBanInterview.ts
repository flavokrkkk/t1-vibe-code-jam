import { useMutation, useQueryClient } from "@tanstack/react-query";
import { banInterview } from "../api/interviewService";
import { INTERVIEW_DETAIL_QUERY, BAN_INTERVIEW_MUTATION } from "../lib/queryKeys";
import { Interview } from "../types/types";

interface BanInterviewParams {
  interviewId: string;
  reasons: string[];
}

interface UseBanInterviewOptions {
  onSuccess?: (interview: Interview) => void;
  onError?: (error: Error) => void;
}

export const useBanInterview = (options?: UseBanInterviewOptions) => {
  const queryClient = useQueryClient();

  return useMutation<Interview, Error, BanInterviewParams>({
    mutationKey: [BAN_INTERVIEW_MUTATION],
    mutationFn: ({ interviewId, reasons }) =>
      banInterview({ interviewId, reasons }),
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

