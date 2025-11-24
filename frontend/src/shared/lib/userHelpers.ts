/**
 * Получает инициалы пользователя из имени
 * @param username - Имя пользователя (может содержать несколько слов)
 * @returns Инициалы (например, "Иван Петров" -> "ИП")
 */
export const getUserInitials = (username: string): string => {
  const parts = username.trim().split(" ").filter(Boolean);
  if (parts.length >= 2) {
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }
  return username.charAt(0).toUpperCase();
};

/**
 * Форматирует имя пользователя для отображения
 * @param username - Имя пользователя
 * @returns Отформатированное имя (например, "Иванов Иван Петрович" -> "Иван Иванов")
 */
export const getDisplayName = (username: string): string => {
  const parts = username.trim().split(" ").filter(Boolean);
  if (parts.length >= 3) {
    return `${parts[1]} ${parts[0]}`;
  } else if (parts.length === 2) {
    return `${parts[0]} ${parts[1]}`;
  }
  return username;
};

/**
 * Делает первую букву строки заглавной
 * @param str - Строка для форматирования
 * @returns Строка с заглавной первой буквой
 */
export const capitalizeFirst = (str: string): string => {
  if (!str) return str;
  return str.charAt(0).toUpperCase() + str.slice(1);
};
