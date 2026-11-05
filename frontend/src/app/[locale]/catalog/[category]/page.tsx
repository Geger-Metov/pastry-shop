import { notFound } from "next/navigation";
import { getLocale } from "next-intl/server";
import { Suspense } from "react";

import { CatalogView } from "@/components/catalog-view";
import { SkeletonGrid } from "@/components/skeleton-grid";
import { getCategories } from "@/lib/api/categories";
import { getProducts } from "@/lib/api/products";

export default function CategoryPage({
  params,
}: PageProps<"/[locale]/catalog/[category]">) {
  return (
    <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-12">
      <Suspense fallback={<SkeletonGrid />}>
        <CategoryProducts params={params} />
      </Suspense>
    </main>
  );
}

async function CategoryProducts({
  params,
}: {
  params: Promise<{ category: string }>;
}) {
  // params - это Promise: значение известно только во время запроса
  const { category } = await params;
  const locale = await getLocale();
  const [categories, products] = await Promise.all([
    getCategories(locale),
    getProducts(locale, category),
  ]);

  // API на неизвестную категорию отвечает пустым списком, а для пользователя это 404
  if (!categories.some((item) => item.slug === category)) notFound();

  return (
    <CatalogView
      categories={categories}
      products={products}
      locale={locale}
      active={category}
    />
  );
}
