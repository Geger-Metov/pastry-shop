import Image from "next/image";
import { getLocale, getTranslations } from "next-intl/server";
import { Suspense } from "react";

import { Link } from "@/i18n/navigation";
import { getProductBySlug } from "@/lib/api/products";
import type { Variant } from "@/lib/api/types";
import { formatPrice } from "@/lib/format";
import { getShopCurrency } from "@/lib/shop";

export default function ProductPage({
  params,
}: PageProps<"/[locale]/products/[slug]">) {
  return (
    <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-12">
      <Suspense
        fallback={
          <div className="bg-muted h-96 animate-pulse rounded-xl" aria-hidden />
        }
      >
        <ProductDetails params={params} />
      </Suspense>
    </main>
  );
}

async function ProductDetails({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const locale = await getLocale();
  const t = await getTranslations();
  // getProductBySlug сам вызывает notFound(), если API ответил 404
  const product = await getProductBySlug(locale, slug);

  const allergenNames: Record<string, string> = {
    gluten: t("allergens.gluten"),
    milk: t("allergens.milk"),
    eggs: t("allergens.eggs"),
    nuts: t("allergens.nuts"),
  };
  const variantLabel = (variant: Variant) =>
    [
      variant.weight_g !== null &&
        t("variant.weight", { value: variant.weight_g }),
      variant.pieces !== null && t("variant.pieces", { count: variant.pieces }),
    ]
      .filter(Boolean)
      .join(" · ");

  return (
    <article>
      <Link
        href="/catalog"
        className="text-muted-foreground text-sm hover:underline"
      >
        ← {t("product.back")}
      </Link>

      <div className="mt-6 grid gap-8 md:grid-cols-2">
        <div className="grid gap-4">
          {product.images.length === 0 ? (
            <div className="bg-muted text-muted-foreground grid aspect-4/3 place-items-center rounded-xl">
              {t("product.noImage")}
            </div>
          ) : (
            product.images.map((image, index) => (
              <div
                key={image.id}
                className="bg-muted relative aspect-4/3 overflow-hidden rounded-xl"
              >
                <Image
                  src={image.path}
                  alt={product.name}
                  fill
                  unoptimized
                  priority={index === 0}
                  sizes="(min-width: 768px) 50vw, 100vw"
                  className="object-cover"
                />
              </div>
            ))
          )}
        </div>

        <div>
          <h1 className="text-3xl font-semibold">{product.name}</h1>
          {product.locale !== locale && (
            <p className="text-muted-foreground mt-2 text-sm">
              {t("fallbackNotice")}
            </p>
          )}
          {product.description && (
            <p className="text-muted-foreground mt-4">{product.description}</p>
          )}

          <h2 className="mt-8 text-lg font-medium">{t("product.options")}</h2>
          <ul className="mt-3 divide-y rounded-xl border">
            {product.variants.map((variant) => (
              <li
                key={variant.id}
                className="flex items-center justify-between px-4 py-3"
              >
                <span>{variantLabel(variant)}</span>
                <span className="font-medium">
                  {formatPrice(variant.price, locale, getShopCurrency())}
                </span>
              </li>
            ))}
          </ul>

          {product.allergens.length > 0 && (
            <>
              <h2 className="mt-8 text-lg font-medium">
                {t("product.allergens")}
              </h2>
              <ul className="mt-3 flex flex-wrap gap-2">
                {product.allergens.map((allergen) => (
                  <li
                    key={allergen.id}
                    className="bg-muted rounded-full px-3 py-1 text-sm"
                  >
                    {allergenNames[allergen.code] ?? allergen.code}
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      </div>
    </article>
  );
}
