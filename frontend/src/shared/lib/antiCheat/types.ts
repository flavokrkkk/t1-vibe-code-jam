export type AntiCheatViolationType =
  | "TAB_SWITCH"
  | "WINDOW_BLUR"
  | "DEVTOOLS_OPEN"
  | "COPY_PASTE"
  | "CONTEXT_MENU"
  | "SCREENSHOT";

export interface AntiCheatViolation {
  type: AntiCheatViolationType;
  timestamp: string;
  details?: string;
}

export interface AntiCheatWarning {
  violation: AntiCheatViolation;
  warningNumber: number;
}

