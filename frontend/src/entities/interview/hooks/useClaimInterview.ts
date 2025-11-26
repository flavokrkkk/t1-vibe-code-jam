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
    onMutate: async (variables) => {
      // Отменяем все запросы для интервью, чтобы избежать конфликтов
      await queryClient.cancelQueries({ queryKey: [INTERVIEW_DETAIL_QUERY] });
      await queryClient.cancelQueries({ queryKey: [INTERVIEWS_LIST_QUERY] });

      // Сохраняем предыдущие данные для отката
      const previousQueries = queryClient.getQueriesData({
        queryKey: [INTERVIEW_DETAIL_QUERY],
      });

      return { previousQueries };
    },
    onSuccess: (claimedInterview, variables) => {
      // Обновляем кэш детального интервью
      queryClient.setQueryData(
        [INTERVIEW_DETAIL_QUERY, claimedInterview.id],
        claimedInterview
      );

      // Оптимистично добавляем интервью в список (если его там еще нет)
      queryClient.setQueryData<Interview[]>(
        [INTERVIEWS_LIST_QUERY],
        (oldData) => {
          if (!oldData) {
            return [claimedInterview];
          }

          // Проверяем, нет ли уже этого интервью в списке
          const exists = oldData.some((item) => item.id === claimedInterview.id);
          if (exists) {
            // Обновляем существующее интервью
            return oldData.map((item) =>
              item.id === claimedInterview.id ? claimedInterview : item
            );
          }

          // Добавляем новое интервью в начало списка
          return [claimedInterview, ...oldData];
        }
      );

      options?.onSuccess?.(claimedInterview);
    },
    onError: (error, variables, context) => {
      // В случае ошибки можно откатить изменения, если нужно
      // Но обычно лучше просто показать ошибку пользователю
      options?.onError?.(error);
    },
    retry: false,
  });
};

