"use server";

import { getTranslations } from "next-intl/server";

import { getApi } from "@/lib/api/client";
import { type ErrorCode, mapValidationErrors } from "@/lib/lead-errors";
import {
  FIELD_NAMES,
  type FieldName,
  type LeadFormState,
} from "@/lib/lead-form";

// Берём только свои поля: в FormData есть ещё служебные поля React ($ACTION_...)
function readValues(formData: FormData): Partial<Record<FieldName, string>> {
  const values: Partial<Record<FieldName, string>> = {};
  for (const name of FIELD_NAMES) {
    const value = formData.get(name);
    values[name] = typeof value === "string" ? value : "";
  }
  return values;
}

export async function createLead(
  _prev: LeadFormState,
  formData: FormData,
): Promise<LeadFormState> {
  const t = await getTranslations("customOrder");
  const values = readValues(formData);

  const servings = Number(values.servings);
  const body = {
    name: values.name ?? "",
    phone: values.phone ?? "",
    // пустая строка = «не заполнено»: не отправляем поле вовсе
    email: values.email || undefined,
    desired_date: values.desired_date || undefined,
    servings:
      values.servings && Number.isFinite(servings) ? servings : undefined,
    budget: values.budget || undefined, // строкой: так не теряется точность
    decor: values.decor || undefined,
    comment: values.comment || undefined,
    design_description: values.design_description || undefined,
  };

  const failed = (fieldErrors = {}): LeadFormState => ({
    status: "error",
    message: Object.keys(fieldErrors).length ? undefined : t("errors.general"),
    fieldErrors,
    values,
  });

  try {
    const { response, error } = await getApi().POST("/leads", { body });

    if (response.ok) return { status: "success" };

    if (response.status === 422 && Array.isArray(error?.detail)) {
      const { fieldErrors, hasUnmapped } = mapValidationErrors(
        error.detail,
        (code: ErrorCode, params) => t(`errors.${code}`, params),
      );
      const result = failed(fieldErrors);
      // были ошибки не по полям (или ни одной понятной): добавим общее сообщение
      if (hasUnmapped && result.status === "error") {
        result.message = t("errors.general");
      }
      return result;
    }

    return failed(); // 500, 429 и прочее
  } catch (cause) {
    // бэкенд недоступен
    console.error("createLead: request failed", cause);
    return failed();
  }
}
