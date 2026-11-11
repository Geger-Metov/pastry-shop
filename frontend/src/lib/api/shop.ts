import { connection } from "next/server";

import { getApi } from "./client";

export async function getShopCurrency() {
  await connection();
  const { data, error } = await getApi().GET("/shop");
  if (error) throw new Error("Failed to load shop currency", { cause: error });
  return data.currency;
}
