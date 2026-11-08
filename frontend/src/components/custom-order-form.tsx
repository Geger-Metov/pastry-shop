"use client";

import { useTranslations } from "next-intl";
import { useId, useSyncExternalStore } from "react";

import { Button } from "@/components/ui/button";
import {
  Field,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

// Имена полей совпадают с LeadIn из API: на шаге 14 по ним
// ошибки сервера (`loc`) привяжутся к нужному полю.
export type FieldName =
  | "name"
  | "phone"
  | "email"
  | "desired_date"
  | "servings"
  | "budget"
  | "decor"
  | "comment"
  | "design_description";

const subscribeNever = () => () => {};
const getServerToday = (): string | undefined => undefined;
function getLocalToday(): string {
  const d = new Date();
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

type Props = {
  /** Уже переведённые тексты ошибок по полям (появятся на шаге 14). */
  errors?: Partial<Record<FieldName, string>>;
  pending?: boolean;
  /** Значения, чтобы не потерять ввод после ошибки (шаг 14). */
  defaultValues?: Partial<Record<FieldName, string>>;
};

type FormFieldProps = {
  name: FieldName;
  label: string;
  hint?: string;
  required?: boolean;
  optionalText: string;
  requiredText: string;
  error?: string;
  children: (a: {
    id: string;
    name: FieldName;
    "aria-invalid": boolean;
    "aria-describedby": string | undefined;
    required: boolean;
  }) => React.ReactNode;
};

// Один блок «подпись + поле + подсказка + ошибка», чтобы не повторять
// связку id / htmlFor / aria-describedby девять раз.
function FormField({
  name,
  label,
  hint,
  required = false,
  optionalText,
  requiredText,
  error,
  children,
}: FormFieldProps) {
  const id = useId();
  const hintId = `${id}-hint`;
  const errorId = `${id}-error`;
  const describedBy =
    [error ? errorId : null, hint ? hintId : null].filter(Boolean).join(" ") ||
    undefined;

  return (
    <Field data-invalid={error ? true : undefined}>
      <FieldLabel htmlFor={id}>
        {label}
        {required ? (
          <>
            <span aria-hidden="true">*</span>
            <span className="sr-only">({requiredText})</span>
          </>
        ) : (
          <span className="text-muted-foreground font-normal">
            ({optionalText})
          </span>
        )}
      </FieldLabel>
      {children({
        id,
        name,
        "aria-invalid": Boolean(error),
        "aria-describedby": describedBy,
        required,
      })}
      {hint && <FieldDescription id={hintId}>{hint}</FieldDescription>}
      {error && <FieldError id={errorId}>{error}</FieldError>}
    </Field>
  );
}

export function CustomOrderForm({
  errors = {},
  pending = false,
  defaultValues = {},
}: Props) {
  const t = useTranslations("customOrder");

  // «Сегодня» считаем после монтирования: на сервере другой часовой пояс,
  // и значение при рендере дало бы расхождение с браузером (hydration).
  const today = useSyncExternalStore(
    subscribeNever,
    getLocalToday,
    getServerToday,
  );

  const common = {
    optionalText: t("optional"),
    requiredText: t("required"),
  };

  return (
    <form
      // Шаг 13: только вёрстка. Отправку (Server Action) добавим на шаге 14.
      onSubmit={(event) => event.preventDefault()}
      noValidate
      className="max-w-xl"
    >
      <FieldGroup>
        <FormField
          {...common}
          name="name"
          label={t("fields.name.label")}
          hint={t("fields.name.hint")}
          required
          error={errors.name}
        >
          {(p) => (
            <Input
              {...p}
              type="text"
              autoComplete="name"
              minLength={2}
              maxLength={100}
              defaultValue={defaultValues.name}
            />
          )}
        </FormField>

        <FormField
          {...common}
          name="phone"
          label={t("fields.phone.label")}
          hint={t("fields.phone.hint")}
          required
          error={errors.phone}
        >
          {(p) => (
            <Input
              {...p}
              type="tel"
              autoComplete="tel"
              inputMode="tel"
              placeholder={t("fields.phone.placeholder")}
              defaultValue={defaultValues.phone}
            />
          )}
        </FormField>

        <FormField
          {...common}
          name="email"
          label={t("fields.email.label")}
          hint={t("fields.email.hint")}
          error={errors.email}
        >
          {(p) => (
            <Input
              {...p}
              type="email"
              autoComplete="email"
              placeholder={t("fields.email.placeholder")}
              defaultValue={defaultValues.email}
            />
          )}
        </FormField>

        <FormField
          {...common}
          name="desired_date"
          label={t("fields.desiredDate.label")}
          hint={t("fields.desiredDate.hint")}
          error={errors.desired_date}
        >
          {(p) => (
            <Input
              {...p}
              type="date"
              min={today}
              defaultValue={defaultValues.desired_date}
            />
          )}
        </FormField>

        <div className="grid gap-7 sm:grid-cols-2">
          <FormField
            {...common}
            name="servings"
            label={t("fields.servings.label")}
            hint={t("fields.servings.hint")}
            error={errors.servings}
          >
            {(p) => (
              <Input
                {...p}
                type="number"
                inputMode="numeric"
                min={1}
                max={1000}
                step={1}
                placeholder={t("fields.servings.placeholder")}
                defaultValue={defaultValues.servings}
              />
            )}
          </FormField>

          <FormField
            {...common}
            name="budget"
            label={t("fields.budget.label")}
            hint={t("fields.budget.hint")}
            error={errors.budget}
          >
            {(p) => (
              <Input
                {...p}
                type="number"
                inputMode="decimal"
                min={0}
                step="0.01"
                placeholder={t("fields.budget.placeholder")}
                defaultValue={defaultValues.budget}
              />
            )}
          </FormField>
        </div>

        <FormField
          {...common}
          name="decor"
          label={t("fields.decor.label")}
          hint={t("fields.decor.hint")}
          error={errors.decor}
        >
          {(p) => (
            <Input
              {...p}
              type="text"
              maxLength={200}
              defaultValue={defaultValues.decor}
            />
          )}
        </FormField>

        <FormField
          {...common}
          name="design_description"
          label={t("fields.designDescription.label")}
          hint={t("fields.designDescription.hint")}
          error={errors.design_description}
        >
          {(p) => (
            <Textarea
              {...p}
              rows={5}
              maxLength={5000}
              defaultValue={defaultValues.design_description}
            />
          )}
        </FormField>

        <FormField
          {...common}
          name="comment"
          label={t("fields.comment.label")}
          hint={t("fields.comment.hint")}
          error={errors.comment}
        >
          {(p) => (
            <Textarea
              {...p}
              rows={3}
              maxLength={2000}
              defaultValue={defaultValues.comment}
            />
          )}
        </FormField>

        <Button type="submit" size="lg" disabled={pending}>
          {pending ? t("sending") : t("submit")}
        </Button>
      </FieldGroup>
    </form>
  );
}
