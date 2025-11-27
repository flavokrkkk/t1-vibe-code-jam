const STORAGE_KEY = "anti_cheat_warnings";
const VIOLATIONS_STORAGE_KEY = "anti_cheat_violations";
const MAX_WARNINGS = 3;

export interface StoredWarning {
  interviewId: string;
  warnings: number;
  lastWarningTime: string;
}

export interface StoredViolations {
  interviewId: string;
  violations: Array<{
    type: string;
    timestamp: string;
    details?: string;
  }>;
}

export const getWarnings = (interviewId: string): number => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return 0;

    const data: Record<string, StoredWarning> = JSON.parse(stored);
    return data[interviewId]?.warnings ?? 0;
  } catch {
    return 0;
  }
};

export const addWarning = (interviewId: string): number => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    const data: Record<string, StoredWarning> = stored
      ? JSON.parse(stored)
      : {};

    const current = data[interviewId]?.warnings ?? 0;
    const newCount = current + 1;

    data[interviewId] = {
      interviewId,
      warnings: newCount,
      lastWarningTime: new Date().toISOString(),
    };

    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    return newCount;
  } catch {
    return 0;
  }
};

export const clearWarnings = (interviewId: string): void => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return;

    const data: Record<string, StoredWarning> = JSON.parse(stored);
    delete data[interviewId];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch {
    // Ignore errors
  }
};

export const hasReachedMaxWarnings = (interviewId: string): boolean => {
  return getWarnings(interviewId) >= MAX_WARNINGS;
};

export const MAX_WARNINGS_COUNT = MAX_WARNINGS;

export const addViolation = (
  interviewId: string,
  violation: { type: string; timestamp: string; details?: string }
): void => {
  try {
    const stored = localStorage.getItem(VIOLATIONS_STORAGE_KEY);
    const data: Record<string, StoredViolations> = stored
      ? JSON.parse(stored)
      : {};

    if (!data[interviewId]) {
      data[interviewId] = {
        interviewId,
        violations: [],
      };
    }

    data[interviewId].violations.push(violation);
    localStorage.setItem(VIOLATIONS_STORAGE_KEY, JSON.stringify(data));
  } catch {
    // Ignore errors
  }
};

export const getViolations = (
  interviewId: string
): Array<{ type: string; timestamp: string; details?: string }> => {
  try {
    const stored = localStorage.getItem(VIOLATIONS_STORAGE_KEY);
    if (!stored) return [];

    const data: Record<string, StoredViolations> = JSON.parse(stored);
    return data[interviewId]?.violations ?? [];
  } catch {
    return [];
  }
};

export const clearViolations = (interviewId: string): void => {
  try {
    const stored = localStorage.getItem(VIOLATIONS_STORAGE_KEY);
    if (!stored) return;

    const data: Record<string, StoredViolations> = JSON.parse(stored);
    delete data[interviewId];
    localStorage.setItem(VIOLATIONS_STORAGE_KEY, JSON.stringify(data));
  } catch {
    // Ignore errors
  }
};

