import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { INTERVIEW_ALL_QUERY, INTERVIEW_DETAIL_QUERY } from "../lib/queryKeys";
import { getAllInterviews, getInterviewById } from "../api/interviewService";

export const useInterview = () => {
  const { interviewId } = useParams();

  return useQuery({
    queryKey: [INTERVIEW_DETAIL_QUERY, interviewId],
    queryFn: () => getInterviewById({ interviewId: interviewId ?? "" }),
    enabled: !!interviewId,
    refetchInterval: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    staleTime: 1000 * 60 * 10,
  });
};

export const useGetAllInterview = () => {
  return useQuery({
    queryKey: [INTERVIEW_ALL_QUERY],
    queryFn: getAllInterviews,
  });
};
