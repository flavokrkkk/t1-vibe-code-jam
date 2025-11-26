import React from "react";
import { useNavigate } from "react-router-dom";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/shared/ui/dialog/dialog";
import { Button } from "@/shared/ui/button/button";
import { ERouteNames } from "@/shared/lib/routeVariables";

interface AntiCheatRulesDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onAccept: () => void;
}

export const AntiCheatRulesDialog: React.FC<AntiCheatRulesDialogProps> = ({
  open,
  onOpenChange,
  onAccept,
}) => {
  const navigate = useNavigate();

  const handleAccept = () => {
    onAccept();
    onOpenChange(false);
  };

  const handleCancel = () => {
    navigate(`/${ERouteNames.DASHBOARD_ROUTE}`, { replace: true });
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      handleCancel();
      return;
    }
    onOpenChange(newOpen);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange} modal={true}>
      <DialogContent
        className="max-w-2xl border-0 bg-white p-7 shadow-2xl"
        onEscapeKeyDown={(e) => e.preventDefault()}
        onPointerDownOutside={(e) => e.preventDefault()}
        onInteractOutside={(e) => e.preventDefault()}
      >
        <DialogHeader className="mb-4">
          <DialogTitle className="text-left text-xl font-bold text-gray-900 mb-1.5">
            Правила античитинга
          </DialogTitle>
          <DialogDescription className="text-left text-sm text-gray-600 leading-snug">
            При нарушении правил вы получите предупреждение. Все нарушения
            фиксируются в процессе интервью.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2.5">
            <h4 className="font-semibold text-base text-gray-900 flex items-center gap-2">
              Запрещенные действия
            </h4>
            <div className="grid grid-cols-2 gap-2">
              {[
                {
                  title: "Переключение вкладок",
                  desc: "Другие вкладки браузера",
                },
                {
                  title: "Потеря фокуса",
                  desc: "Другие приложения",
                },
                {
                  title: "DevTools",
                  desc: "F12, Ctrl+Shift+I",
                },
                {
                  title: "Копирование/вставка",
                  desc: "Ctrl+C, Ctrl+V, Ctrl+X",
                },
                {
                  title: "Контекстное меню",
                  desc: "Правый клик",
                },
                {
                  title: "Выделение текста",
                  desc: "Заблокировано",
                },
                {
                  title: "Скриншоты",
                  desc: "PrintScreen",
                },
              ].map((item, index) => (
                <div
                  key={index}
                  className="flex items-start gap-2 p-2 rounded-lg bg-zinc-100 hover:bg-zinc-50 cursor-pointer transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 text-xs mb-0.5">
                      {item.title}
                    </p>
                    <p className="text-xs text-gray-600 leading-tight">
                      {item.desc}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <DialogFooter className="mt-5 flex-row justify-start gap-1">
          <Button
            type="button"
            variant="outline"
            onClick={handleCancel}
            className="rounded-xl border-gray-300 px-6 py-3 text-gray-700 hover:bg-gray-50 cursor-pointer"
          >
            Отмена
          </Button>
          <Button
            type="button"
            onClick={handleAccept}
            className="rounded-xl bg-blue-600 px-6 py-3 text-white hover:bg-blue-700 shadow-sm cursor-pointer"
          >
            Я согласен с правилами
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
