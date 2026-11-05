import { useTranslations } from "next-intl";

import { Link } from "@/i18n/navigation";
import type { Locale } from "@/i18n/routing";
import type { Category, Product } from "@/lib/api/types";
import { cn } from "@/lib/utils";

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
  const chip = (isActive: boolean) =>
    cn(
      "rounded-full border px-4 py-1.5 text-sm hover:bg-muted",
      isActive &&
        "border-primary bg-primary text-primary-foreground hover:bg-primary/90",
    );

  return (
    <>
      <h1 className="text-3xl font-semibold">{t("title")}</h1>

      <nav aria-label={t("title")} className="mt-6 flex flex-wrap gap-2">
        <Link href="/catalog" className={chip(active === undefined)}>
          {t("all")}
        </Link>
        {categories.map((category) => (
          <Link
            key={category.id}
            href={`/catalog/${category.slug}`}
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
