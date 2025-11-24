import {
  createContext,
  FC,
  PropsWithChildren,
  useContext,
  useState,
} from "react";
import { deleteAccessToken, setAccessToken } from "@/entities/token";
import { IViewerContext, IViewerState } from "./types";

const ViewerContext = createContext<IViewerContext>({
  isAuthenticated: false,
  loginViewer: () => {},
  logoutViewer: () => {},
});

export const useViewer = () => {
  return useContext(ViewerContext);
};

export const ViewerProvider: FC<PropsWithChildren> = ({ children }) => {
  const [viewer, setViewer] = useState<IViewerState>({
    isAuthenticated: false,
  });

  const handleLoginViewer = (accessToken: string) => {
    setViewer({
      isAuthenticated: true,
      accessToken,
    });
    setAccessToken(accessToken);
  };

  const handleLogoutViewer = () => {
    setViewer({
      isAuthenticated: false,
      accessToken: null,
    });
    deleteAccessToken();
  };

  return (
    <ViewerContext.Provider
      value={{
        ...viewer,
        loginViewer: handleLoginViewer,
        logoutViewer: handleLogoutViewer,
      }}
    >
      {children}
    </ViewerContext.Provider>
  );
};
