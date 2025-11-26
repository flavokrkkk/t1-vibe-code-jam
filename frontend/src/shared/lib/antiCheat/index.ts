export { AntiCheatProvider, useAntiCheat } from "./antiCheatProvider";
export type { AntiCheatViolation, AntiCheatWarning } from "./types";
export {
  getWarnings,
  addWarning,
  clearWarnings,
  hasReachedMaxWarnings,
  MAX_WARNINGS_COUNT,
} from "./storage";
export { hasAcceptedRules, setRulesAccepted } from "./rulesStorage";
