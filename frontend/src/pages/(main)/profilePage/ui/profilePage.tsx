import { useCurrentUser } from "@/entities/user/hooks/useCurrentUser";
import { Avatar, AvatarFallback, AvatarImage } from "@/shared/ui/avatar/avatar";
import { Mail, Calendar } from "lucide-react";

const ProfilePage = () => {
  const { data: currentUser } = useCurrentUser();

  if (!currentUser) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Загрузка профиля...</div>
      </div>
    );
  }

  const initials = currentUser.username
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase();

  return (
    <div className="bg-gray-50">
      <div className="p-2 md:p-4 max-w-7xl mx-auto">
        <div className="bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-500 h-32 md:h-48 relative rounded-2xl md:rounded-4xl">
          <div className="absolute -bottom-12 md:-bottom-16 left-1/2 transform -translate-x-1/2">
            <Avatar className="w-24 h-24 md:w-32 md:h-32 border-4 border-white shadow-2xl">
              <AvatarImage src="" alt={currentUser.username} />
              <AvatarFallback className="bg-blue-600 text-white text-2xl md:text-3xl font-bold">
                {initials}
              </AvatarFallback>
            </Avatar>
          </div>
        </div>
        <div className="text-center mb-6 md:mb-10 mt-16 md:mt-20">
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900">
            {currentUser.username}
          </h1>
          <p className="text-gray-500 mt-2 flex items-center justify-center gap-2 text-sm md:text-base">
            <Calendar className="w-4 h-4" />
            Member since October 23, 2025
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6 mb-8 md:mb-12">
          <div className="p-4 md:p-6 text-center bg-white rounded-2xl md:rounded-4xl border border-blue-600/40">
            <div className="text-3xl md:text-4xl font-bold text-blue-600">
              0
            </div>
            <p className="text-gray-600 mt-2 text-sm md:text-base">
              Завершенные интервью
            </p>
          </div>
          <div className="p-4 md:p-6 text-center bg-white rounded-2xl md:rounded-4xl border border-blue-600/40">
            <div className="text-3xl md:text-4xl font-bold text-blue-600">
              0
            </div>
            <p className="text-gray-600 mt-2 text-sm md:text-base">
              Ответы на вопросы
            </p>
          </div>
          <div className="p-4 md:p-6 text-center bg-white rounded-2xl md:rounded-4xl border border-blue-600/40">
            <div className="text-3xl md:text-4xl font-bold text-blue-600">
              0m 0s
            </div>
            <p className="text-gray-600 mt-2 text-sm md:text-base">
              Средняя продолжительность
            </p>
          </div>
        </div>

        <div className="mb-8 md:mb-12">
          <h2 className="text-xl md:text-2xl font-semibold text-gray-900 mb-4 md:mb-6 flex items-center gap-3">
            Тарифный план
          </h2>
          <div className="bg-white rounded-2xl md:rounded-4xl border border-blue-600/40 overflow-hidden">
            <div className="p-4 md:p-6">
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-4 gap-2 md:gap-0">
                <h3 className="text-base md:text-lg font-semibold">
                  Выберите план
                </h3>
                <span className="text-xs md:text-sm text-gray-500">
                  В настоящее время на бесплатном плане
                </span>
              </div>
              <div className="bg-gradient-to-r from-blue-50 to-cyan-50 rounded-xl p-4 md:p-6 border border-blue-200">
                <div className="flex justify-between items-center">
                  <div>
                    <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 sm:gap-4">
                      <span className="text-lg md:text-xl font-bold text-blue-900">
                        Бесплатный
                      </span>
                      <span className="text-2xl md:text-3xl font-bold text-blue-600">
                        €0.00
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div>
          <h2 className="text-xl md:text-2xl font-semibold text-gray-900 mb-4 md:mb-6 flex items-center gap-3">
            Информация
          </h2>
          <div className="bg-white border border-blue-600/40 rounded-2xl md:rounded-4xl">
            <div className="p-4 md:p-6 space-y-6 md:space-y-8">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-8">
                <div>
                  <label className="text-sm font-medium text-gray-700">
                    Имя
                  </label>
                  <div className="mt-2 px-3 md:px-4 py-2 md:py-3 bg-gray-50 border border-gray-300 rounded-lg text-gray-900 font-medium text-sm md:text-base">
                    Егор
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">
                    Фамилия
                  </label>
                  <div className="mt-2 px-3 md:px-4 py-2 md:py-3 bg-gray-50 border border-gray-300 rounded-lg text-gray-900 font-medium text-sm md:text-base">
                    Яровицын
                  </div>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700">
                  Обо мне
                </label>
                <div className="mt-2 px-3 md:px-4 py-2 md:py-3 bg-gray-50 border border-gray-300 rounded-lg text-gray-500 italic text-sm md:text-base">
                  Не указано
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  Почта
                </label>
                <div className="mt-2 px-3 md:px-4 py-2 md:py-3 bg-gray-50 border border-gray-300 rounded-lg text-gray-900 font-medium text-sm md:text-base break-words">
                  {currentUser.email}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
