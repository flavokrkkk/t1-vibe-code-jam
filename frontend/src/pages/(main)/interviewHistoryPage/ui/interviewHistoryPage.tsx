import { useGetAllInterview } from "@/entities/interview/hooks/useInterview";
import { InterviewStatus } from "@/entities/interview/types/types";
import { format } from "date-fns";
import { Avatar, AvatarFallback } from "@/shared/ui/avatar/avatar";
import {
  Calendar,
  Clock,
  CheckCircle2,
  XCircle,
  Hourglass,
  Briefcase,
} from "lucide-react";
import { TagChip } from "@/shared/ui/tag/ui/badgeChip";
import { Button } from "@/shared/ui/button/button";
import { Image } from "@/shared/ui/image/image";

const statusConfig = {
  [InterviewStatus.PENDING]: {
    label: "Ожидает",
    color: "bg-gray-500",
    icon: Hourglass,
  },
  [InterviewStatus.IN_PROGRESS]: {
    label: "В процессе",
    color: "bg-blue-500",
    icon: Clock,
  },
  [InterviewStatus.COMPLETED]: {
    label: "Завершено",
    color: "bg-green-500",
    icon: CheckCircle2,
  },
  [InterviewStatus.CANCELLED]: {
    label: "Отменено",
    color: "bg-red-500",
    icon: XCircle,
  },
};

const InterviewHistoryPage = () => {
  const { data: interviews = [], isLoading } = useGetAllInterview();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Загрузка истории интервью...</div>
      </div>
    );
  }

  if (interviews.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="bg-gray-200 border-2 border-dashed rounded-xl w-24 h-24 mx-auto mb-6" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Нет пройденных интервью
          </h3>
          <p className="text-gray-500">Начните своё первое собеседование!</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="max-w-7xl mx-auto px-6 pb-12 space-y-4">
        <div className="relative mt-4">
          <Image
            src="/images/blue-banner-v2.png"
            alt="vacancy-banner"
            className="rounded-4xl w-full max-h-60"
          />

          <div className="absolute inset-0 flex flex-col justify-between p-6">
            <div className="flex justify-between items-start">
              <h1 className="text-3xl font-semibold text-white">
                Все ваши собеседования в одном месте
              </h1>
            </div>
          </div>
        </div>
        <div className="grid gap-8 md:grid-cols-2">
          {interviews.map((interview) => {
            const StatusIcon = statusConfig[interview.status].icon;
            const totalSteps = interview.amount_of_tasks;
            const completedSteps =
              interview.current_step_index +
              (interview.status === InterviewStatus.COMPLETED ? 1 : 0);
            const progress =
              totalSteps > 0 ? (completedSteps / totalSteps) * 100 : 0;

            return (
              <div
                key={interview.id}
                className="bg-white rounded-4xl transition-all duration-300 overflow-hidden group"
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-5">
                    <div className="flex items-center gap-3">
                      <Avatar className="w-12 h-12 ring-4 ring-blue-100">
                        <AvatarFallback className="bg-gradient-to-br from-blue-500 to-cyan-500 text-white font-bold">
                          <Briefcase className="w-6 h-6" />
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex flex-col -space-y-1.5">
                        <h3 className="font-bold text-lg text-gray-900 line-clamp-2">
                          {interview.job_role_description || "Собеседование"}
                        </h3>
                        <p className="text-sm text-gray-500 flex items-center gap-1 mt-1">
                          <Calendar className="w-3 h-3" />
                          {format(
                            new Date(interview.created_at),
                            "dd MMM yyyy"
                          )}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="mb-5">
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-600">Прогресс</span>
                      <span className="font-medium text-gray-900">
                        {completedSteps} из {totalSteps}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 transition-all duration-700"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="bg-blue-100 rounded-2xl p-4 text-center">
                      <p className="text-2xl font-bold text-blue-600">
                        {interview.chat_messages?.length ??
                          interview.chat_messages_count ??
                          0}
                      </p>
                      <p className="text-xs text-gray-600">Сообщений</p>
                    </div>
                    {interview.total_score !== null && (
                      <div className="bg-green-100 rounded-2xl p-4 text-center">
                        <p className="text-2xl font-bold text-green-600">
                          {interview.total_score}
                        </p>
                        <p className="text-xs text-gray-600">Баллов</p>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center justify-between">
                    <TagChip
                      className={`${
                        statusConfig[interview.status].color
                      } text-white border-0 flex items-center gap-2`}
                    >
                      <StatusIcon className="w-3 h-3" />
                      {statusConfig[interview.status].label}
                    </TagChip>

                    <Button
                      variant="ghost"
                      size="sm"
                      className="bg-blue-50 text-blue-600 hover:text-blue-600 transition-all cursor-pointer"
                    >
                      {interview.status === InterviewStatus.COMPLETED
                        ? "Посмотреть"
                        : "Продолжить"}
                    </Button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default InterviewHistoryPage;
