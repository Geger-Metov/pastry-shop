import { getLocale } from "next-intl/server";
import { Suspense } from "react";

import { CatalogView } from "@/components/catalog-view";
import { SkeletonGrid } from "@/components/skeleton-grid";
import { getCategories } from "@/lib/api/categories";
import { getProducts } from "@/lib/api/products";

export default function CatalogPage() {
  return (
    <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-12">
      <Suspense fallback={<SkeletonGrid />}>
        <AllProducts />
      </Suspense>
    </main>
  );
}

async function AllProducts() {
  const locale = await getLocale();
  // два независимых запроса идут параллельно
  const [categories, products] = await Promise.all([
    getCategories(locale),
    getProducts(locale),
  ]);

  return (
    <CatalogView categories={categories} products={products} locale={locale} />
  );
}
