import { authApi } from "@/shared/api/baseQueryInstance";
import { Interview } from "../types/types";
import { ErrorMessages } from "@/shared/api/queryError";

import { EInterviewEndpoints } from "../lib/endpoints";
import { CreateInterviewFormData } from "../lib/schemes/createInterviewSchema";

class InterviewService {
  public async createInterview(
    createInterviewDto: CreateInterviewFormData
  ): Promise<Interview> {
    try {
      return await authApi
        .post(EInterviewEndpoints.INTERVIEWS, {
          json: createInterviewDto,
        })
        .json<Interview>();
    } catch (error) {
      throw new Error(ErrorMessages.REQUEST_PREPARATION_ERROR);
    }
  }

  public async getAllInterviews(): Promise<Interview[]> {
    try {
      return await authApi
        .get(EInterviewEndpoints.INTERVIEWS)
        .json<Interview[]>();
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
        .get(`${EInterviewEndpoints.INTERVIEWS}/${interviewId}`)
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
      return await authApi
        .post(
          `${EInterviewEndpoints.INTERVIEWS}/${interviewId}/steps/${stepId}/code`,
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
      return await authApi
        .post(`${EInterviewEndpoints.INTERVIEWS}/${interviewId}/message`, {
          json: { text },
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
        .post(`${EInterviewEndpoints.INTERVIEWS}/${interviewId}/audio`, {
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
}

export const {
  createInterview,
  getAllInterviews,
  getInterviewById,
  submitCode,
  sendChatMessage,
  sendAudioMessage,
} = new InterviewService();
