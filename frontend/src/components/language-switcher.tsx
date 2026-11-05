"use client";

import { useLocale, useTranslations } from "next-intl";

import { Link, usePathname } from "@/i18n/navigation";
import { routing } from "@/i18n/routing";
import { cn } from "@/lib/utils";

export function LanguageSwitcher() {
  const t = useTranslations("language");
  const current = useLocale();
  const pathname = usePathname(); // путь без языка: "/catalog/cakes"

  return (
    <nav aria-label={t("label")} className="flex gap-1 text-sm">
      {routing.locales.map((locale) => (
        <Link
          key={locale}
          href={pathname}
          locale={locale}
          aria-current={locale === current ? "true" : undefined}
          className={cn(
            "hover:bg-muted rounded-md px-2 py-1 uppercase",
            locale === current && "bg-muted font-semibold",
          )}
        >
          {locale}
        </Link>
      ))}
    </nav>
  );
}
