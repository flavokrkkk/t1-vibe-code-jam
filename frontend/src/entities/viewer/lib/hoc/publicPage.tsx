import { FC, PropsWithChildren, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useViewer } from "../../model/context/providers";
import { getAccessToken } from "@/entities/token";
import { Image } from "@/shared/ui/image/image";
import { ERouteNames } from "@/shared/lib/routeVariables";

export const publicPage = (children: React.ReactNode) => {
  return <PublicPage>{children}</PublicPage>;
};

const PublicPage: FC<PropsWithChildren> = ({ children }) => {
  const { loginViewer } = useViewer();
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = getAccessToken();

    if (token) {
      loginViewer(token);
      navigate(`/${ERouteNames.DEFAULT_ROUTE}`);
    } else {
      setIsLoading(false);
    }
  }, [loginViewer, navigate]);

  if (isLoading) {
    return (
      <div className="h-screen w-full flex items-center justify-center">
        <Image
          alt="logo-suspese"
          src="/images/logo.jpg"
          className="w-6 h-6 rounded-sm animate-ping"
        />
      </div>
    );
  }

  return children;
};
