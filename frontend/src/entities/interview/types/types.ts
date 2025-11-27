import { ChatMessage } from "@/entities/message/types/types";

export enum InterviewStatus {
  PENDING = "PENDING",
  IN_PROGRESS = "IN_PROGRESS",
  COMPLETED = "COMPLETED",
  CANCELLED = "CANCELLED",
}

export type CodeTask = {
  id: string; // ID задачи
  description: string; // Описание задачи (что нужно сделать)
  initial_code: string; // Начальный код для редактора (может быть пустым или содержать заготовку)
  language: string; // Язык программирования задачи (например, "typescript", "python")
  test_cases: TestCase[]; // Тестовые случаи
};

export interface CodeTestResult {
  id: string;
  test_id: string;
  status: "PASSED" | "FAILED" | "ERROR";
  details?: string | null;
}

// Измененный тип для "вопроса" - теперь это скорее "этап" или "задача" интервью
export type InterviewStep = {
  id: string; // Уникальный ID для шага/задачи
  type: "CODE_TASK" | "DIALOG"; // Тип шага: просто диалог или кодовая задача
  status: InterviewStatus;
  // Для диалога:
  question_text?: string | null; // Текст вопроса (если это просто диалоговый вопрос, не кодовая задача)
  user_answer?: string | null; // Ответ пользователя на диалоговый вопрос
  feedback?: string | null; // Фидбек по диалоговому ответу
  // Для кодовой задачи:
  code_task?: CodeTask | null; // Объект задачи по программированию
  code_task_id?: string | null;
  user_code?: string | null; // Код, написанный пользователем
  code_test_results?: CodeTestResult[];
  code_feedback?: string | null; // Фидбек от ИИ по коду
  code_score?: number | null; // Оценка за решение задачи
  // Общие поля для всех шагов
  score: number | null; // Общая оценка за этот шаг (например, 0-100)
  ai_feedback: string | null; // Фидбек от ИИ по всему шагу (диалог + код)
  created_at: string; // Дата создания
};

export type Interview = {
  id: string;
  user_id: string;
  creator_id: string;
  job_role_description: string;
  amount_of_tasks: number; // Запрошенное количество задач (вместо вопросов)
  current_step_index: number; // Индекс текущего активного шага/задачи
  status: InterviewStatus;
  created_at: string; // Формат: "2025-11-25T22:02:48.171313Z"
  updated_at: string; // Формат: "2025-11-25T22:02:48.171313Z"
  steps: InterviewStep[]; // Массив шагов/задач интервью
  chat_messages: ChatMessage[]; // Все сообщения чата (ИИ + пользователь)
  total_score: number | null;
  overall_feedback: string | null;
  key_skills: string[]; // Массив ключевых навыков
  preferences: string; // Предпочтения пользователя
  public_token: string; // Публичный токен для доступа к интервью (URL)
  ban_reasons?: string[] | null;
  banned_at?: string | null;
  result_url?: string | null;
};

export interface TestCase {
  id: string;
  input: string | Record<string, any>;
  expected_output: string | any;
}

export type CodeTestResultStatus = "passed" | "failed" | "pending" | "error";

// Тип для элемента списка интервью (без полных данных)
export type InterviewListItem = Omit<Interview, "chat_messages" | "steps"> & {
  chat_messages_count?: number;
  steps_count?: number;
  chat_messages?: ChatMessage[]; // Опционально, может быть undefined
  steps?: InterviewStep[]; // Опционально, может быть undefined
};
