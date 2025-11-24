import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import {
  setAccessToken,
  setRefreshToken,
} from "@/entities/token/lib/tokenService";
import { login } from "../api/authService";
import { ERouteNames } from "@/shared/lib/routeVariables";

export const LOGIN_QUERY = "login-query";

export const useLoginMutation = () => {
  const navigate = useNavigate();

  return useMutation({
    mutationKey: [LOGIN_QUERY],
    mutationFn: login,
    onSuccess: (data) => {
      if (!data) return;

      setAccessToken(data.access_token);
      setRefreshToken(data.refresh_token);

      return navigate(`/${ERouteNames.DASHBOARD_ROUTE}`);
    },
  });
};
