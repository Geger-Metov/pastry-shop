import { connection } from "next/server";

import { getApi } from "./client";
import type { Locale } from "@/i18n/routing";

export async function getCategories(locale: Locale) {
  await connection(); // данные берём при запросе, а не при сборке
  const { data, error } = await getApi().GET("/categories", {
    params: { query: { locale } },
  });
  if (error) throw new Error("Failed to load categories", { cause: error });
  return data;
}
