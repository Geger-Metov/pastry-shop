import "server-only";

// Валюта магазина (ISO 4217). Читаем при вызове, а не при импорте файла.
export function getShopCurrency(): string {
  const currency = process.env.SHOP_CURRENCY;
  if (!currency) throw new Error("SHOP_CURRENCY is not set");
  return currency;
}
