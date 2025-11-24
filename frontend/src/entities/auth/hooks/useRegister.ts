import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { register } from "../api/authService";
import {
  setAccessToken,
  setRefreshToken,
} from "@/entities/token/lib/tokenService";
import { ERouteNames } from "@/shared/lib/routeVariables";

export const REGISTER_QUERY = "register-query";

export const useRegisterMutation = () => {
  const navigate = useNavigate();

  return useMutation({
    mutationKey: [REGISTER_QUERY],
    mutationFn: register,
    onSuccess: (data) => {
      if (!data) return;

      setAccessToken(data.access_token);
      setRefreshToken(data.refresh_token);

      return navigate(`/${ERouteNames.DASHBOARD_ROUTE}`);
    },
  });
};
