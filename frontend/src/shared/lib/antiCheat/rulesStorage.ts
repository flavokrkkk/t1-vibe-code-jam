const RULES_ACCEPTED_KEY = "anti_cheat_rules_accepted";

export const hasAcceptedRules = (interviewId: string): boolean => {
  try {
    const stored = localStorage.getItem(RULES_ACCEPTED_KEY);
    if (!stored) return false;

    const data: Record<string, boolean> = JSON.parse(stored);
    return data[interviewId] ?? false;
  } catch {
    return false;
  }
};

export const setRulesAccepted = (interviewId: string): void => {
  try {
    const stored = localStorage.getItem(RULES_ACCEPTED_KEY);
    const data: Record<string, boolean> = stored ? JSON.parse(stored) : {};

    data[interviewId] = true;
    localStorage.setItem(RULES_ACCEPTED_KEY, JSON.stringify(data));
  } catch {
    // Ignore errors
  }
};

