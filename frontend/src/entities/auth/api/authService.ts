import { authApi, publicApi } from "@/shared/api/baseQueryInstance";
import {
  LoginDto,
  RegisterDto,
  AuthResponse,
  RefreshDto,
  RefreshResponse,
} from "../types/types";
import { EAuthEndpoints } from "../lib/endpoints";
import { ErrorMessages } from "@/shared/api/queryError";

class AuthService {
  public async register(registerDto: RegisterDto): Promise<AuthResponse> {
    try {
      return await publicApi
        .post(EAuthEndpoints.AUTH_REGISTER, {
          json: registerDto,
        })
        .json<AuthResponse>();
    } catch (error) {
      throw new Error(ErrorMessages.REQUEST_PREPARATION_ERROR);
    }
  }

  public async login(loginDto: LoginDto): Promise<AuthResponse> {
    try {
      return await publicApi
        .post(EAuthEndpoints.AUTH_LOGIN, {
          json: loginDto,
        })
        .json<AuthResponse>();
    } catch (error) {
      throw new Error(ErrorMessages.REQUEST_PREPARATION_ERROR);
    }
  }

  public async refreshToken(refreshDto: RefreshDto): Promise<RefreshResponse> {
    try {
      return await authApi
        .post(EAuthEndpoints.AUTH_REFRESH, {
          json: refreshDto,
        })
        .json<RefreshResponse>();
    } catch (error) {
      throw new Error(ErrorMessages.REQUEST_PREPARATION_ERROR);
    }
  }
}

export const { login, register, refreshToken } = new AuthService();
