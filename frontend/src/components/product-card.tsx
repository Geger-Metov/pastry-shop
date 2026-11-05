import Image from "next/image";
import { getTranslations } from "next-intl/server";

import { Link } from "@/i18n/navigation";
import type { Locale } from "@/i18n/routing";
import type { Product } from "@/lib/api/types";
import { formatPrice } from "@/lib/format";
import { getShopCurrency } from "@/lib/shop";

export async function ProductCard({
  product,
  locale,
}: {
  product: Product;
  locale: Locale;
}) {
  const t = await getTranslations("product");
  const image = product.images[0];
  // у товара из API всегда есть хотя бы один вариант (иначе он не попал бы в список)
  const lowest = Math.min(
    ...product.variants.map((variant) => Number(variant.price)),
  );

  return (
    <Link
      href={`/products/${product.slug}`}
      className="group bg-card text-card-foreground block overflow-hidden rounded-xl border"
    >
      <div className="bg-muted relative aspect-4/3">
        {image ? (
          <Image
            src={image.path}
            alt={product.name}
            fill
            unoptimized
            sizes="(min-width: 1024px) 320px, (min-width: 640px) 50vw, 100vw"
            className="object-cover transition-transform group-hover:scale-105"
          />
        ) : (
          <span className="text-muted-foreground absolute inset-0 grid place-items-center text-sm">
            {t("noImage")}
          </span>
        )}
      </div>
      <div className="space-y-1 p-4">
        <h3 className="font-medium">{product.name}</h3>
        <p className="text-muted-foreground text-sm">
          {t("from", {
            price: formatPrice(String(lowest), locale, getShopCurrency()),
          })}
        </p>
      </div>
    </Link>
  );
}
