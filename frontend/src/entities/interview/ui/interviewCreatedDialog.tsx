import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/shared/ui/dialog/dialog";
import { Button } from "@/shared/ui/button/button";
import { Copy, Check } from "lucide-react";
import { cn } from "@/shared/lib/mergeClass";
import { useNavigate } from "react-router-dom";
import { ERouteNames } from "@/shared/lib/routeVariables";
import { useCopied } from "@/shared/hooks/useCopy";
import { useClaimInterview } from "../hooks/useClaimInterview";

interface InterviewCreatedDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  interviewId: string;
  publicToken: string;
}

export const InterviewCreatedDialog: React.FC<InterviewCreatedDialogProps> = ({
  open,
  onOpenChange,
  interviewId,
  publicToken,
}) => {
  const navigate = useNavigate();
  const { isCopied, isPending: isCopyPending, handleCopyClick } = useCopied();
  const {
    mutate: claimInterview,
    isPending: isClaimPending,
    isError: isClaimError,
    error: claimError,
  } = useClaimInterview({
    onSuccess: (claimedInterview) => {
      navigate(
        `/${ERouteNames.DASHBOARD_ROUTE}/interview/${claimedInterview.id}`
      );
      onOpenChange(false);
    },
    onError: (error) => {
      console.error("Ошибка при принятии интервью:", error);
    },
  });

  const extractTokenFromUrl = (urlOrToken: string): string => {
    try {
      const url = new URL(urlOrToken);
      const pathParts = url.pathname.split("/").filter(Boolean);
      const claimIndex = pathParts.findIndex((part) => part === "claim");
      if (claimIndex !== -1 && pathParts[claimIndex + 1]) {
        return pathParts[claimIndex + 1];
      }
      if (pathParts.length > 0) {
        return pathParts[pathParts.length - 1];
      }
      return urlOrToken;
    } catch {
      return urlOrToken;
    }
  };

  const token = extractTokenFromUrl(publicToken);
  const interviewUrl = `${window.location.origin}/${
    ERouteNames.DASHBOARD_ROUTE
  }/claim?token=${encodeURIComponent(token)}`;

  const handleGoToInterview = () => {
    navigate(`/${ERouteNames.DASHBOARD_ROUTE}/interview/${interviewId}`);
    onOpenChange(false);
  };

  const handleLinkClick = (e: React.MouseEvent<HTMLInputElement>) => {
    e.preventDefault();
    claimInterview({ publicToken: token });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange} modal={true}>
      <DialogContent
        className="max-w-md border-0 bg-white p-7 shadow-2xl"
        closeIcon={true}
      >
        <DialogHeader className="mb-4">
          <DialogTitle className="text-left text-xl font-bold text-gray-900 mb-1.5">
            Интервью успешно создано!
          </DialogTitle>
          <DialogDescription className="text-left text-sm text-gray-600 leading-snug">
            Поделитесь ссылкой на него либо пройдите сами!
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="flex items-center gap-2 bg-zinc-100 rounded-xl">
            <input
              type="text"
              value={interviewUrl}
              readOnly
              onClick={handleLinkClick}
              className="flex-1 bg-transparent text-sm px-3 py-3.5 text-gray-700 outline-none cursor-pointer hover:bg-zinc-200 transition-colors rounded-l-xl"
              title="Нажмите, чтобы перейти к интервью"
            />
            <Button
              disabled={isCopyPending || isClaimPending}
              type="button"
              value={interviewUrl}
              onClick={handleCopyClick}
              className={cn(
                "rounded-xl px-5 py-5 text-sm font-medium transition-all cursor-pointer",
                isCopied
                  ? "bg-green-500 hover:bg-green-600 text-white"
                  : "bg-blue-600 hover:bg-blue-700 text-white"
              )}
            >
              {isCopied ? (
                <>
                  <Check className="w-4 h-4" />
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                </>
              )}
            </Button>
          </div>
        </div>

        <DialogFooter className="mt-5 flex-row justify-end gap-2">
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="rounded-xl border-gray-300 px-6 py-3 text-gray-700 hover:bg-gray-50 cursor-pointer"
          >
            Закрыть
          </Button>
          <Button
            type="button"
            onClick={handleGoToInterview}
            disabled={isClaimPending}
            className="rounded-xl bg-blue-600 px-6 py-3 text-white hover:bg-blue-700 shadow-sm cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isClaimPending ? "Загрузка..." : "Пройти интервью"}
          </Button>
          {isClaimError && (
            <p className="text-red-500 text-sm mt-2">
              {claimError?.message || "Ошибка при принятии интервью"}
            </p>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
