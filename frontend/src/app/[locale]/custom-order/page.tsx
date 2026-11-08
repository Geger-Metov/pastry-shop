import { useTranslations } from "next-intl";

import { CustomOrderForm } from "@/components/custom-order-form";

export default function CustomOrderPage() {
  const t = useTranslations("customOrder");

  return (
    <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-12">
      <section className="mb-10 max-w-2xl">
        <h1 className="text-4xl font-semibold tracking-tight">{t("title")}</h1>
        <p className="text-muted-foreground mt-4 text-lg">{t("subtitle")}</p>
      </section>
      <CustomOrderForm />
    </main>
  );
}
