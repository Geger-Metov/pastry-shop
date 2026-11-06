import { notFound } from "next/navigation";
import { connection } from "next/server";

import type { Locale } from "@/i18n/routing";

import { getApi } from "./client";

export async function getProducts(locale: Locale, category?: string) {
  await connection();
  const { data, error } = await getApi().GET("/products", {
    params: { query: { locale, category } },
  });
  if (error) throw new Error("Failed to load products", { cause: error });
  return data;
}

export async function getProductBySlug(locale: Locale, slug: string) {
  await connection();
  const { data, error, response } = await getApi().GET("/products/{slug}", {
    params: { path: { slug }, query: { locale } },
  });
  if (response.status === 404) notFound();

  if (error) throw new Error("Failed to load product", { cause: error });
  return data;
}
