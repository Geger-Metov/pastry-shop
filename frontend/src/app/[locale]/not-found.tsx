import { useTranslations } from "next-intl";

import { Link } from "@/i18n/navigation";

export default function NotFound() {
  const t = useTranslations("notFound");

  return (
    <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-24 text-center">
      <h1 className="text-3xl font-semibold">{t("title")}</h1>
      <p className="text-muted-foreground mt-4">{t("text")}</p>
      <Link href="/" className="mt-8 inline-block text-sm underline">
        {t("home")}
      </Link>
    </main>
  );
}
