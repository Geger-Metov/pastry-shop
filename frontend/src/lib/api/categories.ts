import { api } from "./client";
import type { Locale } from "@/i18n/routing";

export async function getCategories(locale: Locale) {
  const { data, error } = await api.GET("/categories", {
    params: { query: { locale } },
  });
  if (error) throw new Error("Failed to load categories");
  return data;
}
