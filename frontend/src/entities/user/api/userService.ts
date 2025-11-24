import { authApi } from "@/shared/api/baseQueryInstance";
import { ErrorMessages } from "@/shared/api/queryError";
import { User } from "../types/types";

class CustomerService {
  public async getCurrentCustomer(): Promise<User> {
    try {
      const response = await authApi.get("user").json<User>();
      return response;
    } catch (error) {
      throw new Error(ErrorMessages.REQUEST_PREPARATION_ERROR);
    }
  }
}

export const { getCurrentCustomer } = new CustomerService();
