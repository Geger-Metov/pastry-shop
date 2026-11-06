import { useTranslations } from "next-intl";

import { buttonVariants } from "@/components/ui/button";
import { Link } from "@/i18n/navigation";
import type { Locale } from "@/i18n/routing";
import type { Category, Product } from "@/lib/api/types";

import { ProductCard } from "./product-card";

type Props = {
  categories: Category[];
  products: Product[];
  locale: Locale;
  /** slug выбранной категории; undefined - показаны все товары */
  active?: string;
};

export function CatalogView({ categories, products, locale, active }: Props) {
  const t = useTranslations("catalog");
  // выбранная категория - заполненная кнопка, остальные - с рамкой
  const chip = (isActive: boolean) =>
    buttonVariants({ variant: isActive ? "default" : "outline", size: "sm" });

  return (
    <>
      <h1 className="text-3xl font-semibold">{t("title")}</h1>

      <nav aria-label={t("title")} className="mt-6 flex flex-wrap gap-2">
        <Link
          href="/catalog"
          aria-current={active === undefined ? "page" : undefined}
          className={chip(active === undefined)}
        >
          {t("all")}
        </Link>
        {categories.map((category) => (
          <Link
            key={category.id}
            href={`/catalog/${category.slug}`}
            aria-current={category.slug === active ? "page" : undefined}
            className={chip(category.slug === active)}
          >
            {category.name}
          </Link>
        ))}
      </nav>

      {products.length === 0 ? (
        <p className="text-muted-foreground mt-10">{t("empty")}</p>
      ) : (
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} locale={locale} />
          ))}
        </div>
      )}
    </>
  );
}
