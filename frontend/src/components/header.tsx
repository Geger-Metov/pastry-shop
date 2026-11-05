import { useTranslations } from "next-intl";
import { Suspense } from "react";

import { Link } from "@/i18n/navigation";

import { LanguageSwitcher } from "./language-switcher";

export function Header() {
  const t = useTranslations("nav");
  const tMeta = useTranslations("meta");

  return (
    <header className="border-b">
      <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-3">
        <div className="flex items-center gap-6">
          <Link href="/" className="text-lg font-semibold">
            {tMeta("title")}
          </Link>
          <Link href="/catalog" className="text-sm hover:underline">
            {t("catalog")}
          </Link>
        </div>
        {/* usePathname внутри зависит от адреса: с cacheComponents ему нужен Suspense */}
        <Suspense fallback={null}>
          <LanguageSwitcher />
        </Suspense>
      </div>
    </header>
  );
}
