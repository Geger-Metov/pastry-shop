import { useTranslations } from "next-intl";
import { getLocale } from "next-intl/server";
import { Suspense } from "react";

import { SkeletonGrid } from "@/components/skeleton-grid";
import { buttonVariants } from "@/components/ui/button";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
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
          className={buttonVariants({ size: "lg", className: "mt-6" })}
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
            className="group focus-visible:ring-ring/50 block h-full rounded-xl outline-none focus-visible:ring-3"
          >
            <Card className="h-full transition-shadow group-hover:shadow-md">
              <CardHeader>
                <CardTitle className="text-lg">{category.name}</CardTitle>
                {category.description && (
                  <CardDescription>{category.description}</CardDescription>
                )}
              </CardHeader>
            </Card>
          </Link>
        </li>
      ))}
    </ul>
  );
}
