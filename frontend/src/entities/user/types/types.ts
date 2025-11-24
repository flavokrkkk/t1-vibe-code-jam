import { Interview } from "@/entities/interview/types/types";

export interface User {
  id: string;
  email: string;
  username: string;
  created_at?: string;
  updated_at?: string;
  interviews?: Array<Interview>;
}
