import React from "react";
import { Interview } from "@/entities/interview/types/types";
import {
  Page,
  Text,
  View,
  Document,
  StyleSheet,
  Font,
} from "@react-pdf/renderer";

// Регистрация шрифта для поддержки кириллицы
const getFontPath = (filename: string) => {
  if (typeof window !== "undefined") {
    return `${window.location.origin}/fonts/${filename}`;
  }
  return `/fonts/${filename}`;
};

Font.register({
  family: "Aeroport",
  fonts: [
    { src: getFontPath("Aeroport.ttf") },
    { src: getFontPath("Aeroport-Bold.ttf"), fontWeight: "bold" },
    { src: getFontPath("Aeroport-Italic.ttf"), fontStyle: "italic" },
    {
      src: getFontPath("Aeroport-BoldItalic.ttf"),
      fontWeight: "bold",
      fontStyle: "italic",
    },
  ],
});

// Стили
const styles = StyleSheet.create({
  page: {
    padding: 40,
    fontSize: 12,
    color: "#333",
    fontFamily: "Aeroport",
  },
  headerContainer: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 20,
    borderBottom: "2 solid #3d66ff",
    paddingBottom: 10,
  },
  headerText: {
    fontSize: 22,
    fontWeight: "bold",
    color: "#3d66ff",
  },
  section: {
    marginBottom: 15,
    padding: 10,
    borderRadius: 6,
    backgroundColor: "#F7F9FC",
  },
  label: {
    fontWeight: "bold",
    color: "#3d66ff",
    marginBottom: 4,
  },
  divider: {
    marginVertical: 10,
    borderBottom: "1 solid #E0E0E0",
  },
  text: {
    marginBottom: 4,
    lineHeight: 1.5,
  },
  stepContainer: {
    marginBottom: 15,
    padding: 10,
    backgroundColor: "#FFFFFF",
    border: "1 solid #E0E0E0",
    borderRadius: 4,
  },
  stepTitle: {
    fontWeight: "bold",
    color: "#333",
    marginBottom: 6,
    fontSize: 13,
  },
  codeBlock: {
    backgroundColor: "#F5F5F5",
    padding: 8,
    borderRadius: 4,
    fontFamily: "Courier",
    fontSize: 10,
    marginTop: 4,
  },
  chatMessage: {
    marginBottom: 8,
    padding: 6,
    backgroundColor: "#FAFAFA",
    borderRadius: 4,
  },
  chatSender: {
    fontWeight: "bold",
    marginBottom: 2,
    fontSize: 10,
  },
  chatText: {
    fontSize: 10,
    lineHeight: 1.4,
  },
});

const sanitize = (text?: string | null) =>
  text
    ? text
        .replace(/[\x00-\x1F\x7F-\x9F]/g, "")
        .replace(/\s+/g, " ")
        .trim()
    : "";

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString("ru-RU", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

interface InterviewReportProps {
  interview: Interview;
}

const InterviewReport: React.FC<InterviewReportProps> = ({ interview }) => {
  const dialogSteps = interview.steps.filter((step) => step.type === "DIALOG");
  const codeTaskSteps = interview.steps.filter(
    (step) => step.type === "CODE_TASK"
  );

  const averageDialogScore =
    dialogSteps.length > 0
      ? dialogSteps.reduce((sum, step) => sum + (step.score || 0), 0) /
        dialogSteps.length
      : 0;

  const averageCodeScore =
    codeTaskSteps.length > 0
      ? codeTaskSteps.reduce((sum, step) => sum + (step.code_score || 0), 0) /
        codeTaskSteps.length
      : 0;

  return (
    <Document>
      <Page style={styles.page}>
        <View style={styles.headerContainer}>
          <Text style={styles.headerText}>Отчет о результатах интервью</Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.text}>
            <Text style={styles.label}>Должность:</Text>{" "}
            {sanitize(interview.job_role_description)}
          </Text>
          <Text style={styles.text}>
            <Text style={styles.label}>Дата создания:</Text>{" "}
            {formatDate(interview.created_at)}
          </Text>
          {interview.updated_at && (
            <Text style={styles.text}>
              <Text style={styles.label}>Дата завершения:</Text>{" "}
              {formatDate(interview.updated_at)}
            </Text>
          )}
          <Text style={styles.text}>
            <Text style={styles.label}>Статус:</Text>{" "}
            {interview.status === "COMPLETED" ? "Завершено" : interview.status}
          </Text>
          {interview.total_score !== null && (
            <Text style={styles.text}>
              <Text style={styles.label}>Общая оценка:</Text>{" "}
              {interview.total_score}/100
            </Text>
          )}
        </View>

        {interview.overall_feedback && (
          <View style={styles.section}>
            <Text style={styles.label}>Общий фидбек:</Text>
            <Text style={styles.text}>
              {sanitize(interview.overall_feedback)}
            </Text>
          </View>
        )}

        <View style={styles.section}>
          <Text style={styles.label}>Статистика:</Text>
          <Text style={styles.text}>
            Диалоговые вопросы: {dialogSteps.length}
          </Text>
          <Text style={styles.text}>
            Средняя оценка за диалог: {averageDialogScore.toFixed(1)}/100
          </Text>
          <Text style={styles.text}>
            Кодовые задачи: {codeTaskSteps.length}
          </Text>
          <Text style={styles.text}>
            Средняя оценка за код: {averageCodeScore.toFixed(1)}/100
          </Text>
        </View>

        {interview.steps.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.label}>Детальные результаты по шагам:</Text>
            {interview.steps.map((step, index) => (
              <View key={step.id} style={styles.stepContainer}>
                <Text style={styles.stepTitle}>
                  Шаг {index + 1}:{" "}
                  {step.type === "DIALOG" ? "Диалог" : "Кодовая задача"}
                </Text>

                {step.question_text && (
                  <Text style={styles.text}>
                    <Text style={styles.label}>Вопрос:</Text>{" "}
                    {sanitize(step.question_text)}
                  </Text>
                )}

                {step.user_answer && (
                  <Text style={styles.text}>
                    <Text style={styles.label}>Ответ:</Text>{" "}
                    {sanitize(step.user_answer)}
                  </Text>
                )}

                {step.type === "CODE_TASK" && step.code_task && (
                  <>
                    {step.code_task.description && (
                      <Text style={styles.text}>
                        <Text style={styles.label}>Описание задачи:</Text>{" "}
                        {sanitize(step.code_task.description)}
                      </Text>
                    )}
                    {step.user_code && (
                      <View style={styles.codeBlock}>
                        <Text style={styles.label}>Код кандидата:</Text>
                        <Text>{sanitize(step.user_code)}</Text>
                      </View>
                    )}
                  </>
                )}

                {step.score !== null && (
                  <Text style={styles.text}>
                    <Text style={styles.label}>Оценка:</Text> {step.score}/100
                  </Text>
                )}

                {step.type === "CODE_TASK" && step.code_score !== null && (
                  <Text style={styles.text}>
                    <Text style={styles.label}>Оценка за код:</Text>{" "}
                    {step.code_score}/100
                  </Text>
                )}

                {step.feedback && (
                  <Text style={styles.text}>
                    <Text style={styles.label}>Фидбек:</Text>{" "}
                    {sanitize(step.feedback)}
                  </Text>
                )}

                {step.code_feedback && (
                  <Text style={styles.text}>
                    <Text style={styles.label}>Фидбек по коду:</Text>{" "}
                    {sanitize(step.code_feedback)}
                  </Text>
                )}

                {step.ai_feedback && (
                  <Text style={styles.text}>
                    <Text style={styles.label}>AI Фидбек:</Text>{" "}
                    {sanitize(step.ai_feedback)}
                  </Text>
                )}
              </View>
            ))}
          </View>
        )}

        {/* История чата */}
        {interview.chat_messages.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.label}>История чата:</Text>
            {interview.chat_messages.map((msg) => (
              <View key={msg.id} style={styles.chatMessage}>
                <Text style={styles.chatSender}>
                  {msg.sender === "USER" ? "Кандидат" : "AI Интервьюер"} (
                  {formatDate(msg.created_at)}):
                </Text>
                <Text style={styles.chatText}>{sanitize(msg.text)}</Text>
              </View>
            ))}
          </View>
        )}
      </Page>
    </Document>
  );
};

export default InterviewReport;
