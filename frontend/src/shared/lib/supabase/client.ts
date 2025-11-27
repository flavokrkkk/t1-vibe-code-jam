import { createClient } from "@supabase/supabase-js";

const SUPABASE_URL = "https://dcamwjiwnqhwawhusklx.supabase.co";
const SUPABASE_ANON_KEY =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjYW13aml3bnFod2F3aHVza2x4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDYxMDAwNTUsImV4cCI6MjA2MTY3NjA1NX0.oTSgFBkPa6O8Km7Wc_UWWmEgWeJXmyTBOJJiDWBP7tQ";

if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
  // В проде лучше логировать это в мониторинг, здесь ограничимся предупреждением
  // чтобы не падать при отсутствии переменных окружения
  // eslint-disable-next-line no-console
  console.warn(
    "Supabase env vars are not configured. SUPABASE_URL / SUPABASE_ANON_KEY are missing."
  );
}

export const supabase = createClient(
  SUPABASE_URL ?? "",
  SUPABASE_ANON_KEY ?? ""
);
