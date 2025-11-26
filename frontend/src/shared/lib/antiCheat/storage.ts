const STORAGE_KEY = "anti_cheat_warnings";
const MAX_WARNINGS = 3;

export interface StoredWarning {
  interviewId: string;
  warnings: number;
  lastWarningTime: string;
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

