import { useTranslations } from "next-intl";
import { getLocale } from "next-intl/server";
import { Suspense } from "react";

import { SkeletonGrid } from "@/components/skeleton-grid";
import { Link } from "@/i18n/navigation";
import { getCategories } from "@/lib/api/categories";

export default function HomePage() {
  const t = useTranslations("home");

  return (
    <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-12">
      <section className="max-w-2xl">
        <h1 className="text-4xl font-semibold tracking-tight">{t("title")}</h1>
        <p className="text-muted-foreground mt-4 text-lg">{t("subtitle")}</p>
        <Link
          href="/catalog"
          className="bg-primary text-primary-foreground hover:bg-primary/90 mt-6 inline-block rounded-md px-5 py-2.5 text-sm font-medium"
        >
          {t("browse")}
        </Link>
      </section>

      <section className="mt-16">
        <h2 className="mb-6 text-2xl font-semibold">{t("categories")}</h2>
        {/* Данные из API грузятся при запросе: пока ждём, остальная страница уже видна */}
        <Suspense fallback={<SkeletonGrid />}>
          <Categories />
        </Suspense>
      </section>
    </main>
  );
}

async function Categories() {
  const locale = await getLocale();
  const categories = await getCategories(locale);

  return (
    <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {categories.map((category) => (
        <li key={category.id}>
          <Link
            href={`/catalog/${category.slug}`}
            className="bg-card text-card-foreground hover:bg-muted block h-full rounded-xl border p-6"
          >
            <h3 className="text-lg font-medium">{category.name}</h3>
            {category.description && (
              <p className="text-muted-foreground mt-2 text-sm">
                {category.description}
              </p>
            )}
          </Link>
        </li>
      ))}
    </ul>
  );
}
