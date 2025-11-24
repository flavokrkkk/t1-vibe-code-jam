import { getInterviewById } from "../api/interviewService";
import { INTERVIEW_DETAIL_QUERY } from "../lib/queryKeys";
import { Interview } from "../types/types";
import { LoaderFunctionArgs, redirect } from "react-router-dom";
import { ERouteNames } from "@/shared/lib/routeVariables";
import { queryClient } from "@/shared/api/queryClient";

export const interviewDetailAction = async ({
  params,
}: LoaderFunctionArgs): Promise<Interview | Response | null> => {
  const interviewId = params.interviewId;

  if (!interviewId) {
    return redirect(`/${ERouteNames.DASHBOARD_ROUTE}`);
  }

  const loadInterview = async (): Promise<Interview | undefined> => {
    const cachedInterview = queryClient.getQueryData<Interview>([
      INTERVIEW_DETAIL_QUERY,
      interviewId,
    ]);

    if (cachedInterview) {
      return cachedInterview;
    }

    return await getInterviewById({ interviewId });
  };

  const selectInterview = await loadInterview();

  if (!selectInterview) {
    return redirect(`/${ERouteNames.DASHBOARD_ROUTE}`);
  }

  queryClient.setQueryData<Interview>(
    [INTERVIEW_DETAIL_QUERY, interviewId],
    selectInterview
  );

  return selectInterview;
};
