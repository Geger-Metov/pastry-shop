import { getLocale } from "next-intl/server";
import { Suspense } from "react";

import { CatalogView } from "@/components/catalog-view";
import { SkeletonGrid } from "@/components/skeleton-grid";
import { getCategories } from "@/lib/api/categories";
import { getProducts } from "@/lib/api/products";
import { getShopCurrency } from "@/lib/api/shop";

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
  const [categories, products, currency] = await Promise.all([
    getCategories(locale),
    getProducts(locale),
    getShopCurrency(),
  ]);

  return (
    <CatalogView
      categories={categories}
      products={products}
      locale={locale}
      currency={currency}
    />
  );
}
