import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createInterview } from "../api/interviewService";
import {
  INTERVIEWS_LIST_QUERY,
  CREATE_INTERVIEW_MUTATION,
  INTERVIEW_DETAIL_QUERY,
} from "../lib/queryKeys";
import { Interview } from "../types/types";
import { CreateInterviewFormData } from "../lib/schemes/createInterviewSchema";

interface UseCreateInterviewOptions {
  onSuccess?: (interview: Interview) => void;
}

export const useCreateInterview = (options?: UseCreateInterviewOptions) => {
  const queryClient = useQueryClient();

  return useMutation<Interview, Error, CreateInterviewFormData>({
    mutationKey: [CREATE_INTERVIEW_MUTATION],
    mutationFn: createInterview,
    onSuccess: (newInterview) => {
      queryClient.setQueryData<Interview[]>(
        [INTERVIEWS_LIST_QUERY],
        (oldData) => {
          if (oldData) {
            return [newInterview, ...oldData];
          }
          return [newInterview];
        }
      );

      queryClient.setQueryData(
        [INTERVIEW_DETAIL_QUERY, newInterview.id],
        newInterview
      );

      options?.onSuccess?.(newInterview);
    },
  });
};
