import { useNavigate } from "react-router-dom";
import { ERouteNames } from "@/shared/lib/routeVariables";
import { getAccessToken } from "@/entities/token/lib/tokenService";
import { useMemo } from "react";
import { motion } from "framer-motion";
import { Image } from "@/shared/ui/image/image";
import {
  containerVariants,
  itemVariants,
  cardVariants,
  benefits,
} from "../lib/constants";
import { useCurrentUser } from "@/entities/user/hooks/useCurrentUser";
import { Button } from "@/shared/ui/button/button";

const LandingPage = () => {
  const navigate = useNavigate();
  const token = getAccessToken();
  const { data: profileData, isSuccess: isProfileSuccess } = useCurrentUser();
  const isAuthenticated = useMemo(() => {
    return !!token && isProfileSuccess && !!profileData;
  }, [token, isProfileSuccess, profileData]);

  const handleStartWork = () => {
    if (isAuthenticated) {
      navigate(`/${ERouteNames.DASHBOARD_ROUTE}`);
    } else {
      navigate(`/${ERouteNames.AUTH_ROUTE}/${ERouteNames.REGISTER_ROUTE}`);
    }
  };

  const bannerSections = [
    {
      image: "/images/PurePromo-2.webp",
      title: "Адаптивная генерация задач",
      description:
        "ИИ-интервьюер динамически создает технические задачи на основе уровня кандидата и выбранного направления, подстраивая сложность в зависимости от качества решений",
      textPosition: "right" as const,
    },
    {
      image: "/images/PurePromo-3.webp",
      title: "Браузерная IDE с безопасным выполнением",
      description:
        "Полнофункциональная IDE с синтаксической подсветкой, автодополнением и изолированным выполнением кода в Docker контейнерах для обеспечения безопасности",
      textPosition: "left" as const,
    },
  ];

  const benefitCards = [
    {
      title: "Объективная оценка",
      description:
        "Единообразная оценка кандидатов с детальными метриками и анализом качества кода",
      image: "/images/D_BenefitIcon_48x48_291024-1-min.webp",
    },
    {
      title: "Экономия времени",
      description:
        "Автоматизированный процесс собеседования без необходимости участия интервьюеров",
      image: "/images/D_BenefitIcon_48x48_291024-2-min.webp",
    },
    {
      title: "Защита от читерства",
      description:
        "Комплексная система детектирования скопированного кода, консолей разработчика и других нарушений",
      image: "/images/D_BenefitIcon_48x48_291024-3-min.webp",
    },
  ];

  return (
    <div className="flex min-h-screen w-full flex-col bg-black overflow-hidden">
      <section className="relative min-h-screen flex flex-col">
        <div className="absolute inset-0 bg-gradient-to-b from-blue-900/50 via-indigo-900/30 to-black" />

        <div className="container mx-auto px-4 sm:px-6 lg:px-28 pt-12 sm:pt-16 lg:pt-20 pb-6 sm:pb-8 relative z-10">
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="flex flex-col items-center justify-center mb-12 sm:mb-16"
          >
            <motion.div
              variants={itemVariants}
              className="flex items-center gap-3 sm:gap-4 mb-4 mr-10"
            >
              <motion.div
                className="group cursor-pointer rounded-lg transition-all duration-300"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
              >
                <Image
                  alt="logo-suspese"
                  src="/images/logo.jpg"
                  className="w-16 h-16 rounded-full"
                />
              </motion.div>
              <motion.h1
                variants={itemVariants}
                className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-white"
              >
                T1 Course
              </motion.h1>
            </motion.div>
            <motion.p
              variants={itemVariants}
              className="text-gray-300 text-sm sm:text-base md:text-lg text-center max-w-2xl"
            >
              Платформа автоматизированного технического собеседования с
              ИИ-интервьюером
            </motion.p>
          </motion.div>

          <motion.div
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-8 sm:mb-12"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {benefitCards.map((card, index) => (
              <motion.div
                key={index}
                variants={itemVariants}
                className="rounded-3xl sm:rounded-4xl bg-gradient-to-br from-blue-900/30 to-indigo-900/20 backdrop-blur-sm border border-blue-700/30 p-4 sm:p-6 lg:p-8 hover:from-blue-900/40 hover:to-indigo-900/30 hover:border-blue-600/50 transition-all"
              >
                {card.image && (
                  <div className="mb-4">
                    <Image
                      src={card.image}
                      alt={card.title}
                      className="w-12 h-12 sm:w-14 sm:h-14 object-contain"
                    />
                  </div>
                )}
                <h3 className="text-white font-semibold text-base sm:text-lg mb-2">
                  {card.title}
                </h3>
                <p className="text-gray-300 text-xs sm:text-sm leading-relaxed">
                  {card.description}
                </p>
              </motion.div>
            ))}
          </motion.div>
        </div>

        <motion.div
          className="flex-1 relative z-10"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
        >
          <div className="bg-white dark:bg-gray-900 rounded-t-[3rem] sm:rounded-t-[4rem] md:rounded-t-[5rem] min-h-[60vh] pt-14 sm:pt-16 pb-14 sm:pb-20">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8">
              <motion.div
                variants={containerVariants}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                className="text-center mb-8 sm:mb-12 lg:mb-16"
              >
                <motion.h1
                  variants={itemVariants}
                  className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl font-bold text-gray-900 dark:text-white mb-4 sm:mb-6 leading-tight px-2"
                >
                  Собеседование будущего
                </motion.h1>
                <motion.p
                  variants={itemVariants}
                  className="text-base sm:text-lg md:text-xl lg:text-2xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto mb-6 sm:mb-8 px-4"
                >
                  Автоматизированная платформа для технических собеседований с
                  ИИ-интервьюером. Объективная оценка навыков, адаптивные задачи
                  и детальная аналитика
                </motion.p>
                <motion.div
                  variants={itemVariants}
                  className="flex flex-col sm:flex-row justify-center items-center gap-3 sm:gap-4 px-4"
                >
                  <Button
                    onClick={handleStartWork}
                    className="w-full sm:w-auto rounded-4xl bg-[#3d66ff] hover:bg-[#2d56ef] text-white px-6 sm:px-8 lg:px-10 py-6 sm:py-6 lg:py-8 cursor-pointer text-base sm:text-lg font-semibold shadow-lg shadow-blue-600/30"
                  >
                    Начать собеседование
                  </Button>
                  {!isAuthenticated && (
                    <Button
                      variant="outline"
                      onClick={() => navigate(`/${ERouteNames.AUTH_ROUTE}`)}
                      className="w-full sm:w-auto rounded-4xl border-2 border-gray-300 dark:border-gray-600 px-6 sm:px-8 lg:px-10 py-6 sm:py-6 lg:py-8 cursor-pointer text-base sm:text-lg"
                    >
                      Войти
                    </Button>
                  )}
                </motion.div>
              </motion.div>

              <motion.div
                className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-12 sm:mb-16 lg:mb-20 px-4 sm:px-8 lg:px-12 xl:px-20"
                variants={containerVariants}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, amount: 0.2 }}
              >
                {benefits.slice(0, 4).map((benefit, index) => (
                  <motion.div
                    key={index}
                    variants={cardVariants}
                    whileHover="hover"
                    className="rounded-3xl sm:rounded-4xl bg-gray-50 dark:bg-gray-800/50 p-6 sm:p-8 lg:p-10 border border-gray-200 dark:border-gray-700 hover:border-[#3d66ff]/50 transition-all"
                  >
                    <p className="text-sm sm:text-base text-gray-900 dark:text-gray-100 font-medium text-center">
                      {benefit}
                    </p>
                  </motion.div>
                ))}
              </motion.div>

              <motion.div
                className="relative rounded-3xl sm:rounded-4xl mx-4 sm:mx-8 lg:mx-12 xl:mx-20 p-6 sm:p-8 md:p-10 lg:p-14 mb-12 sm:mb-16 lg:mb-20 border border-gray-200 dark:border-gray-700 overflow-hidden"
                variants={containerVariants}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                style={{
                  backgroundImage: `url(https://alfabank.servicecdn.ru/site-upload/f8/43/8854/promocard-03.png)`,
                  backgroundPosition: "center",
                  backgroundRepeat: "no-repeat",
                  backgroundSize: "cover",
                }}
              >
                <div className="relative z-10">
                  <motion.div
                    variants={itemVariants}
                    className="mb-8 sm:mb-10 lg:mb-12 text-center"
                  >
                    <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4 sm:mb-6 px-4">
                      Почему выбирают нас
                    </h2>
                    <p className="text-sm sm:text-base lg:text-lg text-gray-600 dark:text-gray-300 max-w-3xl mx-auto px-4">
                      Платформа решает критические проблемы IT-рекрутинга:
                      непоследовательность оценки, высокие затраты на интервью и
                      потерю перспективных кандидатов из-за стресса. Мы
                      предоставляем объективную, автоматизированную систему
                      оценки технических навыков.
                    </p>
                  </motion.div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
                    {benefits.map((benefit, index) => (
                      <motion.div
                        key={index}
                        variants={itemVariants}
                        className="rounded-3xl sm:rounded-4xl bg-white dark:bg-gray-900/50 p-4 sm:p-6 border border-gray-200 dark:border-gray-700 hover:border-[#3d66ff]/50 transition-all"
                      >
                        <p className="text-sm sm:text-base font-medium text-gray-900 dark:text-gray-100 text-center">
                          {benefit}
                        </p>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </motion.div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-10 lg:gap-14 px-4 sm:px-8 lg:px-12 xl:px-20 md:mb-16 mb-8">
                {bannerSections.map((banner, index) => (
                  <motion.div
                    key={index}
                    whileHover={{ y: -5 }}
                    transition={{ type: "spring", stiffness: 120 }}
                    className="flex flex-col overflow-hidden rounded-4xl shadow-2xl bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border border-gray-200/30 dark:border-gray-700/30 hover:shadow-3xl transition-all"
                  >
                    <div className="relative h-48 sm:h-56 lg:h-64 w-full overflow-hidden">
                      <Image
                        src={banner.image}
                        alt={banner.title}
                        className="object-cover w-full h-full transition-transform duration-700 hover:scale-105"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-black/10 to-transparent" />
                      <div className="absolute bottom-4 left-4 right-4">
                        <h2 className="text-xl sm:text-2xl lg:text-3xl font-bold text-white drop-shadow-md">
                          {banner.title}
                        </h2>
                      </div>
                    </div>

                    <div className="flex flex-col justify-between p-6 sm:p-8 space-y-4">
                      <p className="text-gray-700 dark:text-gray-300 text-sm sm:text-base leading-relaxed">
                        {banner.description}
                      </p>

                      <div className="flex items-center justify-between">
                        <div className="h-1 w-12 bg-gradient-to-r from-[#3d66ff] to-blue-400 rounded-full" />
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          className="text-sm font-medium cursor-pointer text-[#3d66ff] hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300"
                        >
                          Подробнее →
                        </motion.button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>

              <motion.div
                variants={containerVariants}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, amount: 0.3 }}
              >
                <motion.div
                  variants={itemVariants}
                  className="rounded-3xl sm:rounded-4xl  mx-4 sm:mx-8 lg:mx-12 xl:mx-20 p-6 sm:p-8 md:p-12 lg:p-16 text-center shadow-2xl relative overflow-hidden"
                  style={{
                    backgroundImage: `url(https://alfabank.servicecdn.ru/site-upload/01/87/21405/D_PromoCard18_1140x300_26092025.png)`,
                    backgroundPosition: "center",
                    backgroundRepeat: "no-repeat",
                    backgroundSize: "cover",
                  }}
                >
                  <div className="absolute inset-0 bg-gradient-to-br from-[#3d66ff]/90 to-blue-600/70" />
                  <div className="relative z-10">
                    <motion.h2
                      variants={itemVariants}
                      className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-3 sm:mb-4 px-4"
                    >
                      Готовы начать?
                    </motion.h2>
                    <motion.p
                      variants={itemVariants}
                      className="text-white/90 mb-6 sm:mb-8 max-w-2xl mx-auto text-sm sm:text-base lg:text-lg px-4"
                    >
                      Присоединяйтесь к компаниям, которые уже используют
                      автоматизированные технические собеседования для
                      объективной оценки кандидатов
                    </motion.p>
                    <motion.div
                      variants={itemVariants}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <Button
                        onClick={handleStartWork}
                        className="rounded-4xl cursor-pointer bg-white text-[#3d66ff] hover:bg-white/90 shadow-xl px-6 sm:px-8 lg:px-10 py-5 sm:py-6 lg:py-7 text-base sm:text-lg font-semibold"
                      >
                        Начать собеседование
                      </Button>
                    </motion.div>
                  </div>
                </motion.div>
              </motion.div>
            </div>
          </div>
        </motion.div>
      </section>

      <div className="bg-white">
        <footer className="relative bg-gradient-to-b rounded-t-[3rem] sm:rounded-t-[4rem] md:rounded-t-[5rem] from-blue-900/70 via-indigo-900 to-black pt-12 sm:pt-16 pb-8 sm:pb-12">
          <div className="container mx-auto px-4 sm:px-6 lg:px-28">
            <motion.div
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              className="rounded-3xl sm:rounded-4xl  p-6 sm:p-8 lg:p-10"
            >
              <motion.h3
                variants={itemVariants}
                className="text-xl sm:text-2xl font-bold text-white mb-6 sm:mb-8 text-center"
              >
                Команда разработки
              </motion.h3>
              <div className="grid grid-cols-1 sm:grid-cols-5 gap-6 sm:gap-8">
                {[
                  {
                    name: "Никита - ML",
                    telegram: "https://t.me/no_status_now",
                    github: "https://github.com/NikitaMeshDS/",
                    image: "/images/developers/photo_2025-06-30_17-55-01.jpg",
                  },
                  {
                    name: "Саша - ML",
                    telegram: "https://t.me/realnameowner",
                    github: "https://github.com/realalexkrylov/",
                    image: "/images/developers/photo_2025-11-12_17-54-07.jpg",
                  },
                  {
                    name: "Егор - Frontend",
                    telegram: "https://t.me/egoryaaa",
                    github: "https://github.com/flavokrkkk",
                    image: "/images/developers/IMG_3510.webp",
                  },
                  {
                    name: "Мариф - Backend",
                    telegram: "https://t.me/magoxdd",
                    github: "https://github.com/xddprog",
                    image: "/images/developers/photo_2025-03-16_12-50-57.jpg",
                  },
                  {
                    name: "Даня - UI/UX",
                    telegram: "https://t.me/BeforeAdmin",
                    github: "https://github.com/developer2",
                    image: "/images/developers/photo_2024-07-13_23-54-29.jpg",
                  },
                ].map((developer, index) => (
                  <motion.div
                    key={index}
                    variants={itemVariants}
                    className="flex flex-col items-center gap-4 p-4 transition-all"
                  >
                    {developer.image && (
                      <div className="w-24 h-24 sm:w-28 sm:h-28 rounded-full overflow-hidden border-2 border-gray-700/50">
                        <Image
                          src={developer.image}
                          alt={developer.name}
                          className="w-full h-full object-cover"
                        />
                      </div>
                    )}
                    <h4 className="text-white font-semibold text-base sm:text-base">
                      {developer.name}
                    </h4>
                    <div className="flex items-center gap-4">
                      <a
                        href={developer.telegram}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 text-gray-300 hover:text-[#3d66ff] transition-colors"
                      >
                        <svg
                          className="w-5 h-5 sm:w-6 sm:h-6"
                          fill="currentColor"
                          viewBox="0 0 24 24"
                          aria-hidden="true"
                        >
                          <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z" />
                        </svg>
                        <span className="text-sm sm:text-base">Telegram</span>
                      </a>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default LandingPage;
