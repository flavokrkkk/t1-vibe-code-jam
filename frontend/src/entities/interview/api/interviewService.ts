import { authApi, authApiLongTimeout } from "@/shared/api/baseQueryInstance";
import { Interview, InterviewListItem } from "../types/types";
import { ErrorMessages } from "@/shared/api/queryError";

import { EInterviewEndpoints } from "../lib/endpoints";
import { CreateInterviewFormData } from "../lib/schemes/createInterviewSchema";

class InterviewService {
  public async createInterview(
    createInterviewDto: CreateInterviewFormData
  ): Promise<Interview> {
    try {
      return await authApiLongTimeout
        .post(EInterviewEndpoints.INTERVIEWS_CREATE, {
          json: createInterviewDto,
        })
        .json<Interview>();
    } catch (error) {
      if (error instanceof Error) {
        if (
          error.name === "TimeoutError" ||
          error.message.includes("timeout")
        ) {
          throw new Error(
            "Превышено время ожидания. Создание интервью занимает больше времени из-за генерации задач. Попробуйте еще раз."
          );
        }
        if (
          error.message.includes("canceled") ||
          error.message.includes("aborted")
        ) {
          throw new Error(
            "Запрос был отменен. Убедитесь, что ML сервис запущен и доступен."
          );
        }
      }
      console.error("Error creating interview:", error);
      throw new Error(ErrorMessages.REQUEST_PREPARATION_ERROR);
    }
  }

  public async getAllInterviews(): Promise<InterviewListItem[]> {
    try {
      return await authApi
        .get(EInterviewEndpoints.INTERVIEWS_GET)
        .json<InterviewListItem[]>();
    } catch (error) {
      throw new Error(ErrorMessages.REQUEST_PREPARATION_ERROR);
    }
  }

  public async getInterviewById({
    interviewId,
  }: {
    interviewId: string;
  }): Promise<Interview> {
    try {
      return await authApi
        .get(`${EInterviewEndpoints.INTERVIEWS_CREATE}/${interviewId}`)
        .json<Interview>();
    } catch (error) {
      throw new Error(ErrorMessages.REQUEST_PREPARATION_ERROR);
    }
  }

  public async submitCode({
    interviewId,
    stepId,
    userCode,
  }: {
    interviewId: string;
    stepId: string;
    userCode: string;
  }): Promise<Interview> {
    try {
      return await authApiLongTimeout
        .post(
          `${EInterviewEndpoints.INTERVIEWS_CREATE}/${interviewId}/steps/${stepId}/code`,
          {
            json: { user_code: userCode },
          }
        )
        .json<Interview>();
    } catch (error) {
      console.error(
        `Error submitting code for interview ${interviewId}, step ${stepId}:`,
        error
      );
      throw new Error(ErrorMessages.REQUEST_PREPARATION_ERROR);
    }
  }

  public async sendChatMessage({
    interviewId,
    text,
  }: {
    interviewId: string;
    text: string;
  }): Promise<Interview> {
    try {
      return await authApiLongTimeout
        .post(
          `${EInterviewEndpoints.INTERVIEWS_CREATE}/${interviewId}/message`,
          {
            json: { text },
          }
        )
        .json<Interview>();
    } catch (error) {
      throw new Error(
        error instanceof Error
          ? error.message
          : ErrorMessages.REQUEST_PREPARATION_ERROR
      );
    }
  }

  public async sendAudioMessage({
    interviewId,
    audioBlob,
  }: {
    interviewId: string;
    audioBlob: Blob;
  }): Promise<Interview> {
    try {
      const formData = new FormData();
      formData.append("audio", audioBlob, "audio.webm");

      return await authApi
        .post(`${EInterviewEndpoints.INTERVIEWS_CREATE}/${interviewId}/audio`, {
          body: formData,
          timeout: 120000,
        })
        .json<Interview>();
    } catch (error) {
      throw new Error(
        error instanceof Error
          ? error.message
          : ErrorMessages.REQUEST_PREPARATION_ERROR
      );
    }
  }

  public async claimInterview({
    publicToken,
  }: {
    publicToken: string;
  }): Promise<Interview> {
    try {
      return await authApi
        .get(`${EInterviewEndpoints.INTERVIEWS_CREATE}/claim/`, {
          searchParams: { public_token: publicToken },
        })
        .json<Interview>();
    } catch (error) {
      throw new Error(
        error instanceof Error
          ? error.message
          : ErrorMessages.REQUEST_PREPARATION_ERROR
      );
    }
  }
}

export const {
  createInterview,
  getAllInterviews,
  getInterviewById,
  submitCode,
  sendChatMessage,
  sendAudioMessage,
  claimInterview,
} = new InterviewService();
