import { z } from "zod";

export const createInterviewSchema = z.object({
  job_role_description: z
    .string()
    .min(10, "Описание должно быть не менее 10 символов")
    .max(500, "Описание должно быть не более 500 символов"),
  amount_of_tasks: z.number().min(1).max(30),
});

export type CreateInterviewFormData = z.infer<typeof createInterviewSchema>;
