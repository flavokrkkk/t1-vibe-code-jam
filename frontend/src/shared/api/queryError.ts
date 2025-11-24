export enum ErrorMessages {
  HTTP_ERROR = "Ошибка HTTP ${status}: ${message}",
  NETWORK_ERROR = "Не удалось выполнить запрос из-за проблем с сетью",
  UNKNOWN_ERROR = "Произошла неизвестная ошибка при выполнении запроса",
  REQUEST_PREPARATION_ERROR = "Ошибка при формировании запроса",
}
