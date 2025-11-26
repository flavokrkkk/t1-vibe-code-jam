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

export const authApi = ky.create({
  prefixUrl: API_BASE_URL,
  timeout: 10000, // Базовый таймаут для обычных запросов
  hooks: {
    beforeRequest: [
      (request) => {
        const token = getAccessToken();
        if (token) {
          request.headers.set("Authorization", `Bearer ${token}`);
        }
      },
    ],
    afterResponse: [
      async (request, options, response) => {
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
  parseJson: (text) => JSON.parse(text),
});
