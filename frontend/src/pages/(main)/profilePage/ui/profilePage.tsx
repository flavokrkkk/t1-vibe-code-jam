import { useCurrentUser } from "@/entities/user/hooks/useCurrentUser";
import { getDisplayName } from "@/shared/lib/userHelpers";
import { Avatar, AvatarImage } from "@/shared/ui/avatar/avatar";
import { Mail, Calendar } from "lucide-react";

const ProfilePage = () => {
  const { data: currentUser } = useCurrentUser();

  if (!currentUser) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#e0f2f7] to-[#fce4ec] relativeflex items-center justify-center">
        <div className="text-gray-500">Загрузка профиля...</div>
      </div>
    );
  }

  return (
    <div className="relative h-full">
      <div className="p-2 md:p-4 max-w-7xl mx-auto">
        <div className="bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-500 h-32 md:h-48 relative rounded-2xl md:rounded-4xl">
          <div className="absolute -bottom-12 md:-bottom-16 left-1/2 transform -translate-x-1/2">
            <Avatar className="relative h-32 w-32 md:h-40 md:w-40 ring-4 ring-white shadow-xl">
              <AvatarImage
                src="/images/user.webp"
                alt={currentUser.username}
                className="object-cover rounded-2xl"
              />
            </Avatar>
          </div>
        </div>
        <div className="text-center mb-6 md:mb-10 mt-16 md:mt-20">
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900">
            {getDisplayName(currentUser.username)}
          </h1>
          <p className="text-gray-500 mt-2 flex items-center justify-center gap-2 text-sm md:text-base">
            <Calendar className="w-4 h-4" />
            Присоединился 23.10.2025
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6 mb-8 md:mb-12">
          <div className="p-4 md:p-6 text-center bg-white rounded-2xl md:rounded-4xl">
            <div className="text-3xl md:text-4xl font-bold text-blue-600">
              0
            </div>
            <p className="text-gray-600 mt-2 text-sm md:text-base">
              Завершенные интервью
            </p>
          </div>
          <div className="p-4 md:p-6 text-center bg-white rounded-2xl md:rounded-4xl">
            <div className="text-3xl md:text-4xl font-bold text-blue-600">
              0
            </div>
            <p className="text-gray-600 mt-2 text-sm md:text-base">
              Ответы на вопросы
            </p>
          </div>
          <div className="p-4 md:p-6 text-center bg-white rounded-2xl md:rounded-4xl">
            <div className="text-3xl md:text-4xl font-bold text-blue-600">
              0m 0s
            </div>
            <p className="text-gray-600 mt-2 text-sm md:text-base">
              Средняя продолжительность
            </p>
          </div>
        </div>

        <div>
          <h2 className="text-xl md:text-2xl font-semibold text-gray-900 mb-4 md:mb-6 flex items-center gap-3">
            Информация
          </h2>
          <div className="bg-white rounded-2xl md:rounded-4xl">
            <div className="p-4 md:p-6 space-y-6 md:space-y-8">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-8">
                <div>
                  <label className="text-sm font-medium text-gray-700">
                    Имя
                  </label>
                  <div className="mt-2 px-3 md:px-4 py-2 md:py-3 bg-gray-50 border border-gray-300 rounded-2xl text-gray-900 font-medium text-sm md:text-base">
                    Егор
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">
                    Фамилия
                  </label>
                  <div className="mt-2 px-3 md:px-4 py-2 md:py-3 bg-gray-50 border border-gray-300 rounded-2xl text-gray-900 font-medium text-sm md:text-base">
                    Яровицын
                  </div>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700">
                  Обо мне
                </label>
                <div className="mt-2 px-3 md:px-4 py-2 md:py-3 bg-gray-50 border border-gray-300 rounded-2xl text-gray-500 italic text-sm md:text-base">
                  Не указано
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  Почта
                </label>
                <div className="mt-2 px-3 md:px-4 py-2 md:py-3 bg-gray-50 border border-gray-300 rounded-2xl text-gray-900 font-medium text-sm md:text-base break-words">
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
