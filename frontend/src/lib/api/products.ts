import { notFound } from "next/navigation";

import type { Locale } from "@/i18n/routing";

import { api } from "./client";

export async function getProducts(locale: Locale, category?: string) {
  const { data, error } = await api.GET("/products", {
    params: { query: { locale, category } },
  });
  if (error) {
    // console.error("Failed to load products:", error);
    throw new Error("Failed to load products");
  }
  return data;
}

export async function getProductBySlug(locale: Locale, slug: string) {
  const { data, error, response } = await api.GET("/products/{slug}", {
    params: { path: { slug }, query: { locale } },
  });
  if (response.status == 404) notFound();

  if (error) {
    // console.error("Failed to load product:", error);
    throw new Error("Failed to load product");
  }
  return data;
}
