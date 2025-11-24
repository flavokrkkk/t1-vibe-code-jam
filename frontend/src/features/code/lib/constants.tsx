import { CodeTestResultStatus } from "@/entities/interview/types/types";
import { cn } from "@/shared/lib/mergeClass";

export const TEST_RESULT_ICONS = {
  passed: "✓",
  failed: "✗",
  error: "⚠",
  pending: "…",
};

export const TEST_RESULT_MESSAGES = {
  passed: "✅ Test Passed!",
  failed: "❌ Test Failed!",
  error: "⚠️ Execution Error!",
  pending: "Running...",
  default: "Run tests to see results.",
};

export const TEST_RESULT_COLORS = {
  passed: "text-green-400",
  failed: "text-red-400",
  error: "text-yellow-400",
  pending: "text-gray-400",
  default: "text-zinc-700",
};

export const getResultIcon = (result: CodeTestResultStatus) => (
  <span
    className={cn(
      "mr-1",
      TEST_RESULT_COLORS[result] || TEST_RESULT_COLORS.default
    )}
  >
    {TEST_RESULT_ICONS[result]}
  </span>
);

export const getResultDisplay = (result: CodeTestResultStatus | undefined) => {
  const message = result
    ? TEST_RESULT_MESSAGES[result]
    : TEST_RESULT_MESSAGES.default;
  const colorClass = result
    ? TEST_RESULT_COLORS[result]
    : TEST_RESULT_COLORS.default;

  return <p className={cn(colorClass, "flex items-center")}>{message}</p>;
};
