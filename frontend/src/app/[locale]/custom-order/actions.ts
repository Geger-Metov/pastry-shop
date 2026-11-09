"use server";

import { getApi } from "@/lib/api/client";
import type { FieldName } from "@/lib/lead-form";

export type LeadFormState =
  | { status: "idle" }
  | { status: "success" }
  | {
      status: "error";
      messages?: string;
      fieldErrors: Partial<Record<FieldName, string>>;
      values: Record<string, string>;
    };

async function createLead(
  prev: LeadFormState,
  formData: FormData,
): Promise<LeadFormState> {
  const values = Object.fromEntries(formData) as Record<string, string>;

  const body = {
    name: values.name,
    phone: values.phone,
    email: values.email || undefined,
    desired_date: values.desired_date || undefined,
    servings: values.servings ? Number(values.servings) : undefined,
    budget: values.budget || undefined,
    decor: values.decor || undefined,
    comment: values.comment || undefined,
    design_description: values.design_description || undefined,
  };
  /*
  try {
    const { data, error, response } = await getApi().POST("/leads", { body });
    switch (response.status) {
      case 201:
        return { status: "success" };
      case 422:
        return { status: "error", fieldErrors: error?.detail }
      case 500:
        return;
    }
  } catch () {}
  */
}
