import { useQuery } from "@tanstack/react-query";
import { getCurrentCustomer } from "../api/userService";

export const CURRENT_USER_QUERY = "current-user-query";

export const useCurrentUser = () => {
  return useQuery({
    queryKey: [CURRENT_USER_QUERY],
    queryFn: getCurrentCustomer,
  });
};
