import { expect, test } from "@playwright/test";

import en from "../messages/en.json";
import ru from "../messages/ru.json";

// Тексты берём из файлов переводов: если поменять формулировку в messages,
// тесты не сломаются. Сами переводы эти тесты не проверяют.
const t = ru.customOrder;

// Подставляет числа в {min} / {max} так же, как это делает next-intl на сервере
function withParams(message: string, params: Record<string, number>) {
  return message.replace(/\{(\w+)\}/g, (_, key: string) => String(params[key]));
}

test.describe("custom order form (ru)", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/ru/custom-order");
    await expect(page.getByRole("heading", { level: 1 })).toHaveText(t.title);
  });

  test("header link opens the page", async ({ page }) => {
    await page.goto("/ru");
    await page.getByRole("link", { name: ru.nav.customOrder }).click();

    await expect(page).toHaveURL(/\/ru\/custom-order$/);
    await expect(page.getByRole("heading", { level: 1 })).toHaveText(t.title);
  });

  test("empty form shows required errors and focuses the first one", async ({
    page,
  }) => {
    await page.getByRole("button", { name: t.submit }).click();

    // две ошибки: у имени и у телефона (остальные поля необязательные)
    await expect(page.getByText(t.errors.required)).toHaveCount(2);
    await expect(page.getByLabel(t.fields.name.label)).toHaveAttribute(
      "aria-invalid",
      "true",
    );
    await expect(page.getByLabel(t.fields.name.label)).toBeFocused();
    // мы всё ещё на форме, подтверждения нет
    await expect(page.getByText(t.successTitle)).toBeHidden();
  });

  test("keeps the typed values after a server validation error", async ({
    page,
  }) => {
    await page.getByLabel(t.fields.name.label).fill("Айдана");
    await page.getByLabel(t.fields.phone.label).fill("123"); // слишком короткий
    await page
      .getByLabel(t.fields.comment.label)
      .fill("Без орехов, пожалуйста");
    await page.getByRole("button", { name: t.submit }).click();

    await expect(
      page.getByText(withParams(t.errors.tooShort, { min: 5 })),
    ).toBeVisible();
    // ввод не потерялся
    await expect(page.getByLabel(t.fields.name.label)).toHaveValue("Айдана");
    await expect(page.getByLabel(t.fields.phone.label)).toHaveValue("123");
    await expect(page.getByLabel(t.fields.comment.label)).toHaveValue(
      "Без орехов, пожалуйста",
    );
    // и фокус на неверном поле
    await expect(page.getByLabel(t.fields.phone.label)).toBeFocused();
  });

  test("rejects a phone number with letters", async ({ page }) => {
    await page.getByLabel(t.fields.name.label).fill("Айдана");
    await page.getByLabel(t.fields.phone.label).fill("abcdefg"); // 7 символов: длина верна, формат нет
    await page.getByRole("button", { name: t.submit }).click();

    await expect(page.getByText(t.errors.invalidPhone)).toBeVisible();
  });

  // Отдельный тест: ошибки формата полей (pydantic) приходят раньше проверок
  // сценария (телефон, дата), поэтому вместе они в одном ответе не появятся.
  test("rejects an email without @", async ({ page }) => {
    await page.getByLabel(t.fields.name.label).fill("Айдана");
    await page.getByLabel(t.fields.phone.label).fill("+996 555 123 456");
    await page.getByLabel(t.fields.email.label).fill("not-an-email");
    await page.getByRole("button", { name: t.submit }).click();

    await expect(page.getByText(t.errors.invalidEmail)).toBeVisible();
  });

  test("rejects a date in the past", async ({ page }) => {
    await page.getByLabel(t.fields.name.label).fill("Айдана");
    await page.getByLabel(t.fields.phone.label).fill("+996 555 123 456");
    await page.getByLabel(t.fields.desiredDate.label).fill("2020-01-01");
    await page.getByRole("button", { name: t.submit }).click();

    await expect(page.getByText(t.errors.pastDate)).toBeVisible();
  });

  test("sends a lead and shows the confirmation", async ({ page }) => {
    await page.getByLabel(t.fields.name.label).fill(`E2E ${Date.now()}`);
    await page.getByLabel(t.fields.phone.label).fill("+996 555 123 456");
    await page.getByLabel(t.fields.servings.label).fill("10");
    await page.getByLabel(t.fields.budget.label).fill("5000");
    await page.getByLabel(t.fields.comment.label).fill("Тест из Playwright");
    await page.getByRole("button", { name: t.submit }).click();

    const confirmation = page.getByRole("status");
    await expect(confirmation).toContainText(t.successTitle);
    await expect(confirmation).toContainText(t.successText);
    // форма заменена подтверждением
    await expect(page.getByRole("button", { name: t.submit })).toBeHidden();
  });
});

test.describe("custom order form (en)", () => {
  test("texts and error messages are in English", async ({ page }) => {
    await page.goto("/en/custom-order");
    await expect(page.getByRole("heading", { level: 1 })).toHaveText(
      en.customOrder.title,
    );

    await page.getByRole("button", { name: en.customOrder.submit }).click();
    await expect(page.getByText(en.customOrder.errors.required)).toHaveCount(2);
  });
});
