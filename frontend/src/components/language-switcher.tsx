"use client";

import { useLocale, useTranslations } from "next-intl";

import { buttonVariants } from "@/components/ui/button";
import { Link, usePathname } from "@/i18n/navigation";
import { routing } from "@/i18n/routing";

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
          className={buttonVariants({
            variant: locale === current ? "secondary" : "ghost",
            size: "xs",
            className: "uppercase",
          })}
        >
          {locale}
        </Link>
      ))}
    </nav>
  );
}
