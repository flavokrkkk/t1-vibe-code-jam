import { z } from "zod";

export const createInterviewSchema = z.object({
  job_role_description: z
    .string()
    .min(10, "Описание должно быть не менее 10 символов")
    .max(500, "Описание должно быть не более 500 символов"),
  amount_of_tasks: z.number().min(1).max(30),
  key_skills: z
    .array(
      z
        .string()
        .min(1, "Навык не может быть пустым")
        .max(50, "Навык не может быть длиннее 50 символов")
    )
    .max(5, "Можно добавить максимум 5 ключевых навыков"),
  preferences: z
    .string()
    .max(1000, "Пожелания не могут быть длиннее 1000 символов"),
});

export type CreateInterviewFormData = z.infer<typeof createInterviewSchema>;
