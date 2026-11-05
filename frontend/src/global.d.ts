import type { routing } from "@/i18n/routing";
import type messages from "../messages/ru.json";

// Типизирует next-intl: getLocale() возвращает "ru" | "en" | "fr", а t("ключ") проверяется
// по файлу messages/ru.json (опечатка в ключе - ошибка компиляции).
declare module "next-intl" {
  interface AppConfig {
    Locale: (typeof routing.locales)[number];
    Messages: typeof messages;
  }
}
