import { routes } from "@/pages/routes";
import { Provider } from "react-redux";
import { RouterProvider } from "react-router-dom";
import { store } from "../store";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/shared/api/queryClient";

export const Providers = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <Provider store={store}>
        <RouterProvider router={routes} />
      </Provider>
    </QueryClientProvider>
  );
};
