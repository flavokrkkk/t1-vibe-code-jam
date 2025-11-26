import { CodeTask, Interview, InterviewStatus } from "../types/types";

const mockCodeTask1: CodeTask = {
  id: "code_task_1",
  description: `Дана строка 's' и целое число 'numRows'. Ваша задача - преобразовать 's' в зигзагообразный паттерн на заданном количестве строк и затем прочитать его построчно.
  
  Например, если numRows = 3:
  
  P   A   H   N
  A P L S I I G
  Y   I   R
  
  А затем прочитать его построчно: "PAHNAPLSIIGYIR".
  
  Напишите функцию \`convert(s: string, numRows: number): string\`
  `,
  initial_code: `function convert(s: string, numRows: number): string {
    // Ваше решение здесь
    return "";
};`,
  language: "typescript",
  test_cases: [
    {
      id: "1",
      input: { s: "PAYPALISHIRING", numRows: 3 },
      expected_output: "PAHNAPLSIIGYIR",
    },
    {
      id: "2",
      input: { s: "PAYPALISHIRING", numRows: 4 },
      expected_output: "PINALSIGYAHRPI",
    },
    {
      id: "3",
      input: { s: "A", numRows: 1 },
      expected_output: "A",
    },
  ],
};

export const mockInterviewData: Interview = {
  id: "int_tech_dev_456",
  user_id: "user_abc",
  job_role_description: "Frontend Developer (React, TypeScript)",
  amount_of_tasks: 3,
  current_step_index: 1,
  status: InterviewStatus.IN_PROGRESS,
  created_at: "2024-06-13T09:00:00Z",
  updated_at: "2024-06-13T09:00:00Z",
  steps: [
    {
      id: "step_welcome",
      type: "DIALOG",
      status: InterviewStatus.COMPLETED,
      question_text: "Приветствие",
      ai_feedback: null,
      score: null,
      created_at: "2024-06-13T09:00:00Z",
    },
    {
      id: "step_code_1",
      type: "CODE_TASK",
      status: InterviewStatus.IN_PROGRESS,
      code_task: mockCodeTask1,
      user_code: mockCodeTask1.initial_code,
      code_test_results: [],
      code_feedback: null,
      code_score: null,
      ai_feedback: null,
      score: null,
      created_at: "2024-06-13T09:00:00Z",
    },
    {
      id: "step_code_2",
      type: "CODE_TASK",
      status: InterviewStatus.PENDING,
      code_task: null,
      code_test_results: [],
      code_feedback: null,
      code_score: null,
      ai_feedback: null,
      score: null,
      created_at: "2024-06-13T09:00:00Z",
    },
    {
      id: "step_code_3",
      type: "CODE_TASK",
      status: InterviewStatus.PENDING,
      code_task: null,
      code_test_results: [],
      code_feedback: null,
      code_score: null,
      ai_feedback: null,
      score: null,
      created_at: "2024-06-13T09:00:00Z",
    },
  ],
  chat_messages: [
    {
      id: "msg_welcome_1",
      sender: "AI",
      text: "Привет! Добро пожаловать на VibeCode Jam. Я ваш виртуальный интервьюер для роли Frontend Developer. Мы начнем с серии задач по программированию. Вы можете задавать мне вопросы, если застряли, или когда будете готовы перейти к следующей задаче.",
      created_at: "2024-06-13T09:00:05Z",
    },
    {
      id: "msg_task_intro_1",
      sender: "AI",
      text: "Ваша первая задача: **Zigzag Conversion**.",
      created_at: "2024-06-13T09:00:07Z",
    },
    {
      id: "msg_task_desc_1",
      sender: "AI",
      text: mockCodeTask1.description,
      created_at: "2024-06-13T09:00:10Z",
    },
    {
      id: "msg_task_desc_2",
      sender: "USER",
      text: "Готов перейти к следующей",
      created_at: "2024-06-13T09:00:10Z",
    },
  ],
  total_score: null,
  overall_feedback: null,
};
