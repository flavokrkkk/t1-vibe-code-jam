export type ChatMessage = {
  id: string;
  sender: "USER" | "AI";
  text: string;
  timestamp: string;
};

export interface OllamaGenerateResponse {
  model: string;
  created_at: string;
  response: string;
  done: boolean;
  done_reason?: string;
  eval_count?: number;
  prompt_eval_count?: number;
  total_duration?: number;
  remote_host?: string;
  remote_model?: string;
  thinking?: string;
}
