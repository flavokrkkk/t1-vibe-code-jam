import { useMutation } from "@tanstack/react-query";
import { runCodeTests } from "../api/interviewService";

interface RunCodeTestsParams {
  sourceCode: string;
  language: string;
  codeTaskId: string;
}

interface TestResult {
  all_passed: boolean;
  results: Array<{
    passed: boolean;
    status: string | null;
    stdout: string;
    stderr: string;
    expected: string;
  }>;
}

export const useRunCodeTests = () => {
  return useMutation<TestResult, Error, RunCodeTestsParams>({
    mutationFn: runCodeTests,
  });
};
