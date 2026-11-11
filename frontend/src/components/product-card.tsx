import Image from "next/image";
import { getTranslations } from "next-intl/server";

import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Link } from "@/i18n/navigation";
import type { Locale } from "@/i18n/routing";
import type { Product } from "@/lib/api/types";
import { formatPrice } from "@/lib/format";

export async function ProductCard({
  product,
  locale,
  currency,
}: {
  product: Product;
  locale: Locale;
  currency: string;
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
      className="group focus-visible:ring-ring/50 block rounded-xl outline-none focus-visible:ring-3"
    >
      <Card
        size="sm"
        className="h-full transition-shadow group-hover:shadow-md"
      >
        {/* -mt-(--card-spacing) "съедает" верхний отступ Card, и фото прилегает к краю */}
        <div className="bg-muted relative -mt-(--card-spacing) aspect-4/3">
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
        <CardHeader>
          <CardTitle>{product.name}</CardTitle>
          <CardDescription>
            {t("from", {
              price: formatPrice(String(lowest), locale, currency),
            })}
          </CardDescription>
        </CardHeader>
      </Card>
    </Link>
  );
}
