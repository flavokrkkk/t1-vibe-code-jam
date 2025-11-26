import { useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { useClaimInterview } from "@/entities/interview/hooks/useClaimInterview";
import { ERouteNames } from "@/shared/lib/routeVariables";

const ClaimInterviewPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get("token");

  const {
    mutate: claimInterview,
    isPending,
    isError,
    error,
  } = useClaimInterview({
    onSuccess: (claimedInterview) => {
      navigate(
        `/${ERouteNames.DASHBOARD_ROUTE}/interview/${claimedInterview.id}`,
        {
          replace: true,
        }
      );
    },
    onError: (error) => {
      console.error("Ошибка при принятии интервью:", error);
      // Редирект на дашборд при ошибке
      setTimeout(() => {
        navigate(`/${ERouteNames.DASHBOARD_ROUTE}`, { replace: true });
      }, 2000);
    },
  });

  useEffect(() => {
    if (token) {
      claimInterview({ publicToken: token });
    } else {
      navigate(`/${ERouteNames.DASHBOARD_ROUTE}`, { replace: true });
    }
  }, [token, claimInterview, navigate]);

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gradient-to-br from-[#e0f2f7] to-[#fce4ec]">
      <div className="absolute inset-0 z-0 pointer-events-none">
        <div className="absolute top-10 left-10 w-48 h-48 bg-purple-500 opacity-20 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
        <div className="absolute bottom-10 right-10 w-48 h-48 bg-pink-400 opacity-20 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
      </div>
      <div className="relative z-10 text-center">
        {isPending && (
          <div className="space-y-4">
            <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p className="text-gray-700 text-lg font-medium">
              Принятие интервью...
            </p>
          </div>
        )}
        {isError && (
          <div className="space-y-4">
            <p className="text-red-600 text-lg font-medium">
              {error?.message || "Ошибка при принятии интервью"}
            </p>
            <p className="text-gray-600 text-sm">
              Перенаправление на главную страницу...
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ClaimInterviewPage;
