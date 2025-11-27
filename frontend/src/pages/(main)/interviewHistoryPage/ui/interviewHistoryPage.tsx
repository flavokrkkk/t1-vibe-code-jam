import { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { useGetAllInterview } from "@/entities/interview/hooks/useInterview";
import {
  InterviewStatus,
  InterviewListItem,
} from "@/entities/interview/types/types";
import { useCurrentUser } from "@/entities/user/hooks/useCurrentUser";
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
import { ERouteNames } from "@/shared/lib/routeVariables";

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

type TabType = "my" | "shared";

const InterviewHistoryPage = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabType>("my");
  const { data: interviews = [], isLoading } = useGetAllInterview();
  const { data: currentUser, isLoading: isUserLoading } = useCurrentUser();
  const [expandedCheatingByInterviewId, setExpandedCheatingByInterviewId] =
    useState<Record<string, boolean>>({});

  const { myInterviews, sharedInterviews } = useMemo(() => {
    if (!currentUser) {
      return { myInterviews: [], sharedInterviews: [] };
    }

    const my: InterviewListItem[] = [];
    const shared: InterviewListItem[] = [];

    interviews.forEach((interview) => {
      // "Мои интервью" - интервью, где пользователь является участником
      const isMyInterview = interview.user_id === currentUser.id;

      // "Интервью по моей ссылке" - интервью, созданные пользователем, но проходимые другими
      const isSharedInterview =
        interview.creator_id === currentUser.id &&
        interview.user_id !== currentUser.id;

      if (isMyInterview) {
        my.push(interview);
      } else if (isSharedInterview) {
        shared.push(interview);
      }
    });

    return { myInterviews: my, sharedInterviews: shared };
  }, [interviews, currentUser]);

  const currentInterviews =
    activeTab === "my" ? myInterviews : sharedInterviews;

  if (isLoading || isUserLoading) {
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
      <div className="max-w-6xl mx-auto px-6 pb-12 space-y-4">
        <div className="relative mt-4">
          <Image
            src="/images/blue-banner-v2.png"
            alt="vacancy-banner"
            className="rounded-4xl w-full max-h-60"
          />

          <div className="absolute inset-0 flex flex-col justify-between p-6">
            <div className="flex justify-between items-start">
              <h1 className="text-3xl font-semibold text-white">
                Все ваши интервью в одном месте
              </h1>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-1.5 shadow-sm border border-gray-100">
          <div className="relative flex">
            <motion.div
              className="absolute top-0 bottom-0 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl"
              initial={false}
              animate={{
                left: activeTab === "my" ? "0%" : "50%",
                width: "50%",
              }}
              transition={{
                type: "spring",
                stiffness: 300,
                damping: 30,
              }}
            />
            <button
              type="button"
              onClick={() => setActiveTab("my")}
              className="relative z-10 flex-1 px-6 py-3 text-sm font-semibold rounded-xl transition-colors duration-200"
            >
              <motion.span
                className="relative block"
                animate={{
                  color: activeTab === "my" ? "#ffffff" : "#6b7280",
                }}
                transition={{ duration: 0.2 }}
              >
                Мои интервью
                {myInterviews.length > 0 && (
                  <span className="ml-2 text-xs opacity-80">
                    ({myInterviews.length})
                  </span>
                )}
              </motion.span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("shared")}
              className="relative z-10 flex-1 px-6 py-3 text-sm font-semibold rounded-xl transition-colors duration-200"
            >
              <motion.span
                className="relative block"
                animate={{
                  color: activeTab === "shared" ? "#ffffff" : "#6b7280",
                }}
                transition={{ duration: 0.2 }}
              >
                Интервью по моей ссылке
                {sharedInterviews.length > 0 && (
                  <span className="ml-2 text-xs opacity-80">
                    ({sharedInterviews.length})
                  </span>
                )}
              </motion.span>
            </button>
          </div>
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
          >
            {currentInterviews.length === 0 ? (
              <div className="bg-white rounded-4xl p-12 text-center">
                <div className="bg-gray-100 rounded-full w-20 h-20 mx-auto mb-4 flex items-center justify-center">
                  <Image
                    src="/images/D_BenefitIcon_48x48_291024-min.webp"
                    alt="interview-icon"
                  />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {activeTab === "my"
                    ? "У вас пока нет интервью"
                    : "Нет интервью по вашей ссылке"}
                </h3>
                <p className="text-gray-500">
                  {activeTab === "my"
                    ? "Начните своё первое собеседование!"
                    : "Поделитесь ссылкой, чтобы другие могли пройти интервью"}
                </p>
              </div>
            ) : (
              <div className="grid gap-8 md:grid-cols-2">
                {currentInterviews.map((interview) => {
                  const StatusIcon = statusConfig[interview.status].icon;
                  const totalSteps = interview.amount_of_tasks;
                  const completedSteps =
                    interview.current_step_index +
                    (interview.status === InterviewStatus.COMPLETED ? 1 : 0);
                  const progress =
                    totalSteps > 0 ? (completedSteps / totalSteps) * 100 : 0;

                  const isMyInterview =
                    currentUser && interview.user_id === currentUser.id;
                  const isSharedInterview =
                    currentUser &&
                    interview.creator_id === currentUser.id &&
                    interview.user_id !== currentUser.id;

                  const isCompleted =
                    interview.status === InterviewStatus.COMPLETED;

                  const shouldShowButton =
                    isMyInterview || (isSharedInterview && isCompleted);

                  const buttonText = isCompleted ? "Посмотреть" : "Продолжить";

                  const hasCheatingWarnings =
                    Array.isArray(interview.ban_reasons) &&
                    interview.ban_reasons.length > 0;

                  const hasResultReport = !!interview.result_url;

                  const isCheatingExpanded =
                    expandedCheatingByInterviewId[interview.id] ?? false;

                  const handleButtonClick = () => {
                    if (isMyInterview && !isCompleted) {
                      navigate(
                        `/${ERouteNames.DASHBOARD_ROUTE}/interview/${interview.id}`
                      );
                    }
                  };

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
                                {interview.job_role_description ||
                                  "Собеседование"}
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

                        <div className="grid grid-cols-2 gap-4 mb-4">
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

                        {(hasCheatingWarnings || hasResultReport) && (
                          <div className="mb-4 flex flex-col gap-3">
                            {hasCheatingWarnings && (
                              <div className="rounded-2xl border border-red-100 bg-red-50/80 p-3">
                                <p className="text-xs font-semibold text-red-700 mb-1 flex items-center gap-1.5">
                                  <XCircle className="w-3.5 h-3.5" />
                                  Анти‑чит предупреждения
                                </p>
                                <ul className="space-y-0.5 max-h-24 overflow-y-auto pr-1">
                                  {(isCheatingExpanded
                                    ? interview.ban_reasons ?? []
                                    : (interview.ban_reasons ?? []).slice(0, 3)
                                  ).map((reason: string) => (
                                    <li
                                      key={reason}
                                      className="text-[11px] text-red-800/90"
                                    >
                                      • {reason}
                                    </li>
                                  ))}
                                </ul>
                                {(interview.ban_reasons?.length ?? 0) > 3 && (
                                  <button
                                    type="button"
                                    className="mt-2 text-[11px] font-medium text-red-700 hover:text-red-800 cursor-pointer"
                                    onClick={() =>
                                      setExpandedCheatingByInterviewId(
                                        (prev) => ({
                                          ...prev,
                                          [interview.id]: !isCheatingExpanded,
                                        })
                                      )
                                    }
                                  >
                                    {isCheatingExpanded
                                      ? "Свернуть"
                                      : `Показать все (${
                                          interview.ban_reasons?.length ?? 0
                                        })`}
                                  </button>
                                )}
                              </div>
                            )}

                            {hasResultReport && (
                              <div className="rounded-2xl border border-blue-100 bg-blue-50/80 p-3 flex flex-col justify-between">
                                <div>
                                  <p className="text-xs font-semibold text-blue-800 mb-1">
                                    PDF‑отчет по интервью
                                  </p>
                                  <p className="text-[11px] text-blue-900/80">
                                    Сохранённый файл с подробным результатом и
                                    фидбэком.
                                  </p>
                                </div>
                                <div className="mt-2">
                                  <a
                                    href={interview.result_url ?? undefined}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-flex items-center justify-center rounded-xl bg-white px-3 py-1.5 text-[11px] font-medium text-blue-700 shadow-sm border border-blue-100 hover:bg-blue-50 transition-colors cursor-pointer"
                                  >
                                    Открыть PDF
                                  </a>
                                </div>
                              </div>
                            )}
                          </div>
                        )}

                        <div className="flex items-center justify-between">
                          <TagChip
                            className={`${
                              statusConfig[interview.status].color
                            } text-white border-0 flex items-center gap-2`}
                          >
                            <StatusIcon className="w-3 h-3" />
                            {statusConfig[interview.status].label}
                          </TagChip>

                          {shouldShowButton && (
                            <Button
                              variant="ghost"
                              size="sm"
                              className="bg-blue-50 text-blue-600 hover:text-blue-600 transition-all cursor-pointer"
                              onClick={handleButtonClick}
                            >
                              {buttonText}
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
};

export default InterviewHistoryPage;
