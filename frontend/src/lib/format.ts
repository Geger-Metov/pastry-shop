import type { Locale } from "@/i18n/routing";

/** "1300.50" -> "1 300,50 ₽" (формат зависит от языка). Цена приходит из API строкой. */
export function formatPrice(
  price: string,
  locale: Locale,
  currency: string,
): string {
  return new Intl.NumberFormat(locale, { style: "currency", currency }).format(
    Number(price),
  );
}
