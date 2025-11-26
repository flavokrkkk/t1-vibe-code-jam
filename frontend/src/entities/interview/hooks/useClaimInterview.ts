import { useMutation, useQueryClient } from "@tanstack/react-query";
import { claimInterview } from "../api/interviewService";
import {
  INTERVIEW_DETAIL_QUERY,
  INTERVIEWS_LIST_QUERY,
  CLAIM_INTERVIEW_MUTATION,
} from "../lib/queryKeys";
import { Interview } from "../types/types";

interface UseClaimInterviewOptions {
  onSuccess?: (interview: Interview) => void;
  onError?: (error: Error) => void;
}

export const useClaimInterview = (options?: UseClaimInterviewOptions) => {
  const queryClient = useQueryClient();

  return useMutation<Interview, Error, { publicToken: string }>({
    mutationKey: [CLAIM_INTERVIEW_MUTATION],
    mutationFn: ({ publicToken }) => claimInterview({ publicToken }),
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: [INTERVIEW_DETAIL_QUERY] });
      await queryClient.cancelQueries({ queryKey: [INTERVIEWS_LIST_QUERY] });

      const previousQueries = queryClient.getQueriesData({
        queryKey: [INTERVIEW_DETAIL_QUERY],
      });

      return { previousQueries };
    },
    onSuccess: (claimedInterview) => {
      queryClient.setQueryData(
        [INTERVIEW_DETAIL_QUERY, claimedInterview.id],
        claimedInterview
      );

      queryClient.setQueryData<Interview[]>(
        [INTERVIEWS_LIST_QUERY],
        (oldData) => {
          if (!oldData) {
            return [claimedInterview];
          }

          const exists = oldData.some(
            (item) => item.id === claimedInterview.id
          );
          if (exists) {
            return oldData.map((item) =>
              item.id === claimedInterview.id ? claimedInterview : item
            );
          }

          return [claimedInterview, ...oldData];
        }
      );

      options?.onSuccess?.(claimedInterview);
    },
    onError: (error) => {
      options?.onError?.(error);
    },
    retry: false,
  });
};
