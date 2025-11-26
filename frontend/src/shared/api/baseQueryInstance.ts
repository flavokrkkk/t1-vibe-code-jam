import { refreshToken } from "@/entities/auth/api/authService";
import {
  getAccessToken,
  getRefreshToken,
  setAccessToken,
  setRefreshToken,
} from "@/entities/token";
import ky from "ky";

const API_BASE_URL = "http://localhost:8000/api/v1/";

export const publicApi = ky.create({
  prefixUrl: API_BASE_URL,
  timeout: 10000,
  parseJson: (text) => JSON.parse(text),
});

const authApiConfig = {
  prefixUrl: API_BASE_URL,
  hooks: {
    beforeRequest: [
      (request: Request) => {
        const token = getAccessToken();
        if (token) {
          request.headers.set("Authorization", `Bearer ${token}`);
        }
      },
    ],
    afterResponse: [
      async (request: Request, options: RequestInit, response: Response) => {
        if (response.status === 401) {
          const refresh = getRefreshToken();
          if (!refresh) {
            console.warn("Refresh token missing, redirecting to login...");
            return response;
          }

          const refreshResponse = await refreshToken({
            refresh_token: refresh,
          });

          if (refreshResponse?.access_token) {
            setAccessToken(refreshResponse.access_token);
            setRefreshToken(refreshResponse.refresh_token);

            return ky(request, {
              ...options,
              headers: {
                ...options.headers,
                Authorization: `Bearer ${refreshResponse.access_token}`,
              },
            });
          }
        }

        return response;
      },
    ],
  },
  parseJson: (text: string) => JSON.parse(text),
};

// Базовый API с обычным таймаутом для быстрых запросов
export const authApi = ky.create({
  ...authApiConfig,
  timeout: 10000,
});

// API с увеличенным таймаутом для длительных операций (ML сервис, обработка кода)
export const authApiLongTimeout = ky.create({
  ...authApiConfig,
  timeout: 90000, // 90 секунд для операций с ML сервисом
});
