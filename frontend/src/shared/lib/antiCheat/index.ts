export { AntiCheatProvider, useAntiCheat } from "./antiCheatProvider";
export type { AntiCheatViolation, AntiCheatWarning } from "./types";
export {
  getWarnings,
  addWarning,
  clearWarnings,
  hasReachedMaxWarnings,
  MAX_WARNINGS_COUNT,
  addViolation,
  getViolations,
  clearViolations,
} from "./storage";
export { hasAcceptedRules, setRulesAccepted } from "./rulesStorage";
