import {
  CodeTestResult,
  CodeTestResultStatus,
  TestCase,
} from "@/entities/interview/types/types";
import { useState, useMemo, useCallback } from "react";

interface UseCodeTaskTestsProps {
  testCases: TestCase[];
  currentTestResults: CodeTestResult[];
}

export const useCodeTaskTests = ({
  testCases,
  currentTestResults,
}: UseCodeTaskTestsProps) => {
  const [activeTestId, setActiveTestIdState] = useState<string>(() => {
    return testCases.length > 0 ? testCases[0].id : "";
  });

  const setActiveTestId = useCallback((id: string) => {
    setActiveTestIdState(id);
  }, []);

  const activeCase = useMemo(
    () => testCases.find((tc) => tc.id === activeTestId),
    [testCases, activeTestId]
  );

  const mappedTestResults = useMemo(() => {
    const resultsMap: { [key: string]: CodeTestResultStatus } = {};
    currentTestResults.forEach((res) => {
      resultsMap[res.test_id] = res.status.toLowerCase() as CodeTestResultStatus;
    });
    return resultsMap;
  }, [currentTestResults]);

  return {
    activeTestId,
    setActiveTestId,
    activeCase,
    mappedTestResults,
  };
};
