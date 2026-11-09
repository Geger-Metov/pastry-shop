import { type FieldErrors, isFieldName } from "./lead-form";

// Ключи из messages/*.json -> customOrder.errors.*
export type ErrorCode =
  | "required"
  | "tooShort"
  | "tooLong"
  | "invalidPhone"
  | "invalidEmail"
  | "pastDate"
  | "invalidNumber"
  | "tooSmall"
  | "tooBig"
  | "invalid";

export type Translate = (
  code: ErrorCode,
  values?: Record<string, number>,
) => string;

// Одна запись из ответа 422 (формат FastAPI)
type ValidationDetail = {
  loc: (string | number)[];
  type: string;
  input?: unknown;
  ctx?: unknown;
};

function ctxNumber(ctx: unknown, key: string): number {
  if (typeof ctx === "object" && ctx !== null && key in ctx) {
    const value = Number((ctx as Record<string, unknown>)[key]);
    if (Number.isFinite(value)) return value;
  }
  return 0;
}

// Текст сервера (`msg`) не показываем: он на русском. Берём `type` и поле.
function toMessage(
  field: string,
  detail: ValidationDetail,
  translate: Translate,
): string {
  const { type, ctx, input } = detail;
  // Пустое (или из одних пробелов) поле тоже «слишком короткое», но для
  // пользователя это «не заполнено», а не «минимум N символов».
  if (
    type === "string_too_short" &&
    typeof input === "string" &&
    input.trim() === ""
  ) {
    return translate("required");
  }
  switch (type) {
    case "missing":
      return translate("required");
    case "string_too_short":
      return translate("tooShort", { min: ctxNumber(ctx, "min_length") });
    case "string_too_long":
      return translate("tooLong", { max: ctxNumber(ctx, "max_length") });
    case "greater_than": // servings: gt=0, значения целые, поэтому минимум gt + 1
      return translate("tooSmall", { min: ctxNumber(ctx, "gt") + 1 });
    case "greater_than_equal":
      return translate("tooSmall", { min: ctxNumber(ctx, "ge") });
    case "less_than_equal":
      return translate("tooBig", { max: ctxNumber(ctx, "le") });
    case "int_parsing":
    case "int_from_float":
    case "int_type":
    case "decimal_parsing":
    case "decimal_type":
    case "decimal_max_digits":
    case "decimal_max_places":
    case "finite_number":
      return translate("invalidNumber");
  }
  if (type.startsWith("date")) return translate("invalid");
  // value_error: проверки из кода (телефон, email, дата в прошлом)
  switch (field) {
    case "phone":
      return translate("invalidPhone");
    case "email":
      return translate("invalidEmail");
    case "desired_date":
      return translate("pastDate");
    default:
      return translate("invalid");
  }
}

export function mapValidationErrors(
  details: ValidationDetail[],
  translate: Translate,
): { fieldErrors: FieldErrors; hasUnmapped: boolean } {
  const fieldErrors: FieldErrors = {};
  let hasUnmapped = false;

  for (const detail of details) {
    const field = detail.loc[1]; // loc = ["body", "<поле>"]
    if (detail.loc[0] !== "body" || !isFieldName(field)) {
      hasUnmapped = true; // ошибка не про конкретное поле
      continue;
    }
    // Показываем только первую ошибку поля
    fieldErrors[field] ??= toMessage(field, detail, translate);
  }
  return { fieldErrors, hasUnmapped };
}
