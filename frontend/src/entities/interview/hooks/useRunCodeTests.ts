import { useMutation } from "@tanstack/react-query";
import { runCodeTests } from "../api/interviewService";

interface RunCodeTestsParams {
  sourceCode: string;
  language: string;
  testCases: Array<Record<string, any>>;
}

export const useRunCodeTests = () => {
  return useMutation<string, Error, RunCodeTestsParams>({
    mutationFn: runCodeTests,
  });
};

