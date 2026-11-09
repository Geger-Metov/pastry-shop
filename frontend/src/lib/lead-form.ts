// Имена полей совпадают с LeadIn из API: по ним ошибки сервера (`loc`)
// привязываются к нужному полю формы.
export const FIELD_NAMES = [
  "name",
  "phone",
  "email",
  "desired_date",
  "servings",
  "budget",
  "decor",
  "comment",
  "design_description",
] as const;

export type FieldName = (typeof FIELD_NAMES)[number];

export function isFieldName(value: unknown): value is FieldName {
  return FIELD_NAMES.some((name) => name === value);
}

export type FieldErrors = Partial<Record<FieldName, string>>;

// Результат действия. Ввод пользователя возвращаем в `values`,
// иначе React очистит форму после отправки.
export type LeadFormState =
  | { status: "idle" }
  | { status: "success" }
  | {
      status: "error";
      message?: string;
      fieldErrors: FieldErrors;
      values: Partial<Record<FieldName, string>>;
    };
